"""Freeze completed native-ACE results, preserving the other two frozen studies.

Read-only source access. This script imports only the paper's JSON collector,
never framework code, and refuses to overwrite either results snapshot.
"""
import hashlib
import json
from pathlib import Path

from collect_results import ROOT, SOURCE, RUNS, HASHES, collect, read


def main():
    previous = ROOT / "data/results_20260914.json"
    output = ROOT / "data/results_20260915.json"
    if output.exists():
        raise SystemExit("Updated snapshot exists; preserve it and use a new version.")
    old = json.loads(previous.read_text())
    fresh = collect(10, benchmarks=("acebench_agent",))
    ace = fresh["runs"]["acebench_agent"]
    prior = old["runs"]["acebench_agent"]
    assert len(ace["points"]) == 10 and ace["test_rounds"] == list(range(1, 11))
    for name in ("baseline_dev", "baseline_test", "profile", "protocol"):
        assert ace[name] == prior[name], (name, "protocol or baseline changed")
    for before, after in zip(prior["points"], ace["points"]):
        assert {k: v for k, v in before.items() if k != "test"} == {
            k: v for k, v in after.items() if k != "test"}, before["round"]
        if before["test"] is not None:
            assert before["test"] == after["test"], before["round"]

    report = SOURCE / "report/2026-09-15-goal/ace4_stopped_test_sweep.md"
    raw = report.read_bytes()
    assert RUNS["acebench_agent"] in raw.decode() and "完整完成R1–R10" in raw.decode()
    HASHES[str(report)] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    ace["reported_state"] = "stopped"
    ace["reported_state_source"] = str(report)
    run = SOURCE / "envopt/runs" / ace["id"]
    sweep_dir = run / ".service/test_evaluations/20260915-011220"
    progress = read(sweep_dir / "progress.json")
    initial = read(sweep_dir / "progress_initial_completed.json")
    assert progress["state"] == "done"
    statuses = []
    for row in progress["records"]:
        status_path = Path(row["output"]) / "status.json"
        status = read(status_path)
        assert status["state"] == "done" and status["split"] == "test"
        assert status["checkpoint"] == row["checkpoint"]
        validation = status["validation"]
        assert (validation["tasks"], validation["repeats"], validation["attempts"]) == (25, 3, 75)
        statuses.append({"round": int(row["round"]) + 1, "job": row["job"],
                         "source": str(status_path), "checkpoint": status["checkpoint"],
                         "protocol_sha256": status["protocol_sha256"], "state": status["state"]})
    cancelled = read(run / ".service/jobs/cdc1ce5eecfc.json")
    assert not cancelled["checkpoint"] and "STOPPED" in cancelled["error"]
    ace["test_completion_audit"] = {
        "sweep_source": str(sweep_dir / "progress.json"),
        "completed_at": progress["updated_at"], "statuses": statuses,
        "initial_failed_rounds": [int(r["round"]) + 1 for r in initial["records"]
                                  if r["state"] != "done"],
        "excluded_training_attempt": {"round": 11, "job": cancelled["id"],
                                      "state": cancelled["state"], "checkpoint": None,
                                      "reason": "Operator stopped training; no complete checkpoint."}}
    fresh["runs"] = {**old["runs"], "acebench_agent": ace}
    fresh["supersedes"] = {"path": str(previous.relative_to(ROOT)),
                           "sha256": hashlib.sha256(previous.read_bytes()).hexdigest(),
                           "snapshot_at": old["snapshot_at"],
                           "scope": "Only ACE updated: R5–R10 test and R10 dev/training; other studies unchanged."}
    fresh["superseded_source_hashes"] = {k: v for k, v in old["source_files"].items()
                                         if k in HASHES and HASHES[k] != v}
    fresh["source_files"] = {**old["source_files"], **HASHES}
    with output.open("x") as stream:
        json.dump(fresh, stream, indent=2, ensure_ascii=False)
    print(fresh["snapshot_at"], "source hashes:", len(fresh["source_files"]))
    print("ACE selected:", ace["dev_selected_round"], "tests:", ace["test_rounds"])
    print("ACE total tasks:", sum(p["tasks"] for p in ace["points"]))
    print("Initial failed test rounds:", ace["test_completion_audit"]["initial_failed_rounds"])


if __name__ == "__main__":
    main()
