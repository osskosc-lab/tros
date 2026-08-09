from .model import ACTIONS, FIELDS, delta
from .modules import WorldModelCore, TimelineEngine, CausalityEngine, WillCore, EchoCore, EthicsLayer, SelfReflectionCore

class MPCBaseline:
    name = "MPC"

    def __init__(self):
        self.world = WorldModelCore()
        self.timeline = TimelineEngine()
        self.last_state = None
        self.last_action = None

    def choose(self, state):
        scored = []
        for action in ACTIONS:
            score, _ = self.timeline.score_action(state, action, lambda s, a: self.world.predict(s, a))
            scored.append((score, action))
        action = max(scored)[1]
        self.last_state = state
        self.last_action = action
        return action

    def observe(self, new_state):
        if self.last_state is None:
            return
        self.world.adapt(self.last_action, delta(new_state, self.last_state))

class TROSAgent:
    def __init__(self, use_echo=True, use_reflection=True):
        self.world = WorldModelCore()
        self.timeline = TimelineEngine()
        self.causality = CausalityEngine()
        self.will = WillCore()
        self.echo = EchoCore()
        self.ethics = EthicsLayer()
        self.reflection = SelfReflectionCore()
        self.use_echo = use_echo
        self.use_reflection = use_reflection
        self.last_state = None
        self.last_action = None
        self.last_prediction = None

    @property
    def name(self):
        return "TROS" if self.use_echo and self.use_reflection else "TROS_no_echo_reflection"

    def correction(self, action):
        out = self.causality.correction(action)
        if self.use_echo:
            e = self.echo.correction()
            out = {k: out[k] + e[k] for k in FIELDS}
        if self.use_reflection:
            r = self.reflection.correction()
            out = {k: out[k] + r[k] for k in FIELDS}
        return out

    def predict(self, state, action):
        return self.world.predict(state, action, self.correction(action))

    def choose(self, state):
        candidates = []
        for action in ACTIONS:
            score, _ = self.timeline.score_action(state, action, self.predict)
            first = self.predict(state, action)
            if self.ethics.allow(first):
                candidates.append((score + self.will.bonus(state, first), action))
        action = max(candidates)[1] if candidates else "conserve"
        self.last_state = state
        self.last_action = action
        self.last_prediction = self.predict(state, action)
        return action

    def observe(self, new_state):
        if self.last_state is None:
            return
        observed = delta(new_state, self.last_state)
        predicted = delta(self.last_prediction, self.last_state)
        residual = {k: observed[k] - predicted[k] for k in FIELDS}
        self.world.adapt(self.last_action, observed, lr=0.05)
        self.causality.update(self.last_action, residual)
        if self.use_echo:
            self.echo.update(residual)
        if self.use_reflection:
            self.reflection.update(residual)
