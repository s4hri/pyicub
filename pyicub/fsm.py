from transitions import Machine, State

class FSM:

    INIT_STATE = "init"

    def __init__(self):
        self._states_ = []
        self._triggers_ = {}
        self._transitions_ = []
        self._machine_ = Machine(model=self, states=[], initial=FSM.INIT_STATE, auto_transitions=False)

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
    
    def addState(self, name, on_enter_callback=None):
        s = State(name=name, on_enter=on_enter_callback)
        self._machine_.add_state(s)
        self._states_.append(name)
        return s

    def addTransition(self, trigger, source, dest):
        self._transitions_.append({'trigger': trigger, 'source': source, 'dest': dest})
        self._triggers_[trigger] = dest
        self._machine_.add_transition(trigger=trigger, source=source, dest=dest)

    def runSteps(self, triggers: list):
        for trigger in triggers:
            self.trigger(trigger)

    def runStep(self, trigger):
        self.trigger(trigger)
        triggers = self.getCurrentTriggers()
        if not triggers:
            self._machine_.set_state(FSM.INIT_STATE)
        return triggers