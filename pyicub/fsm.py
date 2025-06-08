from transitions import State
from transitions.extensions import GraphMachine
from pyicub.utils import importFromJSONFile, exportJSONFile

import json
import logging

class FSM:

    INIT_STATE = "init"

    def __init__(self, name="", JSON_dict=None, JSON_file=None, session_id=0, auto_transitions=False):
        self._name_ = name
        self._states_ = []
        self._transitions_ = []
        self._triggers_ = {}
        self._ordered_triggers_ = []
        self._session_id_ = session_id
        self._session_count_ = 0
        self._states_count_ = {}
        self._root_state_ = None
        self._machine_ = GraphMachine(model=self, states=[], initial=FSM.INIT_STATE, auto_transitions=auto_transitions)
        self._logger_ = FSM.getLogger()
        self.configureLogging(logging_level=logging.INFO)

        if JSON_dict or JSON_file:
            if JSON_dict:
                self.importFromJSONDict(JSON_dict)
            else:
                self.importFromJSONFile(JSON_file)

    @property
    def name(self):
        return self._name_

    @property
    def triggers(self):
        return self._ordered_triggers_

    @staticmethod
    def getLogger():
        return logging.getLogger('FSM')
    
    def configureLogging(self, logging_level):
        self._logger_.setLevel(logging_level)
        self._logger_.addHandler(logging.StreamHandler())
        self._logger_.handlers[0].setLevel(logging_level)
        self._logger_.handlers[0].setFormatter(logging.Formatter('FSM: [%(levelname)s] %(message)s'))

        # Configure transitions logger
        transitions_logger = logging.getLogger('transitions')
        transitions_logger.setLevel(logging_level)
        transitions_logger.addHandler(logging.StreamHandler())
        transitions_logger.handlers[0].setLevel(logging.WARNING)
        transitions_logger.handlers[0].setFormatter(logging.Formatter('FSM/transitions: [%(levelname)s] %(message)s'))

    def on_exit_init(self, *args, **kwargs):
        self._session_count_ += 1

    def addState(self, name, description=None, on_enter_callback=None, on_exit_callback=None):
        s = State(name=name, on_enter=on_enter_callback, on_exit=on_exit_callback)
        self._machine_.add_state(s)
        self._states_.append({"name": name, "description": description})
        self._states_count_[name] = 0
        return s

    def addTransition(self, source=INIT_STATE, dest="", trigger="", conditions=None, unless=None, before=None, after=None, prepare=None):
        if not dest:
            dest = source
        if source == FSM.INIT_STATE:
            self._root_state_ = dest
        if not trigger:
            trigger = "{}>{}".format(source, dest)
        self._ordered_triggers_.append(trigger)
        self._transitions_.append({'trigger': trigger, 'source': source, 'dest': dest})
        self._triggers_[trigger] = {'source': source, 'dest': dest}
        self._machine_.add_transition(trigger=trigger, source=source, dest=dest, conditions=conditions, unless=unless, before=before, after=after, prepare=prepare)

    def draw(self, filepath):
        self.get_graph().draw(filepath, prog='dot')       
    
    def exportJSONFile(self, filepath):
        data = json.dumps(self.toJSON(), default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
        exportJSONFile(filepath, data)

    def getCurrentState(self):
        return self.state

    def getSessionID(self):
        return self._session_id_

    def getSessionCount(self):
        return self._session_id_

    def getState(self, name):
        return self._machine_.get_state(name)

    def getStates(self):
        return self._states_

    def getTransitions(self):
        return self._transitions_

    def getTriggers(self):
        return self._triggers_

    def getCurrentTriggers(self):
        return self.getStateTriggers(self.getCurrentState())

    def getStateTriggers(self, state_name):
        return self._machine_.get_triggers(state_name)

    def importFromJSONDict(self, data):
        print("FSM: Importing FSM from JSON dictionary")
        name = data.get("name", "")
        states = data.get("states", [])
        transitions = data.get("transitions", [])

        for state_data in states:
            self.addState(name=state_data["name"], description=state_data["description"])

        for transition_data in transitions:
            print("Adding transition: %s" % transition_data)
            self.addTransition(source=transition_data["source"], dest=transition_data["dest"], trigger=transition_data["trigger"])

        initial_state = data.get("initial_state", FSM.INIT_STATE)
        self._machine_.set_state(initial_state)

    def importFromJSONFile(self, filepath):
        data = importFromJSONFile(filepath)
        self.importFromJSONDict(data)

    def runStep(self, trigger, **kargs):
        self._logger_.info("Executing trigger: %s with args: %s" % (trigger, kargs))
        source, dest = self._triggers_.get(trigger, {}).get('source', 'unknown'), self._triggers_.get(trigger, {}).get('dest', 'unknown')
        self._logger_.info("Transitioning from <%s> to <%s>" % (source, dest))
        if kargs:
            self.trigger(trigger_name=trigger, **kargs)
        else:
            self.trigger(trigger_name=trigger)
        triggers = self.getCurrentTriggers()
        if not triggers:
            self._machine_.set_state(FSM.INIT_STATE)
        self._states_count_[self.getCurrentState()] = self._states_count_.get(self.getCurrentState(), 0) + 1
        self._logger_.debug("Current state: %s, triggers available: %s" % (self.getCurrentState(), triggers))
        self._logger_.debug("Session ID: %s, Session Count: %s" % (self.getSessionID(), self.getSessionCount()))
        self._logger_.debug("States count: %s" % self._states_count_)
        return triggers

    def setSessionID(self, session_id):
        self._session_id_ = session_id

    def getSessionID(self):
        return self._session_id_

    def getSessionCount(self):
        return self._session_count_

    def toJSON(self):
        data = {
            "name": self._name_,
            "states": self._states_,
            "transitions": self._transitions_,
            "initial_state": self._machine_.initial,
            "session_id": self._session_id_,
            "session_count": self._session_count_,
            "states_count": self._states_count_
        }
        return data


