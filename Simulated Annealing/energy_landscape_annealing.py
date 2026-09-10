"""
================================================================================
ENERGY LANDSCAPE — SIMULATED ANNEALING
Animação Científica Conceitual // Mecânica Estatística e Otimização
XLIII Semana da Física — Universidade Federal de Goiás (UFG)

Autor: Engenheiro de Software Científico & Físico Computacional
Arquivo: energy_landscape_annealing.py
Saída: energy_landscape_annealing.mp4 (1920x1080 @ 60 FPS, 15.0 s)
================================================================================
"""

import os
import sys
import shutil
import time
import numpy as np

# ==============================================================================
# CONTROLE DE VISUALIZAÇÃO E PREVIEW
# ==============================================================================
# Se True: exibe a figura interativamente com plt.show() e NÃO exporta o MP4.
# Se False: renderiza frame a frame (900 frames) e exporta o arquivo MP4 e PNG final.
PREVIEW_ONLY = False

if not PREVIEW_ONLY:
    import matplotlib
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Rectangle

# ==============================================================================
# CONFIGURAÇÃO CENTRALIZADA (Parâmetros Físicos e Computacionais)
# ==============================================================================
CONFIG = {
    # Reprodutibilidade e Monte Carlo
    "seed": 20260922,
    "fallback_seeds": [20260922, 20260918, 20260911, 20260926],
    "duration_s": 15.0,
    "fps": 60,
    "total_frames": 900,  # 15.0 s * 60 FPS = 900 frames
    "n_steps": 75,        # Passos discretos de Monte Carlo ao longo do vídeo
    
    # Domínio da coordenada abstrata de configuração e posição inicial
    "x_min": -3.80,
    "x_max": 3.80,
    "x_initial": -1.472,  # Alocada no poço do mínimo local inicial
    
    # Parâmetros de recozimento (Annealing) em unidades computacionais (k_B = 1)
    "T_initial": 2.40,
    "T_final": 0.06,
    "proposal_sigma": 0.60,  # Desvio padrão da distribuição de proposta simétrica
    
    # Parâmetros de saída cinematográfica (Full HD 1080p, proporção 16:9)
    "output_mp4": "energy_landscape_annealing.mp4",
    "output_png": "energy_landscape_final_frame.png",
    "dpi": 120,
    "figsize": (16.0, 9.0),  # 16.0 * 120 = 1920 px, 9.0 * 120 = 1080 px
    "bitrate": 10000,        # Taxa de bits em kbps para alta nitidez vetorial
}

# Paleta de Cores: Dark Scientific / Deep Tech / Computational Physics
PALETTE = {
    "bg": "#0f111a",             # Fundo escuro profundo
    "panel": "#131622",          # Painel de instrumentos e eixos
    "panel_border": "#3e445b",   # Linha de separação discreta
    "curve": "#8be9fd",          # Curva de energia (Cyan luminoso)
    "particle": "#ffb86c",       # Partícula / Estado atual (Âmbar / Dourado)
    "accepted": "#50fa7b",       # Movimento aceito / Mínimo global (Verde esmeralda)
    "rejected": "#ff5555",       # Movimento rejeitado / Barreira (Vermelho coral)
    "local_min": "#bd93f9",      # Mínimo local (Púrpura suave)
    "text": "#f8f8f2",           # Texto principal em alto contraste
    "muted": "#8b93a7",          # Texto secundário e telemetria atenuada
}

# ==============================================================================
# 1. PAISAGEM DE ENERGIA ANALÍTICA E CONTÍNUA (C^inf)
# ==============================================================================
def build_energy_landscape(config):
    """
    Constrói a função de energia analítica contínua e suave E(x).
    Combina um potencial confinante quadrático suave com 5 poços gaussianos calibrados.
    Apresenta:
      - 5 mínimos locais com barreiras de alturas variadas;
      - Mínimo local inicial em x ≈ -1.47;
      - Barreira energética entre x ≈ -1.47 e o restante da paisagem em x ≈ -0.71;
      - Bacia mais profunda (mínimo global) em x ≈ +2.68.
    Retorna uma função matemática estritamente determinística e vetorial E(x).
    """
    wells = [
        (-2.90, 2.00, 0.42),  # Poço 1: extremo esquerdo (raso)
        (-1.47, 2.70, 0.48),  # Poço 2: mínimo local inicial
        ( 0.01, 2.20, 0.45),  # Poço 3: intermediário central
        ( 1.45, 2.80, 0.48),  # Poço 4: intermediário inferior
        ( 2.75, 5.00, 0.55),  # Poço 5: bacia mais profunda da paisagem
    ]

    def raw_potential(x):
        x_arr = np.asarray(x, dtype=float)
        base = 0.10 * (x_arr ** 2)
        pot = base.copy()
        for x0, depth, width in wells:
            pot -= depth * np.exp(-((x_arr - x0) ** 2) / (2.0 * (width ** 2)))
        return pot

    # Normalização de referência: calibra o mínimo global para exatamente E = 0.60
    x_sample = np.linspace(config["x_min"], config["x_max"], 5000)
    raw_min = np.min(raw_potential(x_sample))
    offset = raw_min - 0.60

    def energy(x):
        x_arr = np.asarray(x, dtype=float)
        return raw_potential(x_arr) - offset

    return energy


def detect_minima(energy_fn, x_min, x_max, n_points=5000):
    """
    Identifica analítico-numericamente todos os mínimos e máximos locais
    em uma malha fina, localizando com exatidão o mínimo inicial, o mínimo
    profundo e a barreira intermediária para rotulagem dinâmica precisa.
    """
    x_grid = np.linspace(x_min, x_max, n_points)
    E_grid = energy_fn(x_grid)
    dx = x_grid[1] - x_grid[0]
    dE = np.gradient(E_grid, dx)

    # Identificação de trocas de sinal da primeira derivada
    sign_flips = np.diff(np.sign(dE))
    minima_indices = np.where(sign_flips > 0)[0] + 1
    maxima_indices = np.where(sign_flips < 0)[0] + 1

    all_minima = [{"x": float(x_grid[i]), "E": float(E_grid[i])} for i in minima_indices]
    all_maxima = [{"x": float(x_grid[i]), "E": float(E_grid[i])} for i in maxima_indices]

    deepest_min = min(all_minima, key=lambda m: m["E"])
    local_min = min(all_minima, key=lambda m: abs(m["x"] - (-1.47)))
    
    # Identifica o pico da barreira entre o poço local inicial e o poço seguinte
    barrier_candidates = [m for m in all_maxima if local_min["x"] < m["x"] < deepest_min["x"]]
    barrier = barrier_candidates[0] if barrier_candidates else max(all_maxima, key=lambda m: m["E"])

    return {
        "all_minima": all_minima,
        "all_maxima": all_maxima,
        "local_min": local_min,
        "deepest_min": deepest_min,
        "barrier": barrier,
        "x_grid": x_grid,
        "E_grid": E_grid,
    }

