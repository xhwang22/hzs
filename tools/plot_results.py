"""Publication plots/tables from a frozen, independently recounted results snapshot."""
from pathlib import Path
import json
import os
import csv
import hashlib

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea
from matplotlib.ticker import MaxNLocator
import numpy as np

DATA = json.loads((ROOT / "data/results_20260915.json").read_text())
APPWORLD_CSV = ROOT / "data/appworld_user_20260915.csv"
APPWORLD_META = json.loads((ROOT / "data/appworld_user_20260915.meta.json").read_text())
with APPWORLD_CSV.open(newline="") as stream:
    APPWORLD_ROWS = [{"checkpoint": row["checkpoint"], "round": int(row["round"]),
                     **{k: float(row[k]) if row[k] else None for k in
                        ("train_tgc", "train_sgc", "test_normal_tgc", "test_normal_sgc")}}
                    for row in csv.DictReader(stream)]
APPWORLD_PLOT_ROWS = [row for row in APPWORLD_ROWS if row["round"] <= APPWORLD_META["plot_last_round"]]
APPWORLD_SELECTED = max(APPWORLD_PLOT_ROWS, key=lambda row: (round(row["train_tgc"], 12), -row["round"]))["round"]
ORDER = ["tau2", "bfcl", "acebench_agent"]
MAX_ROUND = max(run["points"][-1]["round"] for run in DATA["runs"].values())
ROUND_TICKS = list(range(0, MAX_ROUND + 1, 2))
NAMES = {"tau2": r"$\tau^2$-Bench", "bfcl": "BFCL multi-turn", "acebench_agent": "ACEBench-Agent\n(native FC)"}
COLORS = {"dev": "#287E72", "test": "#4E70A0", "ink": "#263D42", "muted": "#84928F", "warm": "#B4774B"}
TREND_COLORS = {"dev": "#7962AA", "test": "#BB803D"}
DELTA_COLOR = "#2F8B63"
plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 8,
    "axes.labelsize": 8, "axes.titlesize": 9, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .55,
    "axes.edgecolor": "#AEBAB7", "text.color": COLORS["ink"], "axes.labelcolor": COLORS["ink"],
    "xtick.color": "#5D6F70", "ytick.color": "#5D6F70", "pdf.fonttype": 42,
    "svg.fonttype": "none", "savefig.facecolor": "white"})


def export(fig, name):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(ROOT / "figures" / (name + "." + ext), dpi=240)
    plt.close(fig)


def paired_interval(run):
    """Resample tasks within fixed subsets, retaining all three repeats per task."""
    if not run["baseline_test"]["comparable"]:
        return None
    selected = run["dev_selected_round"]
    chosen = run["baseline_test"] if selected == 0 else run["points"][selected-1]["test"]
    if chosen is None:
        return None
    base = {g["case_id"]: g for g in run["baseline_test"]["task_groups"]}
    target = {g["case_id"]: g for g in chosen["task_groups"]}
    assert set(base) == set(target)
    strata = sorted({g["category"] for g in base.values()})
    rng = np.random.default_rng(20260914)
    draws = np.zeros(10000)
    total = len(base)
    for category in strata:
        ids = sorted(k for k, g in base.items() if g["category"] == category)
        delta = np.array([(target[k]["pass_count"] - base[k]["pass_count"]) / 3 for k in ids])
        weight = (1/len(strata) if len(strata) == 2 else len(ids)/total)
        draws += weight * delta[rng.integers(0, len(ids), size=(10000, len(ids)))].mean(axis=1)
    return (100 * np.quantile(draws, [.025, .975])).tolist()


def selected_delta(run, split):
    """Each split's stored-score difference at the validation-selected checkpoint."""
    selected = run["dev_selected_round"]
    record = (run["baseline_" + split] if selected == 0
              else run["points"][selected - 1][split])
    if record is None:
        return None
    score = 100 * record["metrics"]["overall"]
    delta = score - 100 * run["baseline_" + split]["metrics"]["overall"]
    return selected, score, delta


