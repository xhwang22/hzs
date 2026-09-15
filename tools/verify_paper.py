"""Check frozen data/derived outputs without opening live experimental directories."""
import json
import hashlib
import math
import csv
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]


def main():
    snapshot = json.loads((ROOT / "data/results_20260915.json").read_text())
    summary = json.loads((ROOT / "data/summary_20260915.json").read_text())
    layout = json.loads((ROOT / "build/evolution_layout.json").read_text())
    appworld = json.loads((ROOT / "data/appworld_plot_summary.json").read_text())
    app_path = ROOT / appworld["source"]
    assert hashlib.sha256(app_path.read_bytes()).hexdigest() == appworld["source_sha256"]
    with app_path.open(newline="") as stream:
        app_rows = list(csv.DictReader(stream))
    assert len(app_rows) == 10 and [int(r["round"]) for r in app_rows] == list(range(10))
    for raw, parsed in zip(app_rows, appworld["records"]):
        assert raw["checkpoint"] == parsed["checkpoint"]
        for field in ("train_tgc", "train_sgc", "test_normal_tgc", "test_normal_sgc"):
            value = float(raw[field]) if raw[field] else None
            assert value == parsed[field]
            assert value is None or 0 <= value <= 1
    assert appworld["records"][-1]["test_normal_tgc"] is None
    assert appworld["records"][-1]["test_normal_sgc"] is None
    assert appworld["plotted_rounds"] == list(range(9))
    assert appworld["metadata"]["excluded_plot_rounds"] == [9]
    displayed_appworld = [r for r in appworld["records"] if r["round"] in appworld["plotted_rounds"]]
    assert appworld["selected_round"] == max(displayed_appworld, key=lambda r: (
        round(r["train_tgc"], 12), -r["round"]))["round"] == 7
    assert "appworld" not in snapshot["runs"] and "appworld" not in summary["runs"]
    assert appworld["metadata"]["source_kind"] == "user_supplied_csv"
    assert not appworld["metadata"]["local_per_task_audit_available"]
    prior_path = ROOT / snapshot["supersedes"]["path"]
    assert hashlib.sha256(prior_path.read_bytes()).hexdigest() == snapshot["supersedes"]["sha256"]
    prior = json.loads(prior_path.read_text())
    for key in ("tau2", "bfcl"):
        assert prior["runs"][key] == snapshot["runs"][key], (key, "unrelated study changed")
    expected = {"tau2": (5, 846, 6768, 2), "bfcl": (9, 809, 6472, 33),
                "acebench_agent": (3, 626, 5008, 0)}
    for key, run in snapshot["runs"].items():
        last_round = 10 if key == "acebench_agent" else 9
        assert [p["round"] for p in run["points"]] == list(range(1, last_round + 1))
        selected, tasks, episodes, aborts = expected[key]
        eligible = [(0, run["baseline_dev"]["metrics"]["overall"])] + [
            (p["round"], p["dev"]["metrics"]["overall"]) for p in run["points"]]
        assert max(eligible, key=lambda p: (round(p[1], 12), -p[0]))[0] == selected
        s = summary["runs"][key]
        assert s["last_round"] == last_round
        assert (s["selected_round"], s["total_tasks"], s["total_episodes"], s["aborted_episodes"]) == expected[key]
        assert sum(p["tasks"] for p in run["points"]) == tasks
        assert sum(p["episodes"] for p in run["points"]) == episodes
        dev_ids = {g["case_id"] for g in run["baseline_dev"]["task_groups"]}
        test_ids = {g["case_id"] for g in run["baseline_test"]["task_groups"]}
        assert not (dev_ids & test_ids), (key, "split overlap")
        for point in run["points"]:
            assert {g["case_id"] for g in point["dev"]["task_groups"]} == dev_ids
            if point["test"]:
                assert {g["case_id"] for g in point["test"]["task_groups"]} == test_ids
            assert point["tasks"] * 8 == point["episodes"]
        assert abs(run["points"][selected-1]["test"]["metrics"]["overall"] * 100 - s["selected_test"]) < 1e-10
    assert summary["runs"]["tau2"]["delta_pp"] is None
    assert not snapshot["runs"]["tau2"]["baseline_test"]["comparable"]
    ace = snapshot["runs"]["acebench_agent"]
    assert ace["test_rounds"] == list(range(1, 11))
    assert ace["reported_state"] == "stopped"
    assert ace["test_completion_audit"]["initial_failed_rounds"] == [6, 8]
    assert ace["test_completion_audit"]["excluded_training_attempt"]["round"] == 11
    expected_test = [49.44444444444444, 50, 56.11111111111111,
                     52.77777777777777, 54.44444444444444, 51.11111111111111]
    for point, score in zip(ace["points"][4:], expected_test):
        assert abs(point["test"]["metrics"]["overall"] * 100 - score) < 1e-10
    for before, after in zip(prior["runs"]["acebench_agent"]["points"], ace["points"]):
        assert {k: v for k, v in before.items() if k != "test"} == {
            k: v for k, v in after.items() if k != "test"}
        if before["test"] is not None:
            assert before["test"] == after["test"]
    assert abs(summary["runs"]["acebench_agent"]["last_test"] - expected_test[-1]) < 1e-10
    assert summary["runs"]["acebench_agent"]["paired_task_bootstrap_ci95_pp"][0] < 0
    for name in ("overview", "evolution", "subsets"):
        with fitz.open(ROOT / "figures" / (name + ".pdf")) as pdf:
            assert len(pdf) == 1 and not pdf[0].get_images(), (name, "non-vector figure")
            if name == "evolution":
                raw_text = pdf[0].get_text()
                figure_text = " ".join(raw_text.split())
                labels = raw_text.splitlines()
                assert "Tasks" not in labels, "The task-count panel was removed."
                assert "Success" not in figure_text and "score (%)" not in figure_text
                assert "Test through" not in figure_text and "unmeasured" not in figure_text
                assert "†" not in figure_text
                assert labels.count("Evolution round") == 4
                assert len({tuple(p["limits"]) for p in layout["panels"].values()}) == 4
                assert abs(pdf[0].rect.height - 3.7 * 72) < .1
                assert "AppWorld" in figure_text and "TGC" in figure_text
                assert "Train Δ +6.17" in figure_text and "Test Δ +3.17" in figure_text
                assert "test-normal" not in figure_text.lower()
                assert layout["panels"]["appworld"]["test_rounds"] == list(range(9))
                assert layout["panels"]["appworld"]["split_labels"] == ["Train", "Test"]
                assert layout["panels"]["appworld"]["last_round"] == 8
                for key, last in (("tau2", 9), ("bfcl", 9), ("acebench_agent", 10), ("appworld", 8)):
                    panel = layout["panels"][key]
                    assert panel["last_round"] == last and max(panel["x_ticks"]) == last
                    assert all(0 <= tick <= last for tick in panel["x_ticks"])
                    assert abs(panel["x_limits"][1] - last * 1.04) < 1e-10
                    assert panel["header_alignment"] == "center"
                    assert abs(panel["header_center_offset_pt"]) < .5
                    assert panel["delta_color"] == "#2F8B63"
                for split, mapped in (("train", "dev"), ("test_normal", "test")):
                    field = f"{split}_tgc"
                    delta = 100 * (appworld["records"][7][field] - appworld["records"][0][field])
                    assert abs(layout["panels"]["appworld"]["deltas"][mapped]["delta_pp"] - delta) < 1e-10
                for key, run in snapshot["runs"].items():
                    selected = run["dev_selected_round"]
                    panel = layout["panels"][key]
                    assert panel["selected_round"] == selected
                    assert panel["max_marker_size_pt"] <= 3, "No large highlight rings."
                    for tick in panel["ticks"]:
                        assert f"{tick:g}" in labels, (key, tick, "missing y tick")
                    all_values = []
                    for split, label in (("dev", "Val"), ("test", "Test")):
                        score = run["points"][selected - 1][split]["metrics"]["overall"]
                        baseline = run["baseline_" + split]["metrics"]["overall"]
                        delta = 100 * (score - baseline)
                        assert f"{label} Δ {delta:+.2f}" in figure_text, (key, split, "delta label")
                        assert abs(delta - panel["deltas"][split]["delta_pp"]) < 1e-10
                        all_values.extend([100 * baseline] + [100 * p[split]["metrics"]["overall"]
                                          for p in run["points"] if p[split]])
                    padding = max(2, (max(all_values) - min(all_values)) * .18)
                    assert panel["limits"] == [max(0, math.floor(min(all_values) - padding)),
                                                min(100, math.ceil(max(all_values) + padding))]
                spans = [s for b in pdf[0].get_text("dict")["blocks"]
                         for line in b.get("lines", []) for s in line["spans"] if s["text"].strip()]
                delta_spans = [s for s in spans if "Δ" in s["text"]]
                assert len(delta_spans) == 8 and all(s["color"] == int("2F8B63", 16) for s in delta_spans)
                for i, span in enumerate(spans):
                    box = fitz.Rect(span["bbox"])
                    assert pdf[0].rect.contains(box), ("figure text overflow", span["text"])
                    for other in spans[i + 1:]:
                        overlap = box & fitz.Rect(other["bbox"])
                        assert overlap.is_empty or overlap.width <= .5 or overlap.height <= .5, (
                            "figure text overlap", span["text"], other["text"])
                pdf[0].get_pixmap(matrix=fitz.Matrix(2, 2)).save(ROOT / "build/evolution_print_scale.png")
                pdf[0].get_pixmap(matrix=fitz.Matrix(2, 2), colorspace=fitz.csGRAY).save(
                    ROOT / "build/evolution_grayscale.png")
    log = (ROOT / "build/main.log").read_text(errors="replace")
    assert "Overfull" not in log
    assert "undefined" not in log.lower()
    with fitz.open(ROOT / "build/main.pdf") as pdf:
        texts = [p.get_text() for p in pdf]
        combined = "\n".join(texts)
        for marker in ("42.08", "39.33", "52.22", "51.11", "56.11", "16.67", "11.11", "ACEBench", "AppWorld", "TGC"):
            assert marker in combined, marker
        assert "Figure 4:" not in combined and "Supplementary AppWorld Records" not in combined
        assert "test-normal" not in combined.lower()
        assert "appworld_metrics" not in (ROOT / "sections/appendix.tex").read_text()
        for stale in ("through R4 only", "first four completed checkpoints", "ACE was ongoing",
                      "ongoing, small-test-set study", "circled test scores", "on a common scale"):
            assert stale not in combined
        report = {"snapshot_at": snapshot["snapshot_at"], "data_checks": "passed",
                  "source_hash_records": len(snapshot["source_files"]),
                  "source_projects_opened_by_this_check": False, "pdf_pages": len(pdf),
                  "appworld_source_sha256": appworld["source_sha256"],
                  "appworld_selection_round": appworld["selected_round"],
                  "method_figure_pages": [i+1 for i,t in enumerate(texts) if "Figure 1:" in t],
                  "results_table_pages": [i+1 for i,t in enumerate(texts) if "Table 1:" in t],
                  "evolution_figure_pages": [i+1 for i,t in enumerate(texts) if "Figure 2:" in t]}
    (ROOT / "build/paper_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