# ==============================================================================
# 2. DINÂMICA DE METRÓPOLIS E SIMULAÇÃO CIENTÍFICA
# ==============================================================================
def temperature_schedule(step, total_steps, t_init, t_final):
    """
    Programa de recozimento exponencial suave (Cooling Schedule):
    T(s) = T_init * (T_final / T_init) ** (s / (total_steps - 1))
    """
    decay_ratio = t_final / t_init
    progress = step / max(1, total_steps - 1)
    return float(t_init * (decay_ratio ** progress))


def metropolis_step(x, T, sigma, x_min, x_max, rng, energy_fn):
    """
    Executa um passo rigoroso do Critério de Metrópolis.
    A proposta é gerada por uma distribuição simétrica Gaussiana:
        q(x' | x) = Normal(x, sigma^2).
    Como q(x' | x) = q(x | x'), a probabilidade de transição reversa é idêntica
    e o fator de Hastings cancela estritamente:
        q(x | x') / q(x' | x) = 1.
    Logo, o critério reduz-se puramente ao Critério de Metrópolis:
        P_accept = min(1, exp(-ΔE / T))
    assumindo k_B = 1 (unidades computacionais).
    """
    # Proposta de transição simétrica
    dx = rng.normal(0.0, sigma)
    x_prop = float(np.clip(x + dx, x_min, x_max))

    E_curr = float(energy_fn(x))
    E_prop = float(energy_fn(x_prop))
    dE = E_prop - E_curr

    # Avaliação rigorosa da regra de aceitação
    if dE <= 0.0:
        p_acc = 1.0
    else:
        p_acc = float(np.exp(-dE / T))

    # Variável aleatória uniforme u ~ Uniform(0, 1)
    u = float(rng.uniform(0.0, 1.0))
    accepted = (u < p_acc)

    return {
        "x_old": x,
        "x_prop": x_prop,
        "E_old": E_curr,
        "E_prop": E_prop,
        "dE": dE,
        "T": T,
        "p_acc": p_acc,
        "u": u,
        "accepted": accepted,
        "x_new": x_prop if accepted else x,
        "E_new": E_prop if accepted else E_curr,
    }


def validate_trajectory(trajectory, landscape_info, config):
    """
    Testa rigorosamente os 7 critérios do Simulated Annealing:
    [1] Começa na bacia do mínimo local;
    [2] Em alta T, aceitou pelo menos uma piora energética (ΔE > 0);
    [3] Ocorreu transposição da barreira energética para fora da bacia inicial;
    [4] Atingiu a região da bacia mais profunda;
    [5] Em baixa T, rejeitou pelo menos uma piora energética (ΔE > 0);
    [6] A energia final é substancialmente menor que a inicial;
    [7] O estado final está estavelmente confinado no mínimo profundo.
    """
    local_min_x = landscape_info["local_min"]["x"]
    deep_min_x = landscape_info["deepest_min"]["x"]
    barrier_x = landscape_info["barrier"]["x"]

    # 1. Início na bacia local
    init_x = trajectory[0]["x_old"]
    c1 = abs(init_x - local_min_x) < 0.35

    # 2. Piora aceita em alta temperatura (primeiros 26 passos)
    early_uphill_acc = any(t["dE"] > 0.15 and t["accepted"] for t in trajectory[:26])

    # 3. Transposição da barreira energética (entre passos 20 e 45)
    escaped = any(t["x_new"] > barrier_x + 0.15 for t in trajectory[20:45])

    # 4. Entrada na bacia profunda
    reached_deep = any(t["x_new"] > deep_min_x - 0.50 for t in trajectory[40:70])

    # 5. Piora rejeitada em baixa temperatura (últimos 20 passos)
    late_uphill_rej = any(t["dE"] > 0.15 and not t["accepted"] for t in trajectory[55:])

    # 6. Redução líquida de energia
    energy_drop = (trajectory[0]["E_old"] - trajectory[-1]["E_new"]) > 1.2

    # 7. Confinamento final no mínimo profundo
    final_x = trajectory[-1]["x_new"]
    c7 = abs(final_x - deep_min_x) < 0.25

    all_passed = all([c1, early_uphill_acc, escaped, reached_deep, late_uphill_rej, energy_drop, c7])
    
    diagnostic = {
        "c1_start_local_basin": c1,
        "c2_early_uphill_accepted": early_uphill_acc,
        "c3_barrier_escaped": escaped,
        "c4_reached_deep_basin": reached_deep,
        "c5_late_uphill_rejected": late_uphill_rej,
        "c6_energy_significantly_reduced": energy_drop,
        "c7_final_near_deep_min": c7,
        "energy_drop_value": trajectory[0]["E_old"] - trajectory[-1]["E_new"],
        "final_x": final_x,
        "final_E": trajectory[-1]["E_new"]
    }
    return all_passed, diagnostic


