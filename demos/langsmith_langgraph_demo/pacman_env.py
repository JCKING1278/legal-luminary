import random
from typing import List, Tuple

class PacmanValidationEnv:
    """A minimal environment where each markdown page under `_pages` is a pill.

    State:
      - current index (int)
      - verified set (set of indices)

    Actions:
      0 -> move_next (wrap around)
      1 -> move_prev (wrap around)
      2 -> verify current page

    Dynamics:
      - Each step incurs a stay-alive penalty (-0.1)
      - Verifying an unverified page gives +10 reward and marks it verified
      - Ghosts appear randomly with probability p_ghost: when a ghost appears on a step,
        the agent is forced to 'turn back' to previous cell (move_prev) and receives a penalty -5
      - The episode ends when all pages are verified or max_steps reached
    """

    def __init__(self, n_pages: int, p_ghost: float = 0.05, max_steps: int = 500):
        assert n_pages > 0
        self.n_pages = n_pages
        self.p_ghost = p_ghost
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.current = 0
        self.verified = set()
        self.steps = 0
        self.done = False
        return self._obs()

    def _obs(self) -> Tuple[int, Tuple[int, ...]]:
        # observation: current index and sorted tuple of verified indices
        return (self.current, tuple(sorted(self.verified)))

    def step(self, action: int):
        if self.done:
            raise RuntimeError("Episode is done; call reset()")

        reward = 0.0
        info = {}

        # ghost check happens first
        if random.random() < self.p_ghost:
            # ghost forces a backtrack
            self.current = (self.current - 1) % self.n_pages
            reward += -5.0
            info['ghost'] = True
            self.steps += 1
            reward += -0.1  # stay-alive penalty
            if len(self.verified) >= self.n_pages:
                self.done = True
            if self.steps >= self.max_steps:
                self.done = True
            return self._obs(), reward, self.done, info

        info['ghost'] = False

        # normal action
        if action == 0:
            self.current = (self.current + 1) % self.n_pages
        elif action == 1:
            self.current = (self.current - 1) % self.n_pages
        elif action == 2:
            # verify
            if self.current not in self.verified:
                self.verified.add(self.current)
                reward += 10.0
            else:
                # small penalty for redundant verification
                reward += -0.5
        else:
            raise ValueError("Invalid action")

        # stay-alive penalty
        reward += -0.1

        self.steps += 1

        if len(self.verified) >= self.n_pages:
            self.done = True
            info['all_verified'] = True
        else:
            info['all_verified'] = False

        if self.steps >= self.max_steps:
            self.done = True

        return self._obs(), reward, self.done, info

    def render(self):
        # simple text rendering
        line = []
        for i in range(self.n_pages):
            if i == self.current:
                c = 'P'  # pacman
            elif i in self.verified:
                c = 'v'  # verified pill
            else:
                c = '.'  # unvisited pill
            line.append(c)
        print(''.join(line), f" steps={self.steps} verified={len(self.verified)}/{self.n_pages}")
