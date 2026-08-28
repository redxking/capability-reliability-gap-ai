#!/usr/bin/env python3
"""Generate the publication figures and their single-source calculation data.

The figures are designed at the manuscript's final 6.75-inch width. Raster
files are emitted at 300 dpi; SVG and TIFF variants are emitted for production.
Figure 2 is plotted from the same CSV that is delivered with the repository.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.ticker import PercentFormatter
from PIL import Image, TiffImagePlugin


INK = "#1F2933"
MUTED = "#52606D"
GRID = "#CBD5E1"
BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#6F4E9C"
LIGHT_BLUE = "#EAF4FB"
LIGHT_ORANGE = "#FCEFEA"
LIGHT_GREEN = "#E7F5F0"
LIGHT_GREY = "#F3F4F6"
WHITE = "#FFFFFF"


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 12,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": MUTED,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "svg.fonttype": "none",
        }
    )


FIGURE_METADATA = {
    "figure1_capability_assurance_axes": (
        "Capability and assurance are separate dimensions",
        "Author-proposed C0–C5 capability and A0–A5 assurance axes. The diagram distinguishes rightward capability gains from upward assurance evidence for a defined use and consequence.",
    ),
    "figure2_reliability_compounding": (
        "Illustrative compounding under an iid step-success model",
        "Calculated p to the power n curves for per-step success probabilities 0.99, 0.999, and 0.9999 over 1 to 200 required unverified steps. The figure is illustrative, not empirical AI-system evidence.",
    ),
    "figure3_agent_assurance_architecture": (
        "Author-proposed control pattern for a consequential AI-agent action",
        "A fail-closed proposal, authorization, pre-action verification, consequence-based approval, constrained execution, post-action verification, state acceptance, audit, monitoring, and recovery architecture.",
    ),
}


def save_all(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    title, description = FIGURE_METADATA[stem]
    png_path = output_dir / f"{stem}.png"
    tiff_path = output_dir / f"{stem}.tiff"
    svg_path = output_dir / f"{stem}.svg"
    # No tight bounding box: every export retains the designed 6.75-inch artboard.
    fig.savefig(
        png_path,
        dpi=300,
        metadata={
            "Author": "Angelis Pseftis",
            "Title": title,
            "Description": description,
        },
    )
    # Re-encode the raster-identical PNG as LZW TIFF with explicit resolution and authorship tags.
    with Image.open(png_path) as raster:
        tags = TiffImagePlugin.ImageFileDirectory_v2()
        tags[270] = description  # ImageDescription
        tags[305] = "Matplotlib and Pillow"  # Software, not authorship
        tags[315] = "Angelis Pseftis"  # Artist
        raster.convert("RGB").save(
            tiff_path,
            format="TIFF",
            compression="tiff_lzw",
            dpi=(300, 300),
            tiffinfo=tags,
        )
    fig.savefig(
        svg_path,
        metadata={
            "Creator": "Angelis Pseftis",
            "Title": title,
            "Description": description,
        },
    )
    plt.close(fig)


def figure1(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.75, 4.15))
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_xticklabels(["C0\nClaimed", "C1\nSelected", "C2\nControlled", "C3\nBounded use", "C4\nDependable", "C5\nAdaptive"])
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_yticklabels(["A0\nNone", "A1\nPreliminary", "A2\nDocumented", "A3\nOperational", "A4\nIndependent", "A5\nContinuous"])
    ax.set_xlabel("Capability level for a defined function and environment")
    ax.set_ylabel("Assurance level for a defined use and consequence")
    ax.set_title("Capability and assurance are separate dimensions", pad=10, weight="bold")
    ax.grid(color=GRID, linewidth=0.7, zorder=0)

    # Regions are deliberately light enough for high-contrast print text.
    ax.add_patch(Rectangle((2.55, 0.0), 2.45, 2.75, facecolor=LIGHT_ORANGE, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((2.55, 3.55), 2.45, 1.45, facecolor=LIGHT_GREEN, edgecolor="none", zorder=0))
    ax.text(3.73, 1.90, "Capability–assurance gap", ha="center", va="center", color=INK, weight="bold")
    ax.text(3.73, 1.52, "capability evidence exceeds\nassurance for the proposed use", ha="center", va="center", color=INK, fontsize=8.1)
    ax.text(3.73, 4.72, "Consequence-appropriate assurance", ha="center", va="center", color=INK, weight="bold")

    stages = [
        (1.0, 1.0, "Selected evidence"),
        (2.0, 1.7, "Controlled evidence"),
        (3.0, 2.2, "Bounded use"),
        (3.9, 4.05, "Assured\nfor this use"),
    ]
    xs, ys, labels = zip(*stages)
    ax.plot(xs[:3], ys[:3], color=BLUE, linewidth=2.2, linestyle="-", marker="o", markersize=7,
            markerfacecolor=WHITE, markeredgewidth=2, zorder=3)
    ax.add_patch(FancyArrowPatch((3.02, 2.25), (3.83, 3.95), arrowstyle="-|>", mutation_scale=13,
                                 linewidth=2.2, color=GREEN, zorder=3))
    for x, y, label in stages:
        color = GREEN if "Assured" in label else BLUE
        if "Assured" in label:
            ax.scatter([x], [y], s=60, facecolor=WHITE, edgecolor=color, linewidth=2.2, zorder=4)
        if "Assured" in label:
            ax.annotate(label, (x, y), xytext=(12, 0), textcoords="offset points", ha="left", va="center",
                        fontsize=8.5, weight="bold", color=INK, zorder=5)
        else:
            ax.annotate(label, (x, y), xytext=(0, 10), textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, weight="bold", color=INK, zorder=5)

    # Explicitly show that capability can improve while assurance does not.
    ax.add_patch(FancyArrowPatch((1.0, 0.62), (4.18, 0.62), arrowstyle="-|>", mutation_scale=12,
                                 linewidth=1.7, linestyle="--", color=ORANGE))
    ax.text(2.6, 0.30, "Rightward capability gains do not, by themselves, move assurance upward",
            ha="center", va="center", fontsize=7.9, color=INK, weight="bold")
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
    fig.subplots_adjust(left=0.20, right=0.945, bottom=0.22, top=0.89)
    save_all(fig, output_dir, "figure1_capability_assurance_axes")


def write_reliability_data(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    probabilities = (0.99, 0.999, 0.9999)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "steps_n",
                "per_step_success_probability_p",
                "workflow_success_probability_p_power_n",
                "formula",
                "assumption_scope",
            ),
        )
        writer.writeheader()
        for p in probabilities:
            for n in range(1, 201):
                writer.writerow(
                    {
                        "steps_n": n,
                        "per_step_success_probability_p": f"{p:.4f}",
                        "workflow_success_probability_p_power_n": f"{p ** n:.12f}",
                        "formula": "p^n",
                        "assumption_scope": "identical independent step-success events; no verification, retry, recovery, or changing conditional probability",
                    }
                )


def read_reliability_data(path: Path) -> dict[float, list[tuple[int, float]]]:
    series: dict[float, list[tuple[int, float]]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            p = float(row["per_step_success_probability_p"])
            n = int(row["steps_n"])
            workflow = float(row["workflow_success_probability_p_power_n"])
            expected = p ** n
            if not math.isclose(workflow, expected, rel_tol=0.0, abs_tol=5e-12):
                raise ValueError(f"source-data mismatch at p={p}, n={n}")
            series.setdefault(p, []).append((n, workflow))
    return series


def figure2(output_dir: Path, data_path: Path) -> None:
    write_reliability_data(data_path)
    series = read_reliability_data(data_path)
    fig, ax = plt.subplots(figsize=(6.75, 4.25))
    styles = {
        0.99: (ORANGE, "-", "o"),
        0.999: (BLUE, "--", "s"),
        0.9999: (GREEN, "-.", "^"),
    }
    for p, points in sorted(series.items()):
        color, line_style, marker = styles[p]
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        ax.plot(x, y, color=color, linestyle=line_style, linewidth=2.1, marker=marker,
                markevery=25, markersize=4.3, markerfacecolor=WHITE, markeredgewidth=1.2,
                label=f"Per-step success p = {p * 100:.2f}%")

    ax.axhline(0.99, color=MUTED, linewidth=1.1, linestyle=(0, (2, 3)))
    ax.annotate("99% end-to-end target", xy=(188, 0.99), xytext=(160, 0.93),
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 1.0},
                ha="left", va="top", fontsize=8.2, color=MUTED,
                bbox={"facecolor": WHITE, "edgecolor": "none", "pad": 0.8})
    ax.axvline(100, color=GRID, linewidth=1.0, linestyle=":")
    for p, color in ((0.99, ORANGE), (0.999, BLUE), (0.9999, GREEN)):
        value = p ** 100
        ax.scatter([100], [value], s=28, facecolor=WHITE, edgecolor=color, linewidth=1.6, zorder=4)
        dx = 7
        dy = {0.99: -0.035, 0.999: -0.045, 0.9999: -0.035}[p]
        ax.annotate(f"{value * 100:.1f}%", (100, value), xytext=(100 + dx, value + dy),
                    arrowprops={"arrowstyle": "-", "color": color, "lw": 1},
                    color=INK, fontsize=8.3, weight="bold")

    required = 0.99 ** (1 / 100)
    ax.text(7, 0.055, f"At n = 100, a 99% end-to-end target requires\np = 0.99^(1/100) = {required * 100:.5f}% per step.",
            ha="left", va="bottom", fontsize=8.4,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": LIGHT_GREY, "edgecolor": GRID})
    ax.set_xlim(-2, 200)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Number of required unverified steps, n")
    ax.set_ylabel("Probability every step succeeds")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    fig.suptitle("Illustrative compounding under an iid step-success model", weight="bold", y=0.975)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.922), ncol=3, frameon=False,
               handlelength=2.8, columnspacing=1.2)
    fig.text(0.5, 0.012,
             "Assumptions: identical, independent step-success events; no verifier, retry, recovery,\n"
             "or changing conditional probability. Illustrative calculation; not empirical AI-system evidence.",
             ha="center", va="bottom", fontsize=8.0, color=MUTED)
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.20, top=0.82)
    save_all(fig, output_dir, "figure2_reliability_compounding")


def rounded_box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str,
                face: str, edge: str, fontsize: float = 8.7, weight: str = "normal") -> None:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.018,rounding_size=0.035",
                                facecolor=face, edgecolor=edge, linewidth=1.25))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            weight=weight, color=INK)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], label: str = "",
          color: str = BLUE, style: str = "-") -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11,
                                 linewidth=1.4, linestyle=style, color=color,
                                 connectionstyle="arc3,rad=0.0"))
    if label:
        ax.text((start[0] + end[0]) / 2 + 0.012, (start[1] + end[1]) / 2,
                label, fontsize=7.7, color=INK, va="center", ha="left",
                bbox={"facecolor": WHITE, "edgecolor": "none", "pad": 0.5})


def figure3(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.75, 6.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Author-proposed control pattern for a consequential AI-agent action", pad=8, weight="bold")

    x, w, h = 0.18, 0.55, 0.061
    ys = [0.885, 0.795, 0.705, 0.615, 0.525, 0.435, 0.345, 0.255]
    boxes = [
        ("1  Principal and bounded objective", LIGHT_BLUE, BLUE),
        ("2  Orchestrator + model: typed proposal and evidence", WHITE, BLUE),
        ("3  Action-time identity, purpose, scope, and budget", LIGHT_ORANGE, ORANGE),
        ("4  Independent pre-action verification", LIGHT_GREEN, GREEN),
        ("5  Consequence-based approval gate", LIGHT_GREY, PURPLE),
        ("6  Constrained gateway + target system", LIGHT_BLUE, BLUE),
        ("7  Post-action verification of result and side effects", LIGHT_GREEN, GREEN),
        ("8  Accept versioned state / checkpoint", LIGHT_GREY, MUTED),
    ]
    for y, (label, face, edge) in zip(ys, boxes):
        rounded_box(ax, x, y, w, h, label, face, edge, fontsize=8.0, weight="bold")
    for upper, lower in zip(ys[:-1], ys[1:]):
        arrow(ax, (x + w / 2, upper), (x + w / 2, lower + h), color=INK)

    # A documented low-consequence policy path may bypass separate human approval.
    bypass_x = 0.095
    ax.add_patch(FancyArrowPatch((x, ys[3] + h / 2), (bypass_x, ys[3] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25, linestyle="--", color=GREEN))
    ax.add_patch(FancyArrowPatch((bypass_x, ys[3] + h / 2), (bypass_x, ys[5] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25, linestyle="--", color=GREEN))
    ax.add_patch(FancyArrowPatch((bypass_x, ys[5] + h / 2), (x, ys[5] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25, linestyle="--", color=GREEN))
    ax.text(0.078, 0.555, "documented low-impact\npolicy path", rotation=90, color=INK,
            fontsize=8.0, ha="center", va="center", weight="bold")

    # Authorization, verification, approval, or postcondition failure is fail-closed.
    rounded_box(ax, 0.79, 0.525, 0.19, 0.115,
                "PRE-ACTION FAILURE\nDENY • HOLD\nESCALATE\nSAFE STATE",
                LIGHT_ORANGE, ORANGE, fontsize=7.8, weight="bold")
    fail_bus_x = 0.762
    fail_sources = (ys[2] + h / 2, ys[3] + h / 2, ys[4] + h / 2)
    ax.plot([fail_bus_x, fail_bus_x], [min(fail_sources), max(fail_sources)], color=ORANGE,
            linewidth=1.15, linestyle=":")
    for source_y in fail_sources:
        ax.add_patch(FancyArrowPatch((x + w, source_y), (fail_bus_x, source_y), arrowstyle="-|>",
                                     mutation_scale=8, linewidth=1.05, linestyle=":", color=ORANGE))
    ax.add_patch(FancyArrowPatch((fail_bus_x, 0.582), (0.79, 0.582), arrowstyle="-|>",
                                 mutation_scale=9, linewidth=1.15, color=ORANGE))

    # A post-action check fails after execution, so it blocks state acceptance and triggers containment.
    rounded_box(ax, 0.79, 0.325, 0.19, 0.115,
                "POST-ACTION FAILURE\nCONTAIN\nREJECT STATE\nRECOVER • NOTIFY",
                LIGHT_ORANGE, ORANGE, fontsize=7.8, weight="bold")
    ax.add_patch(FancyArrowPatch((x + w, ys[6] + h / 2), (0.79, 0.382), arrowstyle="-|>",
                                 mutation_scale=9, linewidth=1.2, linestyle=":", color=ORANGE))

    # Independent monitoring retains revocation and emergency-disable authority.
    rounded_box(ax, 0.79, 0.755, 0.19, 0.105, "Independent monitor\nrevoke • disable\ncontain • investigate", LIGHT_ORANGE, ORANGE,
                fontsize=8.0, weight="bold")
    arrow(ax, (0.81, 0.755), (x + w, ys[2] + h / 2), "revoke", color=ORANGE, style="--")
    ax.add_patch(FancyArrowPatch((0.985, 0.755), (0.985, ys[5] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25, linestyle="--", color=ORANGE))
    ax.add_patch(FancyArrowPatch((0.985, ys[5] + h / 2), (x + w, ys[5] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25, linestyle="--", color=ORANGE))

    # Results and telemetry can inform a new proposal only after post-action checks.
    ax.add_patch(FancyArrowPatch((x, ys[6] + h / 2), (0.035, ys[6] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.2, color=PURPLE))
    ax.add_patch(FancyArrowPatch((0.035, ys[6] + h / 2), (0.035, ys[1] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.2, color=PURPLE))
    ax.add_patch(FancyArrowPatch((0.035, ys[1] + h / 2), (x, ys[1] + h / 2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.2, color=PURPLE))
    ax.text(0.022, 0.575, "checked result + telemetry", rotation=90, color=PURPLE,
            fontsize=8.0, ha="center", va="center", weight="bold")

    rounded_box(ax, 0.08, 0.05, 0.39, 0.125,
                "Audit event stream\ntamper-evident\naccess-controlled • privacy-aware\nall requests • decisions\npass/fail results • versions", LIGHT_GREY, MUTED,
                fontsize=7.7, weight="bold")
    rounded_box(ax, 0.53, 0.05, 0.39, 0.125,
                "Recovery + compensating controls\nlast accepted checkpoint • isolate\nrestore • notify", LIGHT_GREY, MUTED,
                fontsize=7.8, weight="bold")
    arrow(ax, (x + w / 2 - 0.02, ys[7]), (0.275, 0.175), "accepted-state event", color=MUTED, style=":")
    ax.add_patch(FancyArrowPatch((0.885, 0.325), (0.725, 0.175), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.2, linestyle=":", color=MUTED,
                                 connectionstyle="arc3,rad=0.10"))
    ax.text(0.84, 0.235, "contain / recover", fontsize=8.0, color=MUTED,
            ha="center", va="center", weight="bold")

    fig.text(0.5, 0.012,
             "Control placement is a design proposal, not effectiveness evidence.\n"
             "Independence, coverage, false acceptance, and recovery must be tested.",
             ha="center", va="bottom", fontsize=8.0, color=MUTED)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.085, top=0.925)
    save_all(fig, output_dir, "figure3_agent_assurance_architecture")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figures", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    setup_style()
    figure1(args.figures)
    figure2(args.figures, args.data / "reliability_compounding_long.csv")
    figure3(args.figures)


if __name__ == "__main__":
    main()
