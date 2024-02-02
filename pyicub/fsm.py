from transitions import Machine, State
from transitions.extensions import GraphMachine

class FSM:

    INIT_STATE = "init"

    def __init__(self):
        self._states_ = []
        self._triggers_ = {}
        self._transitions_ = []
        self._machine_ = GraphMachine(model=self, states=[], initial=FSM.INIT_STATE, auto_transitions=False)

    def draw(self, filepath):
        self.get_graph().draw(filepath, prog='dot')
   
    def getAll(self):
        return { "states": self.getStates(), "transitions": self.getTransitions() }

    def getCurrentState(self):
        return self.state

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
    
    def addState(self, name, description='', on_enter_callback=None):
        s = State(name=name, on_enter=on_enter_callback)
        self._machine_.add_state(s)
        self._states_.append({"name": name, "description": description})
        return s

    def addTransition(self, trigger, source, dest):
        self._transitions_.append({'trigger': trigger, 'source': source, 'dest': dest})
        self._triggers_[trigger] = dest
        self._machine_.add_transition(trigger=trigger, source=source, dest=dest)

    def runStep(self, trigger):
        self.trigger(trigger)
        triggers = self.getCurrentTriggers()
        if not triggers:
            self._machine_.set_state(FSM.INIT_STATE)
        return triggers