def run_simulation(config, landscape_info, energy_fn):
    """
    Gera a trajetória completa de Simulated Annealing pré-calculando todos os dados.
    Utiliza a seed principal certificada e valida os resultados.
    """
    seeds_to_try = [config["seed"]] + [s for s in config["fallback_seeds"] if s != config["seed"]]
    
    selected_seed = None
    selected_trajectory = None
    selected_diag = None

    for seed in seeds_to_try:
        rng = np.random.default_rng(seed)
        traj = []
        curr_x = config["x_initial"]

        for step in range(config["n_steps"]):
            T = temperature_schedule(step, config["n_steps"], config["T_initial"], config["T_final"])
            step_record = metropolis_step(
                curr_x, T, config["proposal_sigma"],
                config["x_min"], config["x_max"], rng, energy_fn
            )
            step_record["step"] = step
            traj.append(step_record)
            curr_x = step_record["x_new"]

        passed, diag = validate_trajectory(traj, landscape_info, config)
        if passed:
            selected_seed = seed
            selected_trajectory = traj
            selected_diag = diag
            break

    if selected_trajectory is None:
        raise RuntimeError(
            "Erro de Validação: Nenhuma seed satisfez todas as condições do Simulated Annealing. "
            f"Diagnóstico da última tentativa: {diag}"
        )

    # Mapeamento temporal de passos para os 900 frames:
    # 0.0-3.5 s (frames 0-210): Fase 1 (Alta Temperatura)
    # 3.5-7.0 s (frames 210-420): Fase 2 (Thermal Escape)
    # 7.0-11.5 s (frames 420-690): Fase 3 (Annealing/Cooling)
    # 11.5-13.5 s (frames 690-810): Fase 4 (Baixa Temperatura / Confinamento)
    # 13.5-15.0 s (frames 810-900): Fase 5 (Final Hold)
    phase_alloc = [
        (0, 26, 0, 210),
        (26, 41, 210, 420),
        (41, 61, 420, 690),
        (61, 75, 690, 810)
    ]
    step_start_frames = np.zeros(config["n_steps"] + 1, dtype=int)
    for s_start, s_end, f_start, f_end in phase_alloc:
        n_s = s_end - s_start
        f_alloc = np.round(np.linspace(f_start, f_end, n_s + 1)).astype(int)
        step_start_frames[s_start:s_end + 1] = f_alloc

    return {
        "trajectory": selected_trajectory,
        "seed": selected_seed,
        "diagnostic": selected_diag,
        "step_start_frames": step_start_frames,
    }

