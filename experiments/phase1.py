from __future__ import annotations

import json
import os
import statistics
from dataclasses import asdict

from universe_os.model import SyntheticRegimeEnvironment, catastrophic, utility
from universe_os.agents import MPCBaseline, TROSAgent

SEEDS = list(range(50))
STEPS = 120
SHIFT = 60


def run_one(agent_factory, seed):
    env = SyntheticRegimeEnvironment(seed=seed, shift_step=SHIFT)
    agent = agent_factory()
    post_util = []
    catastrophes = 0
    recovery = None

    for t in range(STEPS):
        state = env.state
        action = agent.choose(state)
        new_state = env.step(action)
        agent.observe(new_state)

        if t >= SHIFT:
            post_util.append(utility(new_state))
            catastrophes += int(catastrophic(new_state))
            if recovery is None and new_state.stability >= 0.55 and new_state.risk <= 0.55:
                recovery = t - SHIFT + 1

    if recovery is None:
        recovery = STEPS - SHIFT + 1

    return {
        "post_shift_utility": statistics.mean(post_util),
        "catastrophic_rate": catastrophes / len(post_util),
        "recovery_latency": recovery,
        "final_state": asdict(env.state),
    }


def summarize(rows):
    return {
        "mean_post_shift_utility": statistics.mean(r["post_shift_utility"] for r in rows),
        "mean_catastrophic_rate": statistics.mean(r["catastrophic_rate"] for r in rows),
        "median_recovery_latency": statistics.median(r["recovery_latency"] for r in rows),
    }


def evaluate(results):
    full = results["TROS"]
    base = results["MPC"]
    abl = results["TROS_no_echo_reflection"]

    c1 = full["mean_post_shift_utility"] >= base["mean_post_shift_utility"]
    if base["mean_catastrophic_rate"] == 0:
        c2 = full["mean_catastrophic_rate"] == 0
    else:
        c2 = full["mean_catastrophic_rate"] <= 0.80 * base["mean_catastrophic_rate"]
    c3 = full["median_recovery_latency"] <= base["median_recovery_latency"]
    c4 = (
        abl["mean_post_shift_utility"] < full["mean_post_shift_utility"]
        or abl["mean_catastrophic_rate"] > full["mean_catastrophic_rate"]
    )
    return {
        "utility_not_worse": c1,
        "catastrophe_reduction": c2,
        "recovery_not_worse": c3,
        "echo_reflection_ablation_degrades": c4,
        "decision": "SUPPORTED" if all((c1, c2, c3, c4)) else "NOT SUPPORTED",
    }


def main():
    factories = {
        "MPC": MPCBaseline,
        "TROS": lambda: TROSAgent(True, True),
        "TROS_no_echo_reflection": lambda: TROSAgent(False, False),
    }
    raw = {}
    summary = {}
    for name, factory in factories.items():
        rows = [run_one(factory, seed) for seed in SEEDS]
        raw[name] = rows
        summary[name] = summarize(rows)

    verdict = evaluate(summary)
    output = {
        "protocol": {"seeds": len(SEEDS), "steps": STEPS, "shift_step": SHIFT},
        "summary": summary,
        "verdict": verdict,
    }

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/phase1_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    lines = ["# TROS / Universe OS Phase 1 Results", ""]
    for name, s in summary.items():
        lines += [
            f"## {name}",
            f"- Mean post-shift utility: {s['mean_post_shift_utility']:.6f}",
            f"- Mean catastrophic rate: {s['mean_catastrophic_rate']:.6f}",
            f"- Median recovery latency: {s['median_recovery_latency']}",
            "",
        ]
    lines += ["## Frozen verdict", f"**{verdict['decision']}**", "", "```json", json.dumps(verdict, indent=2), "```"]
    with open("artifacts/phase1_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
