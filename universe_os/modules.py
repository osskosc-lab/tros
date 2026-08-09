from .model import ACTIONS, FIELDS, State, SyntheticRegimeEnvironment, add_delta, delta, utility

class WorldModelCore:
    def __init__(self):
        self.effects = {
            a: {k: v for k, v in zip(FIELDS, SyntheticRegimeEnvironment.PRE[a])}
            for a in ACTIONS
        }

    def predict(self, state, action, correction=None):
        d = dict(self.effects[action])
        if correction:
            for k in FIELDS:
                d[k] += correction.get(k, 0.0)
        return add_delta(state, d)

    def adapt(self, action, observed_delta, lr=0.08):
        for k in FIELDS:
            self.effects[action][k] = (1-lr)*self.effects[action][k] + lr*observed_delta[k]

class TimelineEngine:
    def __init__(self, horizon=3, discount=0.92):
        self.horizon = horizon
        self.discount = discount

    def score_action(self, state, action, predictor):
        cur, total = state, 0.0
        for h in range(self.horizon):
            cur = predictor(cur, action)
            total += (self.discount**h) * utility(cur)
        return total, cur

class CausalityEngine:
    def __init__(self, lr=0.20):
        self.lr = lr
        self.effect = {a: {k: 0.0 for k in FIELDS} for a in ACTIONS}

    def update(self, action, residual):
        for k in FIELDS:
            self.effect[action][k] = (1-self.lr)*self.effect[action][k] + self.lr*residual[k]

    def correction(self, action):
        return dict(self.effect[action])

class WillCore:
    def bonus(self, state, predicted):
        adversity = max(0.0, state.risk-0.50) + max(0.0, 0.45-state.stability)
        recovery = (predicted.stability-state.stability) + (state.risk-predicted.risk)
        return 1.10 * adversity * recovery

class EchoCore:
    def __init__(self, decay=0.88):
        self.decay = decay
        self.echo = {k: 0.0 for k in FIELDS}

    def update(self, residual):
        for k in FIELDS:
            self.echo[k] = self.decay*self.echo[k] + (1-self.decay)*residual[k]

    def correction(self, gain=0.55):
        return {k: gain*self.echo[k] for k in FIELDS}

class EthicsLayer:
    def __init__(self, max_risk=0.83, min_resources=0.09):
        self.max_risk = max_risk
        self.min_resources = min_resources

    def allow(self, predicted):
        return predicted.risk < self.max_risk and predicted.resources > self.min_resources

class SelfReflectionCore:
    def __init__(self, decay=0.92):
        self.decay = decay
        self.bias = {k: 0.0 for k in FIELDS}

    def update(self, residual):
        for k in FIELDS:
            self.bias[k] = self.decay*self.bias[k] + (1-self.decay)*residual[k]

    def correction(self, gain=0.35):
        return {k: gain*self.bias[k] for k in FIELDS}
