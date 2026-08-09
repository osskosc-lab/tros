from dataclasses import dataclass
import random

ACTIONS = ("conserve", "grow", "cooperate", "exploit")
FIELDS = ("stability", "resources", "trust", "risk", "innovation")

@dataclass(frozen=True)
class State:
    stability: float = 0.62
    resources: float = 0.62
    trust: float = 0.58
    risk: float = 0.30
    innovation: float = 0.45

    def clamp(self):
        return State(**{k: min(1.0, max(0.0, getattr(self, k))) for k in FIELDS})

def add_delta(s, d):
    return State(**{k: getattr(s, k) + d.get(k, 0.0) for k in FIELDS}).clamp()

def delta(a, b):
    return {k: getattr(a, k) - getattr(b, k) for k in FIELDS}

def utility(s):
    return 1.2*s.stability + 0.9*s.resources + 0.8*s.trust + 0.4*s.innovation - 1.5*s.risk

def catastrophic(s):
    return s.risk >= 0.90 or s.resources <= 0.05

class SyntheticRegimeEnvironment:
    PRE = {
        "conserve": (0.035,0.025,0.010,-0.030,-0.010),
        "grow": (-0.005,0.045,-0.010,0.035,0.055),
        "cooperate": (0.025,-0.005,0.045,-0.020,0.012),
        "exploit": (-0.045,0.080,-0.065,0.075,0.035),
    }
    POST = {
        "conserve": (0.030,0.010,0.015,-0.035,-0.010),
        "grow": (-0.050,0.010,-0.040,0.105,0.025),
        "cooperate": (0.060,-0.012,0.070,-0.065,0.018),
        "exploit": (-0.090,0.035,-0.095,0.135,0.015),
    }

    def __init__(self, seed, shift_step=60, noise_sd=0.012):
        self.rng = random.Random(seed)
        self.shift_step = shift_step
        self.noise_sd = noise_sd
        self.t = 0
        self.state = State()

    def step(self, action):
        row = (self.PRE if self.t < self.shift_step else self.POST)[action]
        d = {k: v + self.rng.gauss(0.0, self.noise_sd) for k, v in zip(FIELDS, row)}
        self.state = add_delta(self.state, d)
        self.t += 1
        return self.state
