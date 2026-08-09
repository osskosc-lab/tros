import unittest

from universe_os.model import ACTIONS, State, SyntheticRegimeEnvironment, utility
from universe_os.agents import MPCBaseline, TROSAgent


class KernelTests(unittest.TestCase):
    def test_agents_choose_valid_action(self):
        state = State()
        self.assertIn(MPCBaseline().choose(state), ACTIONS)
        self.assertIn(TROSAgent().choose(state), ACTIONS)

    def test_environment_is_bounded(self):
        env = SyntheticRegimeEnvironment(seed=1, shift_step=2)
        for _ in range(20):
            state = env.step("grow")
            for value in state.as_dict().values() if hasattr(state, "as_dict") else state.__dict__.values():
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_utility_is_finite(self):
        self.assertTrue(abs(utility(State())) < 100)


if __name__ == "__main__":
    unittest.main()
