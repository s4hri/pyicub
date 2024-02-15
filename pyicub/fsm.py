from transitions import Machine, State
from transitions.extensions import GraphMachine
from pyicub.utils import importFromJSONFile, exportJSONFile

class FSM:

    INIT_STATE = "init"

    def __init__(self, name="", JSON_dict=None, JSON_file=None):
        self._name_ = name
        self._states_ = []
        self._triggers_ = {}
        self._transitions_ = []
        self._machine_ = GraphMachine(model=self, states=[], initial=FSM.INIT_STATE, auto_transitions=False)
        if JSON_dict or JSON_file:
            if JSON_dict:
                self.importFromJSONDict(JSON_dict)
            else:
                self.importFromJSONFile(JSON_file)

    def addState(self, name, description='', on_enter_callback=None):
        s = State(name=name, on_enter=on_enter_callback)
        self._machine_.add_state(s)
        self._states_.append({"name": name, "description": description})
        return s

    def addTransition(self, trigger, source, dest):
        self._transitions_.append({'trigger': trigger, 'source': source, 'dest': dest})
        self._triggers_[trigger] = dest
        self._machine_.add_transition(trigger=trigger, source=source, dest=dest)

    def draw(self, filepath):
        self.get_graph().draw(filepath, prog='dot')

    def exportJSONFile(self, filepath):
        exportJSONFile(filepath, self.toJSON())

    def getCurrentState(self):
        return self.state

    def importFromJSONDict(self, data):
        name = data.get("name", "")
        states = data.get("states", [])
        transitions = data.get("transitions", [])

        for state_data in states:
            self.addState(name=state_data["name"], description=state_data["description"], on_enter_callback=self.__on_enter_action__)

        for transition_data in transitions:
            self.addTransition(trigger=transition_data["trigger"], source=transition_data["source"], dest=transition_data["dest"])

        initial_state = data.get("initial_state", FSM.INIT_STATE)
        self._machine_.set_state(initial_state)

    def importFromJSONFile(self, filepath):
        data = importFromJSONFile(filepath)
        self.importFromJSONDict(data)

    def toJSON(self):
        data = {
            "name": self._name_,
            "states": self._states_,
            "transitions": self._transitions_,
            "initial_state": self._machine_.initial,
        }
        return data

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

    def runStep(self, trigger):
        self.trigger(trigger)
        triggers = self.getCurrentTriggers()
        if not triggers:
            self._machine_.set_state(FSM.INIT_STATE)
        return triggers
        