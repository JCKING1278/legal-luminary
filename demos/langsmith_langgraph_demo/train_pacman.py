#!/usr/bin/env python3
"""
Simple Q-learning trainer for `PacmanValidationEnv`.

This is a toy trainer to explore policies for visiting and verifying all pages while
avoiding ghosts (which impose penalties and force backtracking). The state is encoded
as (current_index, tuple(sorted(verified_indices))) converted to a string for tabular Q.
"""
import random
import argparse
import json
from collections import defaultdict
from pathlib import Path

from pacman_env import PacmanValidationEnv


def state_key(obs):
    # obs: (current, tuple(verified))
    return f"{obs[0]}|{','.join(map(str, obs[1]))}"


def choose_action(q_table, s_key, n_actions, eps=0.1):
    if random.random() < eps:
        return random.randrange(n_actions)
    qs = [q_table[(s_key, a)] for a in range(n_actions)]
    max_q = max(qs)
    # break ties randomly
    candidates = [i for i, q in enumerate(qs) if q == max_q]
    return random.choice(candidates)


def train(env, episodes=500, alpha=0.1, gamma=0.99, eps=0.1):
    q_table = defaultdict(float)
    n_actions = 3
    for ep in range(episodes):
        obs = env.reset()
        s_key = state_key(obs)
        cumulative = 0.0
        done = False
        while not done:
            a = choose_action(q_table, s_key, n_actions, eps)
            obs2, r, done, info = env.step(a)
            s2_key = state_key(obs2)
            cumulative += r
            # Q update (tabular)
            best_next = max(q_table[(s2_key, aa)] for aa in range(n_actions))
            q_table[(s_key, a)] = q_table[(s_key, a)] + alpha * (r + gamma * best_next - q_table[(s_key, a)])
            s_key = s2_key
        if (ep + 1) % 50 == 0:
            print(f"Episode {ep+1} cumulative reward {cumulative:.2f} verified {len(env.verified)}/{env.n_pages}")
    return q_table


def evaluate_policy(env, q_table, episodes=20):
    total = 0.0
    for _ in range(episodes):
        obs = env.reset()
        s_key = state_key(obs)
        done = False
        ep_reward = 0.0
        while not done:
            a = choose_action(q_table, s_key, 3, eps=0.0)
            obs, r, done, info = env.step(a)
            s_key = state_key(obs)
            ep_reward += r
        total += ep_reward
    print(f"Average evaluation reward: {total/episodes:.2f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pages", type=int, default=8)
    p.add_argument("--ghost", type=float, default=0.05)
    p.add_argument("--episodes", type=int, default=500)
    args = p.parse_args()

    env = PacmanValidationEnv(n_pages=args.pages, p_ghost=args.ghost)
    q = train(env, episodes=args.episodes)
    evaluate_policy(env, q)
    out = Path(__file__).parent / "q_table.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in q.items()}, f)
    print("Saved Q-table to", out)


if __name__ == "__main__":
    main()