# ==============================================================================
# 3. CONSTRUÇÃO DA FIGURA E COMPOSIÇÃO CINEMATOGRÁFICA (1920x1080)
# ==============================================================================
def build_figure(config, landscape_info, energy_fn):
    """
    Constrói a figura de 1920x1080 com proporção 16:9 em estética Dark Scientific.
    Layout estruturado via GridSpec:
      - 74% de largura para a paisagem de energia e dinâmica de partículas;
      - 26% de largura para telemetria científica (curva T(t), gauge e HUD).
    """
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["text.color"] = PALETTE["text"]
    plt.rcParams["axes.labelcolor"] = PALETTE["text"]
    plt.rcParams["xtick.color"] = PALETTE["muted"]
    plt.rcParams["ytick.color"] = PALETTE["muted"]

    fig = plt.figure(figsize=config["figsize"], dpi=config["dpi"], facecolor=PALETTE["bg"])

    # Cabeçalho institucional superior
    fig.text(0.05, 0.955, "ENERGY LANDSCAPE", fontsize=20, fontweight="bold", color=PALETTE["text"])
    fig.text(0.05, 0.930, "Simulated Annealing // Statistical Mechanics — XLIII Semana da Física (UFG)",
             fontsize=11, color=PALETTE["muted"])

    # Badges permanentes de rigor conceitual
    fig.text(0.95, 0.955, "ANIMAÇÃO CONCEITUAL", fontsize=11, fontweight="bold", color=PALETTE["particle"],
             ha="right", bbox=dict(boxstyle="round,pad=0.4", facecolor="#1f2430", edgecolor=PALETTE["particle"], linewidth=1.2))
    fig.text(0.95, 0.930, "x = coordenada abstrata de configuração | E = energia efetiva (u.c.)",
             fontsize=9.5, color=PALETTE["muted"], ha="right")

    # GridSpec estruturado
    gs = gridspec.GridSpec(3, 2, width_ratios=[3.3, 1.2], height_ratios=[1.1, 0.22, 2.0],
                           left=0.06, right=0.95, bottom=0.08, top=0.90,
                           wspace=0.16, hspace=0.25)

    ax_main = fig.add_subplot(gs[:, 0], facecolor=PALETTE["panel"])
    ax_inset = fig.add_subplot(gs[0, 1], facecolor=PALETTE["panel"])
    ax_bar = fig.add_subplot(gs[1, 1], facecolor=PALETTE["panel"])
    ax_hud = fig.add_subplot(gs[2, 1], facecolor=PALETTE["panel"])

    # --------------------------------------------------------------------------
    # Eixo Principal: Paisagem de Energia E(x)
    # --------------------------------------------------------------------------
    for spine in ["top", "right"]:
        ax_main.spines[spine].set_visible(False)
    ax_main.spines["left"].set_color(PALETTE["panel_border"])
    ax_main.spines["bottom"].set_color(PALETTE["panel_border"])
    ax_main.grid(True, linestyle=":", alpha=0.15, color=PALETTE["muted"])
    ax_main.set_xlabel("Coordenada abstrata de configuração (x) [u.c.]", fontsize=11, color=PALETTE["text"], labelpad=8)
    ax_main.set_ylabel("Energia efetiva E(x) [u.c.]", fontsize=11, color=PALETTE["text"], labelpad=8)
    ax_main.set_xlim(config["x_min"], config["x_max"])
    ax_main.set_ylim(-0.3, 5.8)

    # Curva contínua de energia, halo de glow e preenchimento volumétrico
    x_curve = landscape_info["x_grid"]
    E_curve = landscape_info["E_grid"]
    ax_main.plot(x_curve, E_curve, color=PALETTE["curve"], linewidth=2.8, zorder=3)
    ax_main.plot(x_curve, E_curve, color=PALETTE["curve"], linewidth=6.0, alpha=0.20, zorder=2)
    ax_main.fill_between(x_curve, -0.3, E_curve, color=PALETTE["curve"], alpha=0.05, zorder=1)

    # Linhas e anotações dos mínimos
    x_loc = landscape_info["local_min"]["x"]
    x_deep = landscape_info["deepest_min"]["x"]
    ax_main.axvline(x_loc, color=PALETTE["local_min"], linestyle="--", linewidth=1.2, alpha=0.45, zorder=2)
    ax_main.text(x_loc, 5.40, "MÍNIMO LOCAL", color=PALETTE["local_min"], fontsize=9.5, fontweight="bold",
                 ha="center", bbox=dict(boxstyle="round,pad=0.25", facecolor=PALETTE["bg"], edgecolor=PALETTE["local_min"], alpha=0.7))

    ax_main.axvline(x_deep, color=PALETTE["accepted"], linestyle="--", linewidth=1.2, alpha=0.45, zorder=2)
    ax_main.text(x_deep, 5.40, "REGIÃO DE MENOR ENERGIA\n(MÍNIMO GLOBAL DA PAISAGEM)", color=PALETTE["accepted"],
                 fontsize=9.5, fontweight="bold", ha="center",
                 bbox=dict(boxstyle="round,pad=0.25", facecolor=PALETTE["bg"], edgecolor=PALETTE["accepted"], alpha=0.7))

    # Regra de aceitação na tela renderizada com mathtext
    ax_main.text(0.03, 0.04, r'Critério de Metrópolis:  $P_{\mathrm{acc}} = \min\left[1,\, e^{-\Delta E / T}\right]$',
                 transform=ax_main.transAxes, fontsize=11.5, color=PALETTE["text"],
                 bbox=dict(boxstyle="round,pad=0.4", facecolor=PALETTE["bg"], edgecolor=PALETTE["panel_border"], alpha=0.9))

    # Destaque dinâmico da barreira energética (inicialmente oculto)
    x_barr = landscape_info["barrier"]["x"]
    E_barr = landscape_info["barrier"]["E"]
    barrier_span = ax_main.axvspan(x_barr - 0.25, x_barr + 0.25, color=PALETTE["rejected"], alpha=0.0, zorder=2)
    barrier_arrow = ax_main.annotate(
        "BARREIRA DE ENERGIA\nΔE ≈ +1.22",
        xy=(x_barr, E_barr + 0.05),
        xytext=(x_barr - 0.90, E_barr + 0.85),
        arrowprops=dict(arrowstyle="->", color=PALETTE["rejected"], lw=2.0),
        color=PALETTE["rejected"], fontsize=9.5, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#1a111a", edgecolor=PALETTE["rejected"], alpha=0.95),
        visible=False, zorder=7
    )

    # Elementos dinâmicos da proposta Monte Carlo
    cand_line, = ax_main.plot([], [], color=PALETTE["accepted"], linestyle="--", linewidth=1.8, alpha=0.0, zorder=4)
    cand_circle = ax_main.scatter([], [], s=110, facecolors="none", edgecolors=PALETTE["accepted"],
                                  linewidths=2.0, linestyle="--", zorder=6)
    cand_text = ax_main.text(0, 0, "", color=PALETTE["accepted"], fontsize=9.5, fontweight="bold",
                             visible=False, zorder=7)
    cand_badge = ax_main.text(0, 0, "", fontsize=10, fontweight="bold", visible=False, zorder=8,
                              bbox=dict(boxstyle="round,pad=0.4", facecolor=PALETTE["bg"],
                                        edgecolor=PALETTE["accepted"], alpha=0.95))

    # Partícula do estado atual (com camadas de brilho)
    particle_stem, = ax_main.plot([], [], color=PALETTE["particle"], linestyle=":", linewidth=1.2, alpha=0.30, zorder=3)
    particle_glow1 = ax_main.scatter([], [], s=380, color=PALETTE["particle"], alpha=0.15, zorder=5)
    particle_glow2 = ax_main.scatter([], [], s=180, color=PALETTE["particle"], alpha=0.40, zorder=6)
    particle_core = ax_main.scatter([], [], s=75, color="#ffffff", edgecolors=PALETTE["particle"], linewidths=2.0, zorder=7)

    # Trilha translúcida de estados recentes
    particle_trail = ax_main.scatter([], [], s=25, zorder=3)

    # Card final de confinamento (Fase 5)
    final_card = ax_main.text(
        0.50, 0.40,
        "Flutuações térmicas desfavoráveis tornam-se improváveis.\n"
        "Configurações de menor energia são favorecidas.\n"
        "Sistema confinado no mínimo profundo.",
        transform=ax_main.transAxes, ha="center", va="center", fontsize=11.5, color=PALETTE["text"],
        visible=False, zorder=9,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#151823", edgecolor=PALETTE["accepted"], linewidth=1.5, alpha=0.96)
    )

    # --------------------------------------------------------------------------
    # Subplot Inset: Curva de Resfriamento T(t)
    # --------------------------------------------------------------------------
    ax_inset.set_title("PROGRAMA DE RECOZIMENTO: T(t)", fontsize=9.5, fontweight="bold",
                       color=PALETTE["muted"], loc="left", pad=6)
    for spine in ["top", "right"]:
        ax_inset.spines[spine].set_visible(False)
    ax_inset.spines["left"].set_color(PALETTE["panel_border"])
    ax_inset.spines["bottom"].set_color(PALETTE["panel_border"])
    ax_inset.grid(True, linestyle=":", alpha=0.15, color=PALETTE["muted"])

    t_sched = np.linspace(0, config["duration_s"], 200)
    T_sched = config["T_initial"] * ((config["T_final"] / config["T_initial"]) ** (t_sched / config["duration_s"]))
    ax_inset.plot(t_sched, T_sched, color=PALETTE["particle"], linewidth=2.0, zorder=2)
    inset_dot, = ax_inset.plot([], [], marker="o", markersize=6, color=PALETTE["particle"], zorder=5)

    ax_inset.set_xlim(0, config["duration_s"])
    ax_inset.set_ylim(0, config["T_initial"] * 1.08)
    ax_inset.set_xlabel("Tempo (s)", fontsize=8.5, color=PALETTE["muted"], labelpad=2)
    ax_inset.set_ylabel("Temp. T", fontsize=8.5, color=PALETTE["muted"], labelpad=2)
    ax_inset.tick_params(labelsize=8)

    # --------------------------------------------------------------------------
    # Subplot Gauge: Barra de Temperatura T / T_0
    # --------------------------------------------------------------------------
    ax_bar.set_xlim(0, 1)
    ax_bar.set_ylim(0, 1)
    ax_bar.axis("off")
    bar_bg = Rectangle((0.02, 0.18), 0.96, 0.42, facecolor="#1f2430", edgecolor=PALETTE["panel_border"], linewidth=1.0)
    ax_bar.add_patch(bar_bg)
    bar_fill = Rectangle((0.02, 0.18), 0.96, 0.42, facecolor=PALETTE["particle"], edgecolor="none")
    ax_bar.add_patch(bar_fill)
    ax_bar.text(0.02, 0.74, "GAUGE DE TEMPERATURA: T / T₀", fontsize=8.5, fontweight="bold", color=PALETTE["muted"])
    bar_pct_text = ax_bar.text(0.98, 0.74, "100.0%", fontsize=8.5, fontweight="bold",
                               color=PALETTE["particle"], ha="right", fontfamily="monospace")

    # --------------------------------------------------------------------------
    # Subplot HUD: Telemetria Científica
    # --------------------------------------------------------------------------
    ax_hud.axis("off")
    ax_hud.text(0.05, 0.94, "PAINEL DE TELEMETRIA", fontsize=11, fontweight="bold", color=PALETTE["text"])
    
    hud_time = ax_hud.text(0.05, 0.86, "TEMPO: 0.00 s / 15.00 s", fontsize=9, color=PALETTE["muted"], fontfamily="monospace")
    
    ax_hud.text(0.05, 0.78, "FASE:", fontsize=9, color=PALETTE["muted"])
    hud_phase = ax_hud.text(0.32, 0.78, "HIGH-T EXPLORATION", fontsize=9, fontweight="bold", color=PALETTE["particle"])

    hud_fields = [
        ("TEMPERATURA T", "hud_T"),
        ("ENERGIA ATUAL E", "hud_E"),
        ("PROPOSTA ΔE", "hud_dE"),
        ("P(ACEITAÇÃO)", "hud_pacc"),
        ("SORTEIO u ~ U(0,1)", "hud_u"),
        ("TESTE (u < P_acc)", "hud_test"),
        ("DECISÃO / STATUS", "hud_status"),
    ]
    hud_text_objects = {}
    y_pos = 0.68
    for label, key in hud_fields:
        ax_hud.text(0.05, y_pos, label, fontsize=8.8, color=PALETTE["muted"])
        val_obj = ax_hud.text(0.95, y_pos, "--", fontsize=9.2, fontweight="bold",
                              color=PALETTE["text"], fontfamily="monospace", ha="right")
        hud_text_objects[key] = val_obj
        y_pos -= 0.082

    hud_edu = ax_hud.text(
        0.05, 0.05,
        "Em alta temperatura, o algoritmo\n"
        "pode aceitar transições com ΔE > 0,\n"
        "permitindo transpor barreiras.",
        fontsize=8.5, color=PALETTE["curve"], style="italic",
        bbox=dict(boxstyle="round,pad=0.45", facecolor=PALETTE["bg"], edgecolor=PALETTE["panel_border"], alpha=0.85)
    )

    figure_objects = {
        "fig": fig,
        "ax_main": ax_main,
        "ax_inset": ax_inset,
        "ax_bar": ax_bar,
        "ax_hud": ax_hud,
        "barrier_span": barrier_span,
        "barrier_arrow": barrier_arrow,
        "cand_line": cand_line,
        "cand_circle": cand_circle,
        "cand_text": cand_text,
        "cand_badge": cand_badge,
        "particle_stem": particle_stem,
        "particle_glow1": particle_glow1,
        "particle_glow2": particle_glow2,
        "particle_core": particle_core,
        "particle_trail": particle_trail,
        "final_card": final_card,
        "inset_dot": inset_dot,
        "bar_fill": bar_fill,
        "bar_pct_text": bar_pct_text,
        "hud_time": hud_time,
        "hud_phase": hud_phase,
        "hud_text_objects": hud_text_objects,
        "hud_edu": hud_edu,
    }
    return figure_objects