def adaptive_scale(values):
    """Dashboard-inspired padding with rounded bounds and readable ticks.

    The entire Val/Test history and both baselines determine the range;
    bounds are never chosen from a preferred checkpoint or a selected window.
    """
    low, high = min(values), max(values)
    padding = max(2, (high - low) * .18)
    limits = (max(0, np.floor(low - padding)), min(100, np.ceil(high + padding)))
    step = 5 if limits[1] - limits[0] <= 25 else 10
    ticks = np.arange(np.ceil(limits[0] / step) * step, limits[1] + .01, step)
    return limits, ticks


def appworld_plot_run(metric):
    """Adapter for drawing only; 'dev' below maps to the supplied train split.

    This does not insert AppWorld into the audited runs or imply that its model,
    repeats, task membership, or feedback protocol have been verified locally.
    """
    def record(row, split):
        value = row[f"{split}_{metric}"]
        return None if value is None else {"metrics": {"overall": value}}
    return {"baseline_dev": record(APPWORLD_ROWS[0], "train"),
            "baseline_test": record(APPWORLD_ROWS[0], "test_normal"),
            "dev_selected_round": APPWORLD_SELECTED,
            "points": [{"round": row["round"], "dev": record(row, "train"),
                        "test": record(row, "test_normal")} for row in APPWORLD_PLOT_ROWS[1:]]}


def draw_trend(ax, run, title, split_labels=("Val", "Test")):
    points = run["points"]
    last_round = points[-1]["round"]
    x_padding = last_round * .04
    locator = MaxNLocator(nbins=4 if last_round < 10 else 5, integer=True)
    x_ticks = [int(t) for t in locator.tick_values(0, last_round) if 0 <= t <= last_round]
    if last_round not in x_ticks:
        x_ticks.append(last_round)
    dev_x = [0] + [p["round"] for p in points]
    dev_y = [100*run["baseline_dev"]["metrics"]["overall"]] + [100*p["dev"]["metrics"]["overall"] for p in points]
    ax.plot(dev_x, dev_y, color=TREND_COLORS["dev"], lw=1.5, marker="o", ms=2.65,
            markeredgewidth=.4, solid_capstyle="round", zorder=4)
    tests = [(p["round"], 100*p["test"]["metrics"]["overall"] if p["test"] else np.nan)
             for p in points]
    tests.insert(0, (0, 100*run["baseline_test"]["metrics"]["overall"]))
    ax.plot([p[0] for p in tests], [p[1] for p in tests], color=TREND_COLORS["test"],
            lw=1.3, ls=(0, (3.5, 2)), marker="s", ms=2.4,
            markeredgewidth=.4, zorder=3)
    for split in ("dev", "test"):
        ax.axhline(100 * run["baseline_" + split]["metrics"]["overall"],
                   color=TREND_COLORS[split], lw=.65, ls=(0, (1, 3)), alpha=.45, zorder=1)
    limits, ticks = adaptive_scale(dev_y + [v for _, v in tests if np.isfinite(v)])
    selected = run["dev_selected_round"]
    ax.axvline(selected, color="#A5AAB4", lw=.65, ls=(0, (2, 3)), alpha=.65, zorder=1)
    ax.text(selected, .98, f"R{selected}", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=6.5, color="#878B96")
    ax.set(xlim=(-x_padding, last_round + x_padding), ylim=limits, yticks=ticks, xticks=x_ticks)
    ax.set_xlabel("Evolution round", labelpad=4, fontsize=7.5)
    ax.tick_params(length=2, width=.5, pad=3, labelleft=True)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#ECECF0", lw=.5)
    ax.set_title(title, pad=24, fontsize=8.8, fontweight="bold")
    panel = {"limits": list(limits), "ticks": ticks.tolist(), "selected_round": selected,
             "last_round": last_round, "x_limits": list(ax.get_xlim()), "x_ticks": x_ticks,
             "header_alignment": "center", "delta_color": DELTA_COLOR,
             "split_labels": list(split_labels),
             "test_rounds": [r for r, v in tests if np.isfinite(v)],
             "deltas": {}, "max_marker_size_pt": max(
                 line.get_markersize() for line in ax.lines if line.get_marker() in ("o", "s"))}
    readouts = []
    for split, label in (("dev", split_labels[0]), ("test", split_labels[1])):
        callout = selected_delta(run, split)
        if callout is None:
            continue
        _, score, delta = callout
        label_box = TextArea(label, textprops={"fontsize": 7.1, "fontweight": "bold",
                                              "color": TREND_COLORS[split]})
        delta_box = TextArea(f"Δ {delta:+.2f}", textprops={"fontsize": 7.1, "fontweight": "bold",
                                                         "color": DELTA_COLOR})
        readouts.append(HPacker(children=[label_box, delta_box], align="baseline", pad=0, sep=3))
        panel["deltas"][split] = {"score": score, "delta_pp": delta}
    header = AnnotationBbox(HPacker(children=readouts, align="baseline", pad=0, sep=13),
                            (.5, 1.10), xycoords=ax.transAxes, box_alignment=(.5, 0),
                            frameon=False, pad=0, annotation_clip=False)
    ax.add_artist(header)
    ax._envopt_header = header
    return panel


