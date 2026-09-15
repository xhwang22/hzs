"""Read a bounded experiment snapshot. Never import or execute framework/run code.

Only derived, non-secret data and file hashes are written in the paper workspace.
Normal paper builds read the frozen JSON, not these live source directories.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "OpenAgentScaler-env-evolution"
RUNS = {
    "tau2": "20260913-022502-83b860-tau2",
    "bfcl": "20260913-022504-defa84-bfcl",
    "acebench_agent": "20260914-094616-22571a-acebench_agent",
}
COUNTS = {"tau2": 139, "bfcl": 400, "acebench_agent": 25}
HASHES = {}


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    HASHES[str(path)] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    return json.loads(raw)


def evaluation(path, benchmark, expected=None):
    data = read(path)
    metrics = data["metrics"]
    groups = data["case_groups"]
    assert len(groups) == COUNTS[benchmark], (path, len(groups))
    assert len({g["case_id"] for g in groups}) == len(groups)
    scores = {}
    for group in groups:
        assert group["pass_count"] + group["fail_count"] == 3
        scores.setdefault(group["category"], []).append(group["pass_count"] / 3)
    recomputed = {k: sum(v) / len(v) for k, v in scores.items()}
    weighted = sum(sum(v) for v in scores.values()) / len(groups)
    recomputed["overall"] = (sum(recomputed.values()) / len(scores)
                             if benchmark == "acebench_agent" else weighted)
    for key, value in recomputed.items():
        assert abs(value - metrics[key]) < 1e-10, (path, key, value, metrics[key])
    for key, value in (expected or {}).items():
        assert abs(value - metrics[key]) < 1e-10, (path, key, value, metrics[key])
    values = {k: v["values"] for k, v in data["metric_stats"].items()}
    assert len(values["overall"]) == 3
    assert abs(sum(values["overall"]) / 3 - metrics["overall"]) < 1e-10
    return {"source": str(path), "metrics": metrics, "repeat_values": values,
            "tasks": len(groups), "attempts": 3 * len(groups),
            "task_groups": [{k: g[k] for k in ("case_id", "category", "pass_count", "fail_count")}
                            for g in groups]}


def collect(max_rounds, benchmarks=None):
    moment = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    bases = read(SOURCE / "report/experiment_dashboard/test_baselines.json")
    result = {"schema": "envopt.paper.results.v1", "snapshot_at": moment,
              "round_cap": max_rounds, "source_root": str(SOURCE), "runs": {}}
    for benchmark, name in RUNS.items():
        if benchmarks is not None and benchmark not in benchmarks:
            continue
        run = SOURCE / "envopt/runs" / name
        meta = read(run / "run.json")
        state = meta["evolution"]
        profile = read(run / ".service/experiment_config.json")
        assert profile["rl"]["model_dir"].endswith("Qwen3-4B-Instruct-2507")
        config = {k: profile["rl"].get(k) for k in (
            "model_dir", "learning_rate", "kl_loss_coef", "rollout_batch_size",
            "n_samples_per_prompt", "rollout_temperature", "max_policy_turns",
            "rollout_max_response_len", "rollout_max_context_len", "seed")}
        config["pods"] = state["setting"]["pods"]
        config["evolver"] = {k: profile["evolver"].get(k) for k in (
            "planner_model", "model", "reasoning_effort", "environment_budget",
            "feedback_contract", "experience_max_words")}
        config["corpus_supplied"] = bool(state.get("corpus"))
        config["eval_subset_counts"] = {k: len(v) for k, v in profile["eval"]["task_ids_by_domain"].items()}
        config["eval_repeats"] = profile["eval"]["num_repeats"]
        config["benchmark_specific_eval"] = {}
        for key in ("tau2_bench", "bfcl_v3", "acebench_agent"):
            if key in profile["eval"]:
                # A minimal reproducible interface description, not credentials/provider config.
                specific = profile["eval"][key]
                config["benchmark_specific_eval"][key] = {
                    k: specific[k] for k in ("interaction_protocol", "max_steps", "max_turns",
                        "max_tokens", "temperature", "step_language", "response_normalization") if k in specific}
        baseline = evaluation(run / ".service/baseline/results.json", benchmark, state["baseline_metrics"])
        base_ref = bases[name]
        test_base_path = Path(base_ref["source"]) / "evaluation/eval/eval_results.json"
        test_base = evaluation(test_base_path, benchmark, base_ref["metrics"])
        assert HASHES[str(test_base_path)]["sha256"] == base_ref["results_sha256"]
        test_base.update(comparable=base_ref["comparable"], note=base_ref["note"])
        test_by_job = {}
        for progress in sorted((run / ".service/test_evaluations").glob("*/progress.json")):
            for row in read(progress).get("records", []):
                if row.get("kind") == "completed_iteration" and row.get("state") == "done":
                    test_by_job[row["job"]] = row
        points = []
        for index in range(min(state["completed"], max_rounds)):
            directory = run / "rounds" / ("%03d" % index)
            outcome = read(directory / "analysis/outcome.json")
            job = read(run / ".service/jobs" / (outcome["job"] + ".json"))
            assert job["state"] == "done", (name, index, job["state"])
            audit = outcome["rl_audit"]
            assert audit["recorded_episodes"] == audit["unique_tasks"] * 8
            dev_path = run / ".service/evaluations" / outcome["job"] / "eval/eval_results.json"
            dev = evaluation(dev_path, benchmark, outcome["metrics"])
            private_iteration = run / "evolve_context/iterations" / ("%03d" % index)
            plan = read(private_iteration / "plan.json")
            selection = read(private_iteration / "generation_summary.json")
            assert selection["selected"] == audit["unique_tasks"]
            row = {"round": index + 1, "job": outcome["job"], "revision": outcome["input_revision"],
                   "completed_at": outcome["completed_at"], "iteration_seconds": outcome["iteration_seconds"],
                   "tasks": audit["unique_tasks"], "episodes": audit["recorded_episodes"],
                   "updates": len(audit["training_budget"]["tasks_per_update"]),
                   "mixed_groups": audit["groups_with_reward_variation"],
                   "audit": {"aborted_episodes": audit["aborted_episodes"],
                       "token_capture_complete": audit["token_capture"]["complete"],
                       "reward_normalization_complete": audit["reward_normalization"]["complete"],
                       "weights_changed": audit["weights_changed"],
                       "finite_training_metrics": audit["finite_training_metrics"]},
                   "reward_counts": audit["reward_counts"],
                   "planned_tasks": selection["planned"],
                   "failed_candidates": selection.get("failed_candidates", []),
                   "allocations": selection["per_environment"],
                   "actions": dict(Counter(i["action"] for i in plan["items"])),
                   "explicit_intervention_review": "review_previous" in plan,
                   "dev": dev, "test": None}
            if outcome["job"] in test_by_job:
                t = test_by_job[outcome["job"]]
                status = read(Path(t["output"]) / "status.json")
                assert status["state"] == "done" and status["checkpoint"] == job["checkpoint"]
                row["test"] = evaluation(Path(t["output"]) / "evaluation/eval/eval_results.json", benchmark, t["metrics"])
            points.append(row)
        # Use only development scores, with earliest-round tie breaking; baseline is eligible.
        eligible = [(0, baseline["metrics"]["overall"])] + [(p["round"], p["dev"]["metrics"]["overall"]) for p in points]
        selected = max(eligible, key=lambda pair: (round(pair[1], 12), -pair[0]))[0]
        result["runs"][benchmark] = {"id": name, "reported_state": "ongoing" if benchmark == "acebench_agent" else "stopped",
            "metadata_phase": state.get("phase"), "completed_seen": state["completed"],
            "protocol": state["workflow_protocol"], "profile": config,
            "baseline_dev": baseline, "baseline_test": test_base, "points": points,
            "dev_selected_round": selected, "test_rounds": [p["round"] for p in points if p["test"]]}
    result["source_files"] = HASHES
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rounds", type=int, default=9)
    parser.add_argument("--output", default="data/results_20260914.json")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    assert ROOT in output.parents
    if output.exists():
        raise SystemExit("Snapshot exists; use a new output path to preserve provenance.")
    data = collect(args.max_rounds)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(data["snapshot_at"])
    for name, run in data["runs"].items():
        print(name, len(run["points"]), "selected", run["dev_selected_round"], "tests", run["test_rounds"])
    print("Saved", output, "with", len(HASHES), "source hashes; source projects were read only.")