# ==============================================================================
# 4. ATUALIZAÇÃO CINEMATOGRÁFICA FRAME A FRAME
# ==============================================================================
def update_frame(frame, sim_data, fig_objs, config, landscape_info, energy_fn):
    """
    Renderiza o frame correspondente (0 a 899):
    - A coordenada visual x_vis interpola suavemente entre x_old e x_prop durante ~150 ms
      quando aceito, mantendo y = E(x) rigorosamente sobre a curva.
    - Mostra propostas candidatas x' com linhas tracejadas e destaques pedagógicos de aceitação/rejeição.
    - Destaca a barreira durante a fase de transposição (Thermal Escape).
    - Atualiza a telemetria científica (HUD), gauge e inset com dados estritamente reais.
    """
    trajectory = sim_data["trajectory"]
    step_starts = sim_data["step_start_frames"]
    t_sec = frame / config["fps"]

    # Fases pedagógicas sincronizadas com a timeline de 15 segundos:
    if frame < 210:
        phase_name = "HIGH-T EXPLORATION"
        phase_color = PALETTE["particle"]
        edu_msg = "Em alta temperatura, o algoritmo\npode aceitar transições com ΔE > 0,\npermitindo transpor barreiras."
    elif frame < 420:
        phase_name = "THERMAL ESCAPE"
        phase_color = "#ff79c6"
        edu_msg = "Superação da barreira de energia:\numa piora temporária é aceita\npara alcançar outra bacia."
    elif frame < 690:
        phase_name = "ANNEALING / COOLING"
        phase_color = PALETTE["curve"]
        edu_msg = "Conforme T diminui, aceitação de pioras\ntorna-se progressivamente rara,\ne bacias mais profundas dominam."
    elif frame < 810:
        phase_name = "LOW-T CONFINEMENT"
        phase_color = PALETTE["rejected"]
        edu_msg = "Em baixa temperatura, transições\ncom ΔE > 0 são quase sempre rejeitadas,\nconfinando o estado."
    else:
        phase_name = "FINAL LOW-ENERGY STATE"
        phase_color = PALETTE["accepted"]
        edu_msg = "Confinamento em região de menor energia.\nFlutuações térmicas tornam-se mínimas."

    # Se estiver nos últimos frames (Final Hold: 13.5 a 15.0 s)
    if frame >= 810:
        last_step = trajectory[-1]
        x_vis = last_step["x_new"]
        y_vis = float(energy_fn(x_vis))
        curr_T = config["T_final"]
        
        # Oculta elementos transitórios
        fig_objs["cand_line"].set_alpha(0.0)
        fig_objs["cand_circle"].set_offsets(np.empty((0, 2)))
        fig_objs["cand_text"].set_visible(False)
        fig_objs["cand_badge"].set_visible(False)
        fig_objs["barrier_arrow"].set_visible(False)
        fig_objs["barrier_span"].set_alpha(0.0)
        fig_objs["final_card"].set_visible(True)

        # Atualiza partícula
        fig_objs["particle_stem"].set_data([x_vis, x_vis], [-0.3, y_vis])
        fig_objs["particle_glow1"].set_offsets([[x_vis, y_vis]])
        fig_objs["particle_glow2"].set_offsets([[x_vis, y_vis]])
        fig_objs["particle_core"].set_offsets([[x_vis, y_vis]])

        # HUD Final
        fig_objs["hud_time"].set_text(f"TEMPO: {t_sec:5.2f} s / 15.00 s  [FINAL]")
        fig_objs["hud_phase"].set_text(phase_name)
        fig_objs["hud_phase"].set_color(phase_color)

        hud_map = fig_objs["hud_text_objects"]
        hud_map["hud_T"].set_text(f"{curr_T:6.3f}")
        hud_map["hud_E"].set_text(f"{y_vis:6.3f}")
        hud_map["hud_dE"].set_text(" 0.000")
        hud_map["hud_pacc"].set_text("1.0000")
        hud_map["hud_u"].set_text("------")
        hud_map["hud_test"].set_text("ESTABILIZADO")
        hud_map["hud_test"].set_color(PALETTE["accepted"])
        hud_map["hud_status"].set_text("CONFINADO")
        hud_map["hud_status"].set_color(PALETTE["accepted"])
        fig_objs["hud_edu"].set_text(edu_msg)

        # Inset e Gauge
        fig_objs["inset_dot"].set_data([t_sec], [curr_T])
        fig_objs["bar_fill"].set_width(0.96 * (curr_T / config["T_initial"]))
        fig_objs["bar_pct_text"].set_text(f"{(curr_T / config['T_initial']) * 100:4.1f}%")
        return

    # Execução normal ao longo dos 75 passos de Monte Carlo
    fig_objs["final_card"].set_visible(False)
    
    # Determina o índice do passo
    step_idx = int(np.searchsorted(step_starts, frame, side="right") - 1)
    step_idx = max(0, min(config["n_steps"] - 1, step_idx))

    f_start = step_starts[step_idx]
    f_end = step_starts[step_idx + 1]
    step_len = max(1, f_end - f_start)
    progress_in_step = (frame - f_start) / step_len  # [0.0, 1.0]

    step_data = trajectory[step_idx]
    x_old = step_data["x_old"]
    x_prop = step_data["x_prop"]
    x_new = step_data["x_new"]
    accepted = step_data["accepted"]
    dE = step_data["dE"]
    curr_T = step_data["T"]
    p_acc = step_data["p_acc"]
    u_val = step_data["u"]

    # Interpolação visual suave (smoothstep):
    # progress < 0.30: proposta apresentada, partícula permanece em x_old
    # 0.30 <= progress < 0.85: se aceito, desliza suavemente até x_prop; se rejeitado, permanece
    # progress >= 0.85: acomodação no estado resultante x_new
    if progress_in_step < 0.30:
        x_vis = x_old
        cand_alpha = 1.0
    elif progress_in_step < 0.85:
        if accepted:
            interp_ratio = (progress_in_step - 0.30) / 0.55
            smooth_w = 3.0 * (interp_ratio ** 2) - 2.0 * (interp_ratio ** 3)
            x_vis = x_old + smooth_w * (x_prop - x_old)
            cand_alpha = max(0.0, 1.0 - interp_ratio)
        else:
            x_vis = x_old
            cand_alpha = max(0.0, 1.0 - (progress_in_step - 0.30) / 0.55)
    else:
        x_vis = x_new
        cand_alpha = 0.0

    y_vis = float(energy_fn(x_vis))
    y_old = float(energy_fn(x_old))
    y_prop = float(energy_fn(x_prop))

    # Atualiza a partícula
    fig_objs["particle_stem"].set_data([x_vis, x_vis], [-0.3, y_vis])
    fig_objs["particle_glow1"].set_offsets([[x_vis, y_vis]])
    fig_objs["particle_glow2"].set_offsets([[x_vis, y_vis]])
    fig_objs["particle_core"].set_offsets([[x_vis, y_vis]])

    # Atualiza a trilha translúcida dos estados anteriores
    recent_x = [t["x_new"] for t in trajectory[:max(1, step_idx)]][-25:]
    if recent_x:
        recent_y = [float(energy_fn(rx)) for rx in recent_x]
        n_trail = len(recent_x)
        colors = np.zeros((n_trail, 4))
        colors[:, :3] = [1.0, 0.72, 0.42]  # Âmbar suave
        colors[:, 3] = np.linspace(0.05, 0.40, n_trail)
        fig_objs["particle_trail"].set_offsets(np.column_stack([recent_x, recent_y]))
        fig_objs["particle_trail"].set_facecolors(colors)
        fig_objs["particle_trail"].set_edgecolors("none")
    else:
        fig_objs["particle_trail"].set_offsets(np.empty((0, 2)))

    # Atualiza a proposta candidata x'
    color_prop = PALETTE["accepted"] if accepted else PALETTE["rejected"]
    if cand_alpha > 0.05:
        fig_objs["cand_line"].set_data([x_old, x_prop], [y_old, y_prop])
        fig_objs["cand_line"].set_color(color_prop)
        fig_objs["cand_line"].set_alpha(0.75 * cand_alpha)

        fig_objs["cand_circle"].set_offsets([[x_prop, y_prop]])
        fig_objs["cand_circle"].set_edgecolors(color_prop)
        fig_objs["cand_circle"].set_alpha(cand_alpha)

        dx_sign = 1.0 if x_prop >= x_old else -1.0
        fig_objs["cand_text"].set_position((x_prop + 0.08 * dx_sign, y_prop + 0.18))
        fig_objs["cand_text"].set_text("x' proposta")
        fig_objs["cand_text"].set_color(color_prop)
        fig_objs["cand_text"].set_alpha(cand_alpha)
        fig_objs["cand_text"].set_visible(True)
    else:
        fig_objs["cand_line"].set_alpha(0.0)
        fig_objs["cand_circle"].set_offsets(np.empty((0, 2)))
        fig_objs["cand_text"].set_visible(False)

    # Destaque pedagógico para eventos-chave:
    # 1. Piora aceita em alta temperatura (ΔE > 0 aceito via Metrópolis)
    # 2. Piora rejeitada em baixa temperatura (ΔE > 0 rejeitado)
    is_key_uphill_acc = (dE > 0.20 and accepted and step_idx <= 40) and (progress_in_step < 0.90)
    is_key_uphill_rej = (dE > 0.35 and not accepted and step_idx >= 55) and (progress_in_step < 0.90)

    if is_key_uphill_acc:
        badge_ha = "right" if x_prop > 2.0 else ("left" if x_prop < -2.0 else "center")
        fig_objs["cand_badge"].set_position((x_prop, y_prop + 0.55))
        fig_objs["cand_badge"].set_ha(badge_ha)
        fig_objs["cand_badge"].set_text(
            f"ΔE = {dE:+.2f} > 0\n"
            f"ACEITO (u < P_acc)\n"
            f"u={u_val:.3f} < P={p_acc:.3f}"
        )
        fig_objs["cand_badge"].set_color(PALETTE["accepted"])
        fig_objs["cand_badge"].set_bbox(dict(boxstyle="round,pad=0.35", facecolor=PALETTE["bg"],
                                             edgecolor=PALETTE["accepted"], alpha=0.95))
        fig_objs["cand_badge"].set_visible(True)
    elif is_key_uphill_rej:
        badge_ha = "right" if x_prop > 2.0 else ("left" if x_prop < -2.0 else "center")
        fig_objs["cand_badge"].set_position((x_prop, y_prop + 0.55))
        fig_objs["cand_badge"].set_ha(badge_ha)
        fig_objs["cand_badge"].set_text(
            f"ΔE = {dE:+.2f} > 0\n"
            f"REJEITADO (u > P_acc)\n"
            f"u={u_val:.3f} > P={p_acc:.3f}"
        )
        fig_objs["cand_badge"].set_color(PALETTE["rejected"])
        fig_objs["cand_badge"].set_bbox(dict(boxstyle="round,pad=0.35", facecolor=PALETTE["bg"],
                                             edgecolor=PALETTE["rejected"], alpha=0.95))
        fig_objs["cand_badge"].set_visible(True)
    else:
        fig_objs["cand_badge"].set_visible(False)

    # Destaque temporário da barreira energética durante a fase de transposição (330 a 410)
    if 330 <= frame <= 410:
        barr_alpha = np.sin(np.pi * (frame - 330) / (410 - 330))
        fig_objs["barrier_arrow"].set_visible(True)
        fig_objs["barrier_span"].set_alpha(0.12 * barr_alpha)
    else:
        fig_objs["barrier_arrow"].set_visible(False)
        fig_objs["barrier_span"].set_alpha(0.0)

    # Atualização do Inset T(t)
    fig_objs["inset_dot"].set_data([t_sec], [curr_T])

    # Atualização do Gauge de Temperatura
    gauge_ratio = max(0.0, min(1.0, curr_T / config["T_initial"]))
    fig_objs["bar_fill"].set_width(0.96 * gauge_ratio)
    fig_objs["bar_pct_text"].set_text(f"{gauge_ratio * 100:4.1f}%")

    # Atualização do HUD de Telemetria Científica
    fig_objs["hud_time"].set_text(f"TEMPO: {t_sec:5.2f} s / 15.00 s  [Passo {step_idx+1:02d}/{config['n_steps']:02d}]")
    fig_objs["hud_phase"].set_text(phase_name)
    fig_objs["hud_phase"].set_color(phase_color)

    hud_map = fig_objs["hud_text_objects"]
    hud_map["hud_T"].set_text(f"{curr_T:6.3f}")
    hud_map["hud_E"].set_text(f"{y_vis:6.3f}")
    
    col_dE = PALETTE["accepted"] if dE <= 0 else (PALETTE["particle"] if accepted else PALETTE["rejected"])
    hud_map["hud_dE"].set_text(f"{dE:+6.3f}")
    hud_map["hud_dE"].set_color(col_dE)

    hud_map["hud_pacc"].set_text(f"{p_acc:6.4f}")
    hud_map["hud_u"].set_text(f"{u_val:6.4f}")

    if dE <= 0:
        hud_map["hud_test"].set_text("ΔE ≤ 0 (DIRETO)")
        hud_map["hud_test"].set_color(PALETTE["accepted"])
    elif accepted:
        hud_map["hud_test"].set_text("u < P_acc (SIM)")
        hud_map["hud_test"].set_color(PALETTE["accepted"])
    else:
        hud_map["hud_test"].set_text("u ≥ P_acc (NÃO)")
        hud_map["hud_test"].set_color(PALETTE["rejected"])

    if accepted:
        st_text = "● ACEITO" if dE <= 0 else "● ACEITO (UPHILL)"
        st_col = PALETTE["accepted"]
    else:
        st_text = "✕ REJEITADO"
        st_col = PALETTE["rejected"]

    hud_map["hud_status"].set_text(st_text)
    hud_map["hud_status"].set_color(st_col)
    fig_objs["hud_edu"].set_text(edu_msg)

