from enum import Enum, auto

class PuppyState(Enum):
    IDLE = auto()
    BLINK_LOOK = auto()
    SIT = auto()
    STAND_UP = auto()
    WALK = auto()
    WALK_LEFT = auto()
    WALK_RIGHT = auto()
    FAST_WALK = auto()
    RUN = auto()
    RUN_LEFT = auto()
    RUN_RIGHT = auto()
    SPRINT = auto()
    TURN = auto()
    SNIFF = auto()
    SCRATCH = auto()
    STRETCH = auto()
    YAWN = auto()
    LIE_DOWN = auto()
    SLEEP = auto()
    WAKE_UP = auto()
    WAKE = auto()
    PLAY = auto()
    TAIL_WAG = auto()
    HAPPY = auto()
    PETTED = auto()
    EXCITED = auto()
    CHASE_BALL = auto()
    BALL_CHASE = auto()
    CATCH_BALL = auto()
    CARRY_BALL = auto()
    DROP_BALL = auto()
    WAIT_FOR_THROW = auto()
    EAT = auto()
    DRINK = auto()
    SAD = auto()
    SLEEP_WALK = auto()
    ENTER_HOUSE = auto()
    EXIT_HOUSE = auto()
    SLEEP_INSIDE = auto()

class StateMachine:
    def __init__(self, initial_state=PuppyState.IDLE):
        self._current_state = initial_state
        self._listeners = []

    @property
    def current_state(self):
        return self._current_state

    def set_state(self, new_state: PuppyState):
        if self._current_state != new_state:
            old_state = self._current_state
            self._current_state = new_state
            for listener in self._listeners:
                listener(old_state, new_state)

    def add_listener(self, callback):
        self._listeners.append(callback)