def overview():
    # Four panels in two compact rows preserve readable labels at paper width.
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.7))
    fig.subplots_adjust(left=.065, right=.985, bottom=.12, top=.85, hspace=.90, wspace=.25)
    titles = {"tau2": r"$\tau^2$-Bench", "bfcl": "BFCL multi-turn",
              "acebench_agent": "ACEBench (native FC)", "appworld": "AppWorld · TGC"}
    layout = {"selection": "validation-selected for local runs; train-TGC-selected for supplied AppWorld data",
              "scale": "independent x/y ranges over displayed histories with 18% or 2 pp y-padding",
              "figure_size_inches": [5.5, 3.7], "panels": {}}
    for ax, key in zip(axes.flat, ORDER + ["appworld"]):
        run = appworld_plot_run("tgc") if key == "appworld" else DATA["runs"][key]
        labels = ("Train", "Test") if key == "appworld" else ("Val", "Test")
        layout["panels"][key] = draw_trend(ax, run, titles[key], labels)
    layout["panels"]["appworld"].update(source_kind=APPWORLD_META["source_kind"], metric="tgc")
    fig.canvas.draw()
    for ax, panel in zip(axes.flat, layout["panels"].values()):
        bounds = ax._envopt_header.get_window_extent(fig.canvas.get_renderer())
        center = ax.transAxes.transform((.5, 0))[0]
        panel["header_center_offset_pt"] = ((bounds.x0 + bounds.x1) / 2 - center) * 72 / fig.dpi
    (ROOT / "build/evolution_layout.json").write_text(json.dumps(layout, indent=2))
    summary = {"source": str(APPWORLD_CSV.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(APPWORLD_CSV.read_bytes()).hexdigest(),
               "metadata": APPWORLD_META, "selected_round": APPWORLD_SELECTED,
               "records": APPWORLD_ROWS, "plotted_rounds": [row["round"] for row in APPWORLD_PLOT_ROWS],
               "panels": {"tgc": layout["panels"]["appworld"]}}
    (ROOT / "data/appworld_plot_summary.json").write_text(json.dumps(summary, indent=2))
    export(fig, "evolution")


def subset_plot():
    labels = {"tau2": {"airline": "Airline", "retail": "Retail", "telecom": "Telecom"},
              "bfcl": {"multi_turn_base": "Base", "multi_turn_long_context": "Long context",
                       "multi_turn_miss_func": "Missing function", "multi_turn_miss_param": "Missing parameter"},
              "acebench_agent": {"agent_multi_step": "Multi-step", "agent_multi_turn": "Multi-turn"}}
    palette = ["#287E72", "#4E70A0", "#B4774B", "#87769D"]
    fig, axes = plt.subplots(1, 3, figsize=(5.5, 2.6))
    for ax, key in zip(axes, ORDER):
        run = DATA["runs"][key]
        points = run["points"]
        for color, (metric, label) in zip(palette, labels[key].items()):
            vals = [run["baseline_dev"]["metrics"][metric]] + [p["dev"]["metrics"][metric] for p in points]
            ax.plot(range(len(vals)), np.array(vals)*100, lw=1.35, marker="o", ms=2.3, color=color, label=label)
        ax.set(xlim=(-.4, MAX_ROUND + .5), ylim=(0, 80), xticks=ROUND_TICKS, yticks=[0, 20, 40, 60, 80], xlabel="Evolution round")
        ax.set_title(NAMES[key], fontsize=9, fontweight="bold")
        ax.grid(axis="y", color="#E5EAE7", lw=.5)
        ax.legend(loc="upper left", bbox_to_anchor=(-.06, -.3), fontsize=7, frameon=False, handlelength=1.3, borderaxespad=0)
        ax.tick_params(length=2)
    axes[0].set_ylabel("Dev score (%)")
    fig.subplots_adjust(left=.085, right=.985, bottom=.405, top=.855, wspace=.27)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in axes:
        bounds = ax.get_legend().get_window_extent(renderer)
        assert bounds.y0 >= 5, "Subset legend must retain bottom padding."
    export(fig, "subsets")


def tables():
    target = ROOT / "tables"
    target.mkdir(exist_ok=True)
    labels = {"tau2": r"$\tau^2$-Bench", "bfcl": "BFCL multi-turn", "acebench_agent": r"ACEBench-Agent$^{\ddagger}$"}
    summary = {"snapshot_at": DATA["snapshot_at"], "runs": {}}
    rows = []
    for key in ORDER:
        run = DATA["runs"][key]
        selected = run["dev_selected_round"]
        point = run["points"][selected-1]
        base = 100 * run["baseline_test"]["metrics"]["overall"]
        score = 100 * point["test"]["metrics"]["overall"]
        last_record = run["points"][-1]["test"]
        last = "---" if last_record is None else "%.2f" % (100*last_record["metrics"]["overall"])
        ci = paired_interval(run)
        delta = None if ci is None else score-base
        difference = r"\text{---}" if ci is None else r"%+.2f\;[%+.1f,\,%+.1f]" % (delta, ci[0], ci[1])
        base_text = "%.2f" % base + (r"$^{\dagger}$" if not run["baseline_test"]["comparable"] else "")
        rows.append(r"%s & %d & %s & \textbf{%.2f} & $%s$ & %s \\" % (labels[key], selected, base_text, score, difference, last))
        summary["runs"][key] = {"selected_round": selected, "last_round": run["points"][-1]["round"], "baseline_test": base,
            "selected_test": score, "delta_pp": delta, "paired_task_bootstrap_ci95_pp": ci,
            "last_test": None if last_record is None else last_record["metrics"]["overall"]*100,
            "total_tasks": sum(p["tasks"] for p in run["points"]),
            "total_episodes": sum(p["episodes"] for p in run["points"]),
            "aborted_episodes": sum(p["audit"]["aborted_episodes"] for p in run["points"])}
    text = r"""\begin{table}[t]
\centering
\caption{Preliminary Qwen3-4B results. Select $t^*$ using dev only (earliest maximum, with the base model eligible), then report its test score. ``Last'' means the final completed checkpoint: R9 for $\tau^2$/BFCL and R10 for ACE. Intervals resample paired test tasks within fixed subsets, retaining their three repeats; they do not measure training-seed variability.}
\label{tab:main}
\small
\setlength{\tabcolsep}{3.2pt}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lcrrrr@{}}
\toprule
Benchmark & $t^*$ & Base (\%) & Selected (\%) & $\Delta$ pp [95\% CI] & Last (\%) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular*}
\vspace{3pt}
\parbox{\linewidth}{\footnotesize $^{\dagger}$Historical $\tau^2$ test base uses the pre-repair replay protocol; no matched-protocol gain is claimed. $^{\ddagger}$ACE uses native tool calling and the two-category macro mean; all ten completed checkpoints have test measurements.}
\end{table}
"""
    (target / "main_results.tex").write_text(text)
    (ROOT / "data/summary_20260915.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    overview()
    subset_plot()
    tables()
