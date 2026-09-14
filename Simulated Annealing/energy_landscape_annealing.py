"""GRÁFICO 01 — Energy landscape and a deterministic local greedy trap.

The marker represents an abstract search state, never mechanical motion.
Dependencies: Python 3.10+, NumPy, Matplotlib; FFmpeg/libx264 for MP4.
Run normally to export; --preview, --validate-only and --self-test are available.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
import shutil
import subprocess
import time
from typing import Callable

import matplotlib
import numpy as np
from matplotlib.animation import FFMpegWriter

PREVIEW_ONLY = False

PHASE_TIMES = {
    "landscape_end": 3.0,
    "descent_end": 7.0,
    "left_trial_end": 9.0,
    "right_trial_end": 11.0,
    "both_moves": 11.7,
    "trapped": 12.3,
    "question": 13.0,
    "worse_question": 14.0,
    "final_end": 15.0,
}
CONFIG = {
    "duration_s": 15.0, "fps": 60, "total_frames": 900,
    "x_min": -3.8, "x_max": 3.8, "target_minimum": -1.47,
    "start_fraction": 0.65, "step_fraction": 0.055,
    "neighbor_fraction": 0.35, "min_visual_delta": 0.12,
    "eps": 1e-12, "max_steps": 1000, "neighbor_samples": 500,
    "dpi": 120, "figsize": (16.0, 9.0), "bitrate": 10000,
    "preview_time": 8.3,
    "output_mp4": "energy_landscape_greedy_trap.mp4",
    "output_png": "energy_landscape_greedy_trap_final_frame.png",
}
PALETTE = {
    "bg": "#0f111a", "panel": "#131622", "border": "#343b50",
    "curve": "#8be9fd", "state": "#ffb86c", "accept": "#50fa7b",
    "reject": "#ff6868", "local": "#bd93f9",
    "text": "#f8f8f2", "muted": "#8b93a7",
}
EnergyFunction = Callable[[object], object]


@dataclass(frozen=True)
class Point:
    x: float
    energy: float


@dataclass(frozen=True)
class Proposal:
    current: Point
    trial: Point
    delta: float
    accepted: bool
    after: Point


@dataclass(frozen=True)
class Frame:
    seconds: float
    phase: str
    point: Point | None
    proposal: Proposal | None
    trail: tuple[Point, ...]
    candidate_alpha: float
    phase_label: str
    caption: str
    decision: str
    status: str
    hook: str


def point_at(energy_fn: EnergyFunction, x: float) -> Point:
    return Point(float(x), float(energy_fn(x)))


def build_energy_landscape(config: dict) -> EnergyFunction:
    """Preserve the original quadratic term and all five Gaussian wells.

    The original 5000-sample additive reference is preserved exactly.
    Its sampled minimum is 0.60; the continuous minimum is approximately 0.60.
    This reference changes no gradient, basin or energy difference.
    """
    wells = [
        (-2.90, 2.00, 0.42), (-1.47, 2.70, 0.48),
        (0.01, 2.20, 0.45), (1.45, 2.80, 0.48),
        (2.75, 5.00, 0.55),
    ]

    def raw_potential(x):
        values = np.asarray(x, dtype=float)
        result = 0.10 * values ** 2
        for center, depth, width in wells:
            result = result - depth * np.exp(
                -(values - center) ** 2 / (2.0 * width ** 2)
            )
        return result

    grid = np.linspace(config["x_min"], config["x_max"], 5000)
    offset = np.min(raw_potential(grid)) - 0.60

    def energy(x):
        return raw_potential(np.asarray(x, dtype=float)) - offset

    return energy


def refine_extremum(fn, left: float, right: float, sign: int) -> float:
    """Golden-section refinement within an isolated sampled extremum."""
    ratio = (np.sqrt(5.0) - 1.0) / 2.0
    a, b = left, right
    c, d = b - ratio * (b - a), a + ratio * (b - a)
    fc, fd = sign * float(fn(c)), sign * float(fn(d))
    for _ in range(64):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - ratio * (b - a)
            fc = sign * float(fn(c))
        else:
            a, c, fc = c, d, fd
            d = a + ratio * (b - a)
            fd = sign * float(fn(d))
    return float((a + b) / 2.0)


def detect_minima(energy_fn, x_min, x_max, n_points=5000) -> dict:
    """Detect minima/maxima on a fine grid, then refine their locations."""
    if not x_min < x_max or n_points < 5:
        raise RuntimeError("Invalid landscape domain or sampling grid.")
    grid = np.linspace(x_min, x_max, n_points)
    values = np.asarray(energy_fn(grid))
    if not np.isfinite(values).all():
        raise RuntimeError("Non-finite landscape.")
    extrema = {}
    for name, sign in (("all_minima", 1), ("all_maxima", -1)):
        ordered = sign * values
        indices = np.flatnonzero(
            (ordered[1:-1] < ordered[:-2])
            & (ordered[1:-1] <= ordered[2:])
        ) + 1
        extrema[name] = tuple(
            point_at(energy_fn, refine_extremum(
                energy_fn, grid[i - 1], grid[i + 1], sign
            )) for i in indices
        )
    if not extrema["all_minima"] or not extrema["all_maxima"]:
        raise RuntimeError("The landscape must contain minima and barriers.")
    return {**extrema, "x_grid": grid, "E_grid": values}


def evaluate_proposal(current: Point, x_trial: float, energy_fn, eps) -> Proposal:
    trial = point_at(energy_fn, x_trial)
    delta = trial.energy - current.energy
    accepted = delta < -eps
    return Proposal(current, trial, delta, accepted, trial if accepted else current)


def find_rejected_neighbor_proposals(current, left, right, step, energy_fn,
                                     config) -> tuple[Proposal, Proposal]:
    """Find visible uphill neighbors without leaving the selected basin.

    Search each side in increasing distance, limited to a fixed fraction of
    the distance to its barrier. No rejected candidate becomes a path state.
    """
    proposals = []
    for direction, boundary in ((-1, left), (1, right)):
        limit = config["neighbor_fraction"] * abs(boundary.x - current.x)
        if limit < step:
            raise RuntimeError("Insufficient local space for a trial.")
        for distance in np.linspace(step, limit, config["neighbor_samples"]):
            proposal = evaluate_proposal(
                current, current.x + direction * distance,
                energy_fn, config["eps"],
            )
            if proposal.delta >= config["min_visual_delta"]:
                proposals.append(proposal)
                break
        else:
            raise RuntimeError("No visible uphill neighbor inside the basin.")
    return tuple(proposals)


def build_frame_plan(data: dict, config: dict, energy_fn) -> tuple[Frame, ...]:
    """Prepare every visual coordinate and readout before validation/rendering.

    Smoothstep changes only the visual x between accepted states; visual
    energy is always evaluated at that x. During interpolation the trial HUD
    is hidden, so a discrete proposal delta is never paired with a moving E.
    """
    phases, path, moves = data["phase_times"], data["greedy_path"], data["moves"]
    result = []
    for index in range(config["total_frames"]):
        seconds = index / config["fps"]
        proposal, alpha, hook = None, 0.0, ""
        position, trail = None, ()
        decision, status = "", ""
        if seconds < phases["landscape_end"]:
            phase = "landscape"
            label, caption = "OBJECTIVE LANDSCAPE", "MULTIPLE LOCAL MINIMA"
        elif seconds < phases["descent_end"]:
            phase = "descent"
            progress = ((seconds - phases["landscape_end"])
                        / (phases["descent_end"] - phases["landscape_end"]))
            slot = progress * len(moves)
            step_index = min(int(slot), len(moves) - 1)
            fraction = slot - step_index
            move = moves[step_index]
            weight = float(np.clip((fraction - 0.30) / 0.55, 0.0, 1.0))
            weight = weight * weight * (3.0 - 2.0 * weight)
            position = point_at(
                energy_fn, move.current.x + weight * (move.after.x - move.current.x)
            )
            trail = path[:step_index + 1 + int(fraction >= 0.85)]
            if fraction < 0.30:
                proposal, alpha = move, 1.0
            label, caption = "GREEDY SEARCH", "LOWER E  →  ACCEPT"
            decision = "ACCEPT"
            status = f"LOCAL STEP {step_index + 1:02d} / {len(moves):02d}"
        elif seconds < phases["right_trial_end"]:
            is_left = seconds < phases["left_trial_end"]
            phase = "left_trial" if is_left else "right_trial"
            start = phases["descent_end"] if is_left else phases["left_trial_end"]
            end = phases["left_trial_end"] if is_left else phases["right_trial_end"]
            progress = (seconds - start) / (end - start)
            alpha = min(1.0, max(0.0, progress / 0.12),
                        max(0.0, (1.0 - progress) / 0.15))
            proposal = data["left_rejected_proposal" if is_left
                            else "right_rejected_proposal"]
            position, trail = path[-1], path
            label = "LEFT LOCAL PROPOSAL" if is_left else "RIGHT LOCAL PROPOSAL"
            caption, decision, status = "HIGHER E  →  REJECT", "REJECT", "LOCAL MINIMUM"
        else:
            phase = "trap"
            position, trail = path[-1], path
            label, caption = "LOCAL MINIMUM", "NO LOWER-ENERGY LOCAL MOVE"
            if seconds >= phases["both_moves"]:
                caption = "BOTH LOCAL MOVES INCREASE E"
            if seconds >= phases["trapped"]:
                label = "GREEDY SEARCH IS TRAPPED"
            if seconds >= phases["question"]:
                hook = "HOW CAN WE CROSS THE BARRIER?"
            if seconds >= phases["worse_question"]:
                hook += "\n→ ACCEPT A WORSE STATE?"
            decision, status = "NO MOVE", "TRAPPED IN LOCAL MINIMUM"
        result.append(Frame(seconds, phase, position, proposal, trail, alpha,
                            label, caption, decision, status, hook))
    return tuple(result)


def build_greedy_demonstration(config, landscape_info, energy_fn) -> dict:
    """Run deterministic local argmin search; basin bounds never force moves."""
    minima, maxima = landscape_info["all_minima"], landscape_info["all_maxima"]
    local = min(minima, key=lambda p: abs(p.x - config["target_minimum"]))
    lower = min(minima, key=lambda p: p.energy)
    lefts = [p for p in maxima if p.x < local.x]
    rights = [p for p in maxima if p.x > local.x]
    if not lefts or not rights or lower.energy >= local.energy:
        raise RuntimeError("Target basin must have two barriers and a lower basin.")
    left, right = lefts[-1], rights[0]
    barrier = right if lower.x > local.x else left
    start = local.x + config["start_fraction"] * (left.x - local.x)
    step = config["step_fraction"] * (right.x - left.x)
    if not 0 < config["start_fraction"] < 1 or not 0 < step < (right.x-left.x)/4:
        raise RuntimeError("Invalid starting fraction or greedy step.")
    current = point_at(energy_fn, start)
    path, moves = [current], []
    for _ in range(config["max_steps"]):
        candidates = [
            evaluate_proposal(current, current.x + direction * step,
                              energy_fn, config["eps"])
            for direction in (-1, 1)
            if config["x_min"] <= current.x + direction * step <= config["x_max"]
        ]
        best = min(candidates, key=lambda p: p.trial.energy)
        if not best.accepted:
            break
        moves.append(best)
        current = best.after
        path.append(current)
    else:
        raise RuntimeError("Greedy search exceeded its step limit.")
    if not moves:
        raise RuntimeError("The starting point produced no greedy descent.")
    trial_left, trial_right = find_rejected_neighbor_proposals(
        current, left, right, step, energy_fn, config
    )
    data = {
        "greedy_path": tuple(path), "moves": tuple(moves), "step": step,
        "left_rejected_proposal": trial_left,
        "right_rejected_proposal": trial_right, "local_min": local,
        "basin_bounds": (left, right), "barrier": barrier,
        "barrier_height": barrier.energy - local.energy,
        "lower_basin": lower, "phase_times": dict(PHASE_TIMES),
    }
    data["frames"] = build_frame_plan(data, config, energy_fn)
    return data


def validate_greedy_demonstration(data, config, energy_fn, verbose=True) -> dict:
    """Fail with RuntimeError before rendering if any invariant is violated."""
    path, moves, frames = data["greedy_path"], data["moves"], data["frames"]
    local, lower, barrier = data["local_min"], data["lower_basin"], data["barrier"]
    left, right = data["basin_bounds"]
    rejected = (data["left_rejected_proposal"], data["right_rejected_proposal"])
    eps, step = config["eps"], data["step"]
    checks = {}

    def check(label, result):
        checks[label] = bool(result)

    def same(a, b):
        return np.isclose(a, b, atol=1e-10, rtol=0)

    def valid_point(p):
        return np.isfinite([p.x, p.energy]).all() and same(p.energy, energy_fn(p.x))

    def valid_delta(p):
        return same(p.delta, energy_fn(p.trial.x) - energy_fn(p.current.x))

    check("start state finite", valid_point(path[0]))
    check("start inside selected basin", left.x < path[0].x < right.x)
    check("start higher than final", path[0].energy > path[-1].energy)
    check("energy decreases on accepts", bool(moves) and all(
        m.accepted and m.delta < -eps and m.after == m.trial for m in moves))
    check("monotone accepted energy", np.all(np.diff([p.energy for p in path]) < -eps))
    check("connected accepted trajectory", len(path) == len(moves) + 1 and all(
        m.current == path[i] and m.after == path[i+1] for i, m in enumerate(moves)))
    check("true local argmin choices", all(
        same(abs(m.trial.x - m.current.x), step)
        and m.trial.energy <= min(float(energy_fn(m.current.x - step)),
                                 float(energy_fn(m.current.x + step))) + eps
        for m in moves))
    check("local minimum reached", abs(path[-1].x - local.x) <= step / 2 + 1e-3)
    check("no lower discrete neighbor", all(
        float(energy_fn(path[-1].x + direction*step)) > path[-1].energy
        for direction in (-1, 1)))
    for name, proposal, direction, bound in zip(
            ("left", "right"), rejected, (-1, 1), (left, right)):
        check(f"{name} proposal on correct side",
              direction * (proposal.trial.x - path[-1].x) > 0)
        check(f"{name} proposal uphill", proposal.delta > eps)
        check(f"{name} proposal rejected", not proposal.accepted)
        check(f"{name} rejection unchanged", proposal.current == path[-1]
              and proposal.after == path[-1])
        check(f"{name} proposal remains local",
              left.x < proposal.trial.x < right.x
              and abs(proposal.trial.x-path[-1].x)
              <= config["neighbor_fraction"] * abs(bound.x-path[-1].x) + eps)
    check("barrier not crossed", all(left.x < p.x < right.x for p in path))
    check("lower basin beyond barrier", lower.energy < local.energy
          and min(local.x, lower.x) < barrier.x < max(local.x, lower.x)
          and barrier.energy > local.energy)
    check("computed barrier height", same(
        data["barrier_height"], energy_fn(barrier.x) - energy_fn(local.x)))
    proposals = (*moves, *rejected)
    check("exact proposal delta values", all(valid_delta(p) for p in proposals))
    check("greedy decisions consistent", all(
        p.accepted == (p.delta < -eps) for p in proposals))
    points = (*path, local, lower, left, right, barrier,
              *(p.trial for p in proposals))
    check("finite model values on E(x)", all(valid_point(p) for p in points)
          and np.isfinite([step, data["barrier_height"]]).all())
    check("duration / fps / frames", config["duration_s"] == 15.0
          and config["fps"] == 60 and config["total_frames"] == 900
          and len(frames) == config["duration_s"] * config["fps"])
    check("Full HD dimensions", tuple(round(s*config["dpi"])
          for s in config["figsize"]) == (1920, 1080))
    check("phase boundaries in seconds", data["phase_times"] == PHASE_TIMES)
    check("frame timestamps", all(same(f.seconds, i/config["fps"])
                                 for i, f in enumerate(frames)))
    check("finite frame metadata", all(
        np.isfinite([f.seconds, f.candidate_alpha]).all()
        and 0 <= f.candidate_alpha <= 1 for f in frames))
    check("validated frame plan unchanged",
          frames == build_frame_plan(data, config, energy_fn))
    check("landscape initially alone", all(
        f.point is None and f.proposal is None and not f.trail
        for f in frames if f.seconds < 3))
    check("every visual state on E(x)", all(
        f.point is None or (valid_point(f.point) and left.x < f.point.x < right.x)
        for f in frames))
    check("rejections and final state fixed", all(
        f.point == path[-1] for f in frames if f.seconds >= 7))
    check("only accepted states in trail", all(
        f.trail == path[:len(f.trail)] for f in frames))
    check("HUD and candidate use same data", all(
        f.proposal is None or (
            f.proposal in proposals and f.point == f.proposal.current
            and valid_delta(f.proposal))
        for f in frames))
    check("both rejected trials visible", all(any(
        f.proposal == p and f.candidate_alpha > 0.9 for f in frames)
        for p in rejected))
    texts = " ".join(f.phase_label + f.caption + f.decision + f.status + f.hook
                     for f in frames).casefold()
    forbidden = ("temperature", "cooling", "thermal escape", "metropolis",
                 "p_acc", "p_accept", "low-t", "u < p", "u > p", "annealing")
    check("narrative contains no later rule", not any(w in texts for w in forbidden))
    check("final question remains unanswered",
          frames[-1].hook == "HOW CAN WE CROSS THE BARRIER?\n→ ACCEPT A WORSE STATE?")
    if verbose:
        print("\n" + "=" * 67 + "\nGREEDY LANDSCAPE VALIDATION\n" + "=" * 67)
        for label, passed in checks.items():
            print(f"{label + ':':49s} {'PASS' if passed else 'FAIL'}")
        print(f"\nVALIDATION STATUS: {'PASS' if all(checks.values()) else 'FAIL'}")
        print("=" * 67)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("Validation failed: " + "; ".join(failures))
    return checks


def run_self_tests(data, config, landscape_info, energy_fn):
    """Regression tests include determinism and deliberate invalid data."""
    repeated = build_greedy_demonstration(config, landscape_info, energy_fn)
    if repeated != data:
        raise RuntimeError("Deterministic replay failed.")
    cases = []
    p = data["left_rejected_proposal"]
    cases.append(({**data, "left_rejected_proposal": replace(p, delta=-0.1)}, config))
    cases.append(({**data, "right_rejected_proposal": replace(
        data["right_rejected_proposal"], accepted=True)}, config))
    path = (Point(float("nan"), 0.0), *data["greedy_path"][1:])
    cases.append(({**data, "greedy_path": path}, config))
    cases.append(({**data, "barrier_height": data["barrier_height"] + 1}, config))
    final = replace(data["frames"][-1], point=data["lower_basin"])
    cases.append(({**data, "frames": (*data["frames"][:-1], final)}, config))
    cases.append((data, {**config, "fps": 30}))
    for invalid, invalid_config in cases:
        try:
            validate_greedy_demonstration(invalid, invalid_config, energy_fn, False)
        except RuntimeError:
            continue
        raise RuntimeError("A deliberately invalid case escaped validation.")
    print(f"SELF-TEST: deterministic replay + {len(cases)} invalid cases PASS")


def build_figure(config, landscape_info, data) -> dict:
    """Build the original dark scientific visual language around greedy search."""
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans",
                         "text.color": PALETTE["text"],
                         "axes.labelcolor": PALETTE["muted"],
                         "xtick.color": PALETTE["muted"],
                         "ytick.color": PALETTE["muted"]})
    fig = plt.figure(figsize=config["figsize"], dpi=config["dpi"],
                     facecolor=PALETTE["bg"])
    fig.text(.052, .953, "ENERGY LANDSCAPE", fontsize=22, weight="bold")
    subtitle = fig.text(.053, .924, "", fontsize=11, color=PALETTE["muted"])
    fig.text(.948, .954, "ANIMAÇÃO CONCEITUAL", ha="right", fontsize=10,
             color=PALETTE["state"], bbox=dict(
                 boxstyle="round,pad=.4", fc=PALETTE["panel"],
                 ec=PALETTE["state"], lw=1))
    fig.text(.948, .924, "XLIII SEMANA DA FÍSICA · UFG", ha="right",
             fontsize=9, color=PALETTE["muted"])

    ax = fig.add_axes([.065, .17, .62, .68], facecolor=PALETTE["panel"])
    ax.set(xlim=(config["x_min"], config["x_max"]), ylim=(-.15, 6.3),
           xlabel="CONFIGURATION COORDINATE x",
           ylabel="EFFECTIVE ENERGY E(x)  [c.u.]")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(PALETTE["border"])
    ax.tick_params(labelsize=9)
    ax.grid(color=PALETTE["muted"], alpha=.12, linestyle=":")
    grid, energies = landscape_info["x_grid"], landscape_info["E_grid"]
    ax.plot(grid, energies, color=PALETTE["curve"], lw=6, alpha=.12)
    ax.plot(grid, energies, color=PALETTE["curve"], lw=2.6, zorder=3)
    ax.fill_between(grid, -.15, energies, color=PALETTE["curve"], alpha=.04)
    local, lower, barrier = data["local_min"], data["lower_basin"], data["barrier"]
    local_line = ax.axvline(local.x, ls="--", lw=1, color=PALETTE["local"], alpha=0)
    lower_line = ax.axvline(lower.x, ls="--", lw=1, color=PALETTE["accept"], alpha=0)
    local_label = ax.text(local.x, 5.65, "LOCAL BASIN", ha="center", fontsize=9,
                          color=PALETTE["local"])
    lower_label = ax.text(lower.x, 5.65, "LOWER-ENERGY\nBASIN", ha="center",
                          fontsize=9, color=PALETTE["accept"], linespacing=1.5)
    bounds = data["basin_bounds"]
    basin_fill = ax.axvspan(bounds[0].x, bounds[1].x,
                            color=PALETTE["local"], alpha=0)
    barrier_line = ax.plot([barrier.x, barrier.x], [local.energy, barrier.energy],
                           color=PALETTE["reject"], ls=":", lw=1.3)[0]
    barrier_note = ax.annotate(
        f"ENERGY BARRIER\nΔE = +{data['barrier_height']:.3f}",
        xy=(barrier.x, barrier.energy), xytext=(.24, .77),
        textcoords="axes fraction", fontsize=10, color=PALETTE["reject"],
        ha="left", linespacing=1.6, arrowprops=dict(
            arrowstyle="->", color=PALETTE["reject"], lw=1.1),
        bbox=dict(boxstyle="round,pad=.45", fc=PALETTE["panel"],
                  ec=PALETTE["border"]), zorder=8)
    stem = ax.plot([], [], ":", color=PALETTE["state"], alpha=.3, lw=1)[0]
    glow = ax.scatter([], [], s=380, c=PALETTE["state"], alpha=.13, zorder=6)
    marker = ax.scatter([], [], s=80, facecolor=PALETTE["text"],
                        edgecolor=PALETTE["state"], linewidth=2, zorder=8)
    trail = ax.scatter([], [], s=18, color=PALETTE["state"], alpha=.35, zorder=5)
    candidate = ax.scatter([], [], s=125, facecolor="none", linewidth=2, zorder=9)
    connector = ax.plot([], [], "--", lw=1.3, zorder=4)[0]
    candidate_label = ax.annotate(
        "", xy=(0, 0), xytext=(-75, -65), textcoords="offset points",
        fontsize=10, ha="center", color=PALETTE["reject"],
        arrowprops=dict(arrowstyle="-", color=PALETTE["muted"], lw=.8),
        bbox=dict(boxstyle="round,pad=.45", fc=PALETTE["panel"],
                  ec=PALETTE["border"]), zorder=9)
    hud = fig.add_axes([.735, .17, .215, .68], facecolor=PALETTE["bg"])
    hud.set(xlim=(0, 1), ylim=(0, 1))
    hud.axis("off")
    hud.text(0, .97, "GREEDY SEARCH", fontsize=14, weight="bold")
    for y in (.91, .665, .355, .14):
        hud.axhline(y, color=PALETTE["border"], lw=.8)
    labels = [("CURRENT x", .855), ("CURRENT E", .755),
              ("TRIAL x′", .58), ("TRIAL E", .50), ("STEP ΔE", .42)]
    hud_values = []
    for name, y in labels:
        hud.text(0, y, name, fontsize=9, color=PALETTE["muted"], va="center")
        hud_values.append(hud.text(1, y, "", fontsize=15, fontfamily="monospace",
                                   ha="right", va="center"))
    hud.text(0, .62, "LOCAL PROPOSAL", fontsize=9, color=PALETTE["local"])
    hud.text(0, .31, "GREEDY RULE", fontsize=9, color=PALETTE["muted"])
    hud.text(0, .265, "ΔE < 0  →  ACCEPT", fontsize=11, color=PALETTE["accept"])
    hud.text(0, .22, "ΔE ≥ 0  →  REJECT", fontsize=11, color=PALETTE["reject"])
    hud.text(0, .095, "CURRENT DECISION", fontsize=9, color=PALETTE["muted"])
    decision = hud.text(1, .095, "", ha="right", fontsize=12, weight="bold")
    status = hud.text(0, .025, "", fontsize=9, color=PALETTE["local"])
    phase = fig.text(.065, .875, "", fontsize=11, weight="bold")
    caption = fig.text(.065, .095, "", fontsize=11, color=PALETTE["local"])
    hook = fig.text(.95, .095, "", fontsize=12, ha="right", va="center",
                    color=PALETTE["state"], linespacing=1.6)
    fig.text(.052, .038, "x = abstract configuration coordinate",
             fontsize=9, color=PALETTE["muted"])
    fig.text(.948, .038, "E(x) = effective objective / energy [c.u.]",
             fontsize=9, ha="right", color=PALETTE["muted"])
    clock = fig.text(.948, .875, "", fontsize=9, ha="right",
                     color=PALETTE["muted"], fontfamily="monospace")
    return dict(fig=fig, ax=ax, hud=hud, subtitle=subtitle, phase=phase,
                caption=caption, hook=hook, clock=clock, stem=stem, glow=glow,
                marker=marker, trail=trail, candidate=candidate,
                connector=connector, candidate_label=candidate_label,
                hud_values=hud_values, decision=decision, status=status,
                local_line=local_line, lower_line=lower_line,
                local_label=local_label, lower_label=lower_label,
                basin_fill=basin_fill, barrier_line=barrier_line,
                barrier_note=barrier_note)


def update_frame(index: int, data: dict, objects: dict, config: dict):
    """Only display the validated frame; perform no scientific decisions."""
    frame = data["frames"][index]
    active, trapped = frame.point is not None, frame.phase == "trap"
    objects["hud"].set_visible(active)
    objects["subtitle"].set_text(
        "GREEDY SEARCH // LOCAL MINIMUM TRAP" if active
        else "OBJECTIVE LANDSCAPE // MULTIPLE LOCAL MINIMA")
    objects["phase"].set_text(frame.phase_label)
    objects["caption"].set_text(frame.caption)
    objects["hook"].set_text(frame.hook)
    objects["clock"].set_text(f"{frame.seconds:05.2f} s / {config['duration_s']:.2f} s")
    objects["local_line"].set_alpha(.4 if active else .12)
    objects["lower_line"].set_alpha(.4 if trapped else .12)
    objects["local_label"].set_text("LOCAL MINIMUM" if trapped else "LOCAL BASIN")
    objects["basin_fill"].set_alpha(.045 if trapped else 0)
    for key in ("barrier_note", "barrier_line"):
        objects[key].set_visible(trapped)
    position = [] if not active else [[frame.point.x, frame.point.energy]]
    for key in ("marker", "glow"):
        objects[key].set_offsets(np.asarray(position).reshape(-1, 2))
    objects["stem"].set_data(
        [frame.point.x]*2 if active else [],
        [-.15, frame.point.energy] if active else [])
    objects["trail"].set_offsets(np.asarray(
        [(p.x, p.energy) for p in frame.trail]).reshape(-1, 2))
    values = objects["hud_values"]
    for obj in values:
        obj.set_text("—")
        obj.set_color(PALETTE["text"])
    if active:
        values[0].set_text(f"{frame.point.x:+.4f}")
        values[1].set_text(f"{frame.point.energy:.4f}")
    proposal = frame.proposal
    visible = proposal is not None and frame.candidate_alpha > 0
    for key in ("candidate", "connector", "candidate_label"):
        objects[key].set_visible(visible)
    if proposal is not None:
        values[2].set_text(f"{proposal.trial.x:+.4f}")
        values[3].set_text(f"{proposal.trial.energy:.4f}")
        values[4].set_text(f"{proposal.delta:+.4f}")
        color = PALETTE["accept" if proposal.accepted else "reject"]
        values[4].set_color(color)
        objects["candidate"].set_offsets([[proposal.trial.x, proposal.trial.energy]])
        objects["candidate"].set_edgecolor(color)
        objects["candidate"].set_alpha(frame.candidate_alpha)
        objects["connector"].set_data(
            [proposal.current.x, proposal.trial.x],
            [proposal.current.energy, proposal.trial.energy])
        objects["connector"].set_color(color)
        objects["connector"].set_alpha(frame.candidate_alpha*.65)
        annotation = objects["candidate_label"]
        annotation.xy = (proposal.trial.x, proposal.trial.energy)
        annotation.set_position((-75 if proposal.trial.x < proposal.current.x else 75,
                                 -65))
        annotation.set_text(f"x′  {proposal.trial.x:+.3f}\nΔE  {proposal.delta:+.3f}")
        annotation.set_color(color)
        annotation.set_alpha(frame.candidate_alpha)
    objects["decision"].set_text(frame.decision)
    objects["decision"].set_color(
        PALETTE["accept"] if frame.decision == "ACCEPT" else PALETTE["reject"])
    objects["status"].set_text(frame.status)


def print_diagnostics(data: dict, config: dict):
    print("\nGREEDY LANDSCAPE — QUANTITATIVE DIAGNOSTICS")
    for name, value in (
        ("start", data["greedy_path"][0]), ("final greedy", data["greedy_path"][-1]),
        ("local minimum", data["local_min"]),
        ("left trial", data["left_rejected_proposal"].trial),
        ("right trial", data["right_rejected_proposal"].trial),
        ("barrier", data["barrier"]), ("lower basin", data["lower_basin"]),
    ):
        print(f"{name:18s} x = {value.x:+.8f}   E = {value.energy:.8f}")
    print(f"left ΔE:  {data['left_rejected_proposal'].delta:+.8f}")
    print(f"right ΔE: {data['right_rejected_proposal'].delta:+.8f}")
    print(f"barrier height from detected minimum: {data['barrier_height']:.8f}")
    print(f"accepted moves: {len(data['moves'])}; greedy δ = {data['step']:.8f}")
    print(f"{config['duration_s']} s | {config['fps']} FPS | "
          f"{config['total_frames']} frames | 1920 × 1080")
    print(f"MP4: {Path(config['output_mp4']).resolve()}")
    print(f"PNG: {Path(config['output_png']).resolve()}")


def check_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise RuntimeError("FFmpeg is required for H.264 export; install FFmpeg.")
    result = subprocess.run([executable, "-hide_banner", "-encoders"],
                            capture_output=True, text=True, check=True)
    if "libx264" not in result.stdout:
        raise RuntimeError("This FFmpeg build does not provide libx264.")
    return executable


def validate_rendering(data, objects, config, energy_fn):
    """Audit all rendered artists and visible narrative before encoding."""
    from matplotlib.text import Text

    forbidden = ("temperature", "cooling", "thermal escape", "metropolis",
                 "p_acc", "p_accept", "annealing", "u < p", "u > p", "low-t")
    texts = objects["fig"].findobj(match=Text)
    for index, frame in enumerate(data["frames"]):
        update_frame(index, data, objects, config)
        offsets = objects["marker"].get_offsets()
        if frame.point is None:
            valid = len(offsets) == 0 and not objects["hud"].get_visible()
        else:
            valid = np.allclose(offsets, [[frame.point.x, frame.point.energy]],
                                rtol=0, atol=1e-12)
            valid &= abs(float(energy_fn(offsets[0, 0])) - offsets[0, 1]) < 1e-12
        if objects["candidate"].get_visible():
            proposal = frame.proposal
            valid &= proposal is not None and np.allclose(
                objects["candidate"].get_offsets(),
                [[proposal.trial.x, proposal.trial.energy]], rtol=0, atol=1e-12)
        visible = " ".join(t.get_text() for t in texts if t.get_visible()
                           and (t.axes is None or t.axes.get_visible())).casefold()
        valid &= not any(term in visible for term in forbidden)
        if not valid:
            raise RuntimeError(f"Rendered frame {index} violates its validated data.")
    print(f"RENDER AUDIT: {len(data['frames'])} frames PASS")


def export_animation(data, objects, config, energy_fn, preview_only=False):
    """Validate first; preserve exact dimensions and robust H.264 export."""
    import matplotlib.pyplot as plt

    validate_greedy_demonstration(data, config, energy_fn, verbose=False)
    validate_rendering(data, objects, config, energy_fn)
    fig = objects["fig"]
    if preview_only:
        update_frame(round(config["preview_time"] * config["fps"]),
                     data, objects, config)
        plt.show()
        return
    matplotlib.rcParams["animation.ffmpeg_path"] = check_ffmpeg()
    output = Path(config["output_mp4"])
    final_png = Path(config["output_png"])
    output.parent.mkdir(parents=True, exist_ok=True)
    final_png.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.stem + ".partial.mp4")
    writer = FFMpegWriter(
        fps=config["fps"], codec="libx264", bitrate=config["bitrate"],
        metadata={"title": "Energy landscape — greedy local minimum trap"},
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart", "-threads", "2"])
    start = time.monotonic()
    try:
        with writer.saving(fig, str(temporary), dpi=config["dpi"]):
            for frame in range(config["total_frames"]):
                update_frame(frame, data, objects, config)
                writer.grab_frame()
                if (frame + 1) % config["fps"] == 0:
                    print(f"Frame {frame+1:03d}/{config['total_frames']} | "
                          f"{time.monotonic()-start:.1f} s elapsed", flush=True)
        temporary.replace(output)
        update_frame(config["total_frames"] - 1, data, objects, config)
        fig.savefig(final_png, dpi=config["dpi"], facecolor=PALETTE["bg"])
    except Exception as error:
        raise RuntimeError(f"Export failed; partial output: {temporary}") from error
    finally:
        plt.close(fig)
    print(f"Export complete: {output} and {final_png}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Preview the left rejection.")
    parser.add_argument("--validate-only", action="store_true", help="Validate without rendering.")
    parser.add_argument("--self-test", action="store_true", help="Run regression tests without rendering.")
    args = parser.parse_args()
    preview_only = PREVIEW_ONLY or args.preview
    if not preview_only:
        matplotlib.use("Agg")
    energy_fn = build_energy_landscape(CONFIG)
    landscape = detect_minima(energy_fn, CONFIG["x_min"], CONFIG["x_max"])
    data = build_greedy_demonstration(CONFIG, landscape, energy_fn)
    validate_greedy_demonstration(data, CONFIG, energy_fn)
    print_diagnostics(data, CONFIG)
    if args.self_test:
        run_self_tests(data, CONFIG, landscape, energy_fn)
    if args.self_test or args.validate_only:
        return
    if not preview_only:
        check_ffmpeg()
    objects = build_figure(CONFIG, landscape, data)
    export_animation(data, objects, CONFIG, energy_fn, preview_only)


if __name__ == "__main__":
    main()