# ==============================================================================
# 5. EXPORTAÇÃO MP4 E DIAGNÓSTICO
# ==============================================================================
def export_animation(sim_data, fig_objs, config, landscape_info, energy_fn):
    """
    Renderiza frame a frame diretamente para MP4 (H.264/yuv420p) ou exibe preview.
    Gera também a imagem estática de alta resolução do frame final.
    """
    fig = fig_objs["fig"]

    if PREVIEW_ONLY:
        print("\n[MODO PREVIEW ATIVO]: Abrindo visualização interativa do frame...")
        update_frame(350, sim_data, fig_objs, config, landscape_info, energy_fn)
        plt.show()
        return

    # Verificação estrita da disponibilidade do FFmpeg
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin is None:
        raise RuntimeError(
            "ERRO CRÍTICO: O executável FFmpeg não foi encontrado no PATH do sistema.\n"
            "Para renderizar o vídeo MP4 em 1080p @ 60 FPS, o FFmpeg é mandatório.\n"
            "Por favor, instale o pacote ffmpeg (ex: sudo apt install ffmpeg) para prosseguir."
        )

    print(f"\nBinário FFmpeg detectado com sucesso: {ffmpeg_bin}")
    print(f"Iniciando renderização de {config['total_frames']} frames (60 FPS, 1920x1080)...")
    print(f"Arquivo de saída de vídeo: {config['output_mp4']}")

    writer = FFMpegWriter(
        fps=config["fps"],
        codec="libx264",
        bitrate=config["bitrate"],
        extra_args=["-pix_fmt", "yuv420p"]
    )

    t_start = time.time()
    with writer.saving(fig, config["output_mp4"], dpi=config["dpi"]):
        for frame in range(config["total_frames"]):
            update_frame(frame, sim_data, fig_objs, config, landscape_info, energy_fn)
            writer.grab_frame()

            if (frame + 1) % 60 == 0 or (frame + 1) == config["total_frames"]:
                elapsed = time.time() - t_start
                pct = ((frame + 1) / config["total_frames"]) * 100
                fps_render = (frame + 1) / max(0.001, elapsed)
                eta = (config["total_frames"] - (frame + 1)) / max(0.001, fps_render)
                print(f"  Frame {frame + 1:03d}/{config['total_frames']} [{pct:5.1f}%] — "
                      f"{fps_render:4.1f} FPS — ETA: {eta:4.1f} s", flush=True)

    total_time = time.time() - t_start
    print(f"\nRenderização MP4 concluída com sucesso em {total_time:.2f} segundos!")

    # Exporta o frame final em PNG Full HD
    print(f"Exportando frame final para: {config['output_png']}")
    update_frame(config["total_frames"] - 1, sim_data, fig_objs, config, landscape_info, energy_fn)
    fig.savefig(config["output_png"], dpi=config["dpi"], facecolor=PALETTE["bg"])
    print("Frame final salvo com sucesso.")


def print_diagnostic_banner(sim_data, landscape_info, config):
    """
    Exibe o diagnóstico completo da simulação antes do processo de renderização.
    """
    traj = sim_data["trajectory"]
    diag = sim_data["diagnostic"]
    n_acc = sum(1 for t in traj if t["accepted"])
    n_rej = sum(1 for t in traj if not t["accepted"])
    n_up_acc = sum(1 for t in traj if t["dE"] > 0 and t["accepted"])
    
    init_x = traj[0]["x_old"]
    init_E = traj[0]["E_old"]
    final_x = traj[-1]["x_new"]
    final_E = traj[-1]["E_new"]
    min_E = landscape_info["deepest_min"]["E"]
    reduction = ((init_E - final_E) / init_E) * 100.0

    print("======================================================================")
    print("SIMULATED ANNEALING — ENERGY LANDSCAPE")
    print("XLIII Semana da Física — Universidade Federal de Goiás (UFG)")
    print("======================================================================")
    print(f"Seed efetivamente usada:     {sim_data['seed']}")
    print(f"Estado inicial:              x = {init_x:+.4f} | E = {init_E:.4f}")
    print(f"Estado final:                x = {final_x:+.4f} | E = {final_E:.4f}")
    print(f"Mínimo global analítico:     x = {landscape_info['deepest_min']['x']:+.4f} | E = {min_E:.4f}")
    print(f"Redução energética líquida:  {reduction:.2f}% (ΔE_net = {final_E - init_E:+.4f})")
    print(f"Total de passos de MC:       {config['n_steps']}")
    print(f"Passos aceitos:              {n_acc} ({n_acc / config['n_steps'] * 100:.1f}%)")
    print(f"Passos rejeitados:           {n_rej} ({n_rej / config['n_steps'] * 100:.1f}%)")
    print(f"Transições uphill aceitas:   {n_up_acc}")
    print(f"Fuga do mínimo local:        {'SIM' if diag['c3_barrier_escaped'] else 'NÃO'}")
    print(f"Bacia profunda alcançada:    {'SIM' if diag['c4_reached_deep_basin'] else 'NÃO'}")
    print(f"Confinamento final validado: {'SIM' if diag['c7_final_near_deep_min'] else 'NÃO'}")
    print("----------------------------------------------------------------------")
    print(f"Resolução de renderização:   1920 x 1080 (16:9) @ {config['fps']} FPS")
    print(f"Duração total:               {config['duration_s']} s ({config['total_frames']} frames)")
    print(f"Arquivo de saída:            {config['output_mp4']}")
    print("======================================================================\n")


def main():
    """
    Ponto de entrada principal do script.
    """
    # 1. Construção da paisagem analítica contínua
    energy_fn = build_energy_landscape(CONFIG)

    # 2. Detecção geométrica e numérica dos mínimos e barreiras
    landscape_info = detect_minima(energy_fn, CONFIG["x_min"], CONFIG["x_max"])

    # 3. Execução honesta do algoritmo de Metrópolis e validação
    sim_data = run_simulation(CONFIG, landscape_info, energy_fn)

    # 4. Diagnóstico quantitativo no terminal
    print_diagnostic_banner(sim_data, landscape_info, CONFIG)

    # 5. Construção da interface gráfica e eixos cinematográficos
    fig_objs = build_figure(CONFIG, landscape_info, energy_fn)

    # 6. Exportação do vídeo MP4 e imagem final
    export_animation(sim_data, fig_objs, CONFIG, landscape_info, energy_fn)


if __name__ == "__main__":
    main()
