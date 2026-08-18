#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SIMULAÇÃO DE TENSÃO ENTRÓPICA EM UM POLÍMERO (MODELO FJC 1D)
===============================================================================
Autores: Físico Computacional & Engenheiro de Software
Descrição:
    Este script simula e visualiza a elasticidade entrópica de uma cadeia polimérica
    unidimensional ideal (Freely Jointed Chain - FJC) com N elos de comprimento l.
    
    A elasticidade da borracha e polímeros biológicos (como DNA e titina) não decorre
    de forças de atração/repulsão atômicas (energia potencial interna U ~ 0), mas
    sim da Segunda Lei da Termodinâmica: o estado esticado possui drasticamente menos
    microestados (menor entropia S), gerando uma força de restauração puramente entrópica.

Conceitos Físicos e Matemáticos:
    1. Microestados: Omega(n_R) = N! / (n_R! * (N - n_R)!)
    2. Entropia (Stirling): S(n_R) = k_B [N ln N - n_R ln n_R - (N - n_R) ln (N - n_R)]
    3. Extensão Líquida: X = (n_R - n_L) * l = (2*n_R - N) * l
    4. Tensão Entrópica Exata: J(X) = -T (dS/dX)_T = (k_B T / 2l) * ln(n_R / (N - n_R))
       Em termos de x = X/(N*l): J(x) = (k_B T / l) * arctanh(x)
    5. Regime Hookeano (X << N*l): J_Hooke(X) = (k_B T / (N * l^2)) * X
       Constante elástica efetiva: kappa = k_B T / (N * l^2)
===============================================================================
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False


class FreelyJointedChain1D:
    """
    Classe que encapsula a física estatística e termodinâmica do modelo
    Freely Jointed Chain (FJC) unidimensional.
    """
    def __init__(self, N: int = 100, ell: float = 1.0, kB: float = 1.0, T: float = 300.0):
        """
        Inicializa o modelo polimérico.
        
        Parâmetros:
            N (int): Número total de elos/segmentos na cadeia.
            ell (float): Comprimento de cada segmento (l).
            kB (float): Constante de Boltzmann (arbitrária/didática = 1.0).
            T (float): Temperatura absoluta em Kelvin.
        """
        self.N = int(N)
        self.ell = float(ell)
        self.kB = float(kB)
        self.T = float(T)

    def compute_macrostate(self, n_R: int):
        """
        Calcula as propriedades termodinâmicas macroscópicas para um dado n_R.
        
        Retorna:
            dict com X, S, S_max, J_exact, J_hooke, kappa_hooke, n_L, x_frac, ln_omega
        """
        # Tratamento numérico para evitar log(0) e divisões por zero
        n_R = int(np.clip(n_R, 1, self.N - 1))
        n_L = self.N - n_R
        
        # Extensão líquida ponta-a-ponta (End-to-End Distance)
        X = (n_R - n_L) * self.ell
        x_frac = X / (self.N * self.ell)  # Extensão fracionária x in (-1, 1)

        # Entropia segundo a Aproximação de Stirling: S = k_B * ln(Omega)
        # ln(N!) ~ N ln N - N
        # ln(Omega) = N ln N - n_R ln n_R - n_L ln n_L
        ln_omega = (self.N * np.log(self.N) 
                    - n_R * np.log(n_R) 
                    - n_L * np.log(n_L))
        S = self.kB * ln_omega
        S_max = self.kB * self.N * np.log(2.0)  # Entropia máxima no estado enovelado (n_R = N/2)

        # Tensão Entrópica Exata: J = -T * (dS/dX)_T
        # dX = 2 * l * dn_R  ==>  dS/dX = (1 / 2l) * dS/dn_R = -(k_B / 2l) * ln(n_R / n_L)
        # Logo: J = (k_B * T / 2l) * ln(n_R / n_L) = (k_B * T / l) * arctanh(x_frac)
        J_exact = (self.kB * self.T / (2.0 * self.ell)) * np.log(n_R / n_L)

        # Aproximação Linear (Lei de Hooke Entrópica para X << N*l)
        # kappa = (k_B * T) / (N * l^2)
        kappa_hooke = (self.kB * self.T) / (self.N * (self.ell ** 2))
        J_hooke = kappa_hooke * X

        return {
            "n_R": n_R,
            "n_L": n_L,
            "X": X,
            "x_frac": x_frac,
            "ln_omega": ln_omega,
            "S": S,
            "S_max": S_max,
            "J_exact": J_exact,
            "J_hooke": J_hooke,
            "kappa_hooke": kappa_hooke
        }

    def generate_microstate_walk(self, n_R: int, seed: int = None):
        """
        Gera uma conformação microscópica aleatória (microestado) compatível com o
        macroestado especificado por n_R.
        
        Para fins de visualização intuitiva 2D:
            - Os passos no eixo X obedecem estritamente à física 1D (+l para direita, -l para esquerda).
            - No eixo Y adiciona-se uma flutuação transversal suave (random walk transversal)
              para permitir que o observador visualize cada elo individual sem sobreposição.
              
        Retorna:
            x_coords (np.ndarray): Coordenadas X acumuladas dos nós do polímero (comprimento N+1).
            y_coords (np.ndarray): Coordenadas Y acumuladas dos nós do polímero (comprimento N+1).
            steps_x (np.ndarray): Vetor de passos individuais no eixo X (+ell ou -ell).
        """
        if seed is not None:
            np.random.seed(seed)
            
        n_R = int(np.clip(n_R, 1, self.N - 1))
        n_L = self.N - n_R

        # Cria a lista de passos no eixo X: exatamente n_R para a direita (+1) e n_L para a esquerda (-1)
        steps_x_dir = np.array([1.0] * n_R + [-1.0] * n_L)
        np.random.shuffle(steps_x_dir)  # Permutação aleatória => microestado equiprovável
        steps_x = steps_x_dir * self.ell

        # Flutuações transversais no eixo Y para visualização 2D realista do polímero
        # Passos aleatórios no eixo Y com média zero
        steps_y = np.random.choice([-0.6 * self.ell, 0.0, 0.6 * self.ell], size=self.N)

        # Trajetória acumulada partindo da origem (0, 0)
        x_coords = np.concatenate([[0.0], np.cumsum(steps_x)])
        y_coords = np.concatenate([[0.0], np.cumsum(steps_y)])

        return x_coords, y_coords, steps_x_dir

    def get_theoretical_curves(self, num_points: int = 400):
        """
        Calcula as curvas teóricas contínuas de Entropia S(X) e Tensão J(X)
        ao longo de todo o domínio acessível de extensões X in (-(N-1)l, (N-1)l).
        """
        # Evita os limites exatos -N*l e +N*l para não divergir o logaritmo
        eps = 0.985
        x_frac_arr = np.linspace(-eps, eps, num_points)
        X_arr = x_frac_arr * (self.N * self.ell)

        # n_R contínuo em função de x_frac: n_R = N * (1 + x_frac) / 2
        nR_arr = self.N * (1.0 + x_frac_arr) / 2.0
        nL_arr = self.N * (1.0 - x_frac_arr) / 2.0

        # Entropia teórica
        ln_omega_arr = (self.N * np.log(self.N) 
                        - nR_arr * np.log(nR_arr) 
                        - nL_arr * np.log(nL_arr))
        S_arr = self.kB * ln_omega_arr

        # Tensão teórica exata e linear (Hooke)
        J_exact_arr = (self.kB * self.T / (2.0 * self.ell)) * np.log(nR_arr / nL_arr)
        kappa_hooke = (self.kB * self.T) / (self.N * (self.ell ** 2))
        J_hooke_arr = kappa_hooke * X_arr

        return {
            "X": X_arr,
            "x_frac": x_frac_arr,
            "S": S_arr,
            "J_exact": J_exact_arr,
            "J_hooke": J_hooke_arr,
            "kappa_hooke": kappa_hooke
        }


def plot_polymer_dashboard(model: FreelyJointedChain1D, n_R: int, seed: int = 42, fig=None):
    """
    Renderiza o dashboard de 3 gráficos para a simulação de tensão entrópica:
        Gráfico 1: Visualização espacial da conformação microscópica do polímero.
        Gráfico 2: Curva de Entropia S vs Extensão X com marcador dinâmico.
        Gráfico 3: Curva de Tensão Entrópica J vs Extensão X (Exata vs Hooke) com marcador dinâmico.
        
    Retorna o objeto Figure do Matplotlib formatado com alta qualidade estética.
    """
    if fig is None:
        fig = plt.figure(figsize=(15, 10), facecolor="#0f172a")
    else:
        fig.clf()
        fig.set_facecolor("#0f172a")

    # Calcula propriedades termodinâmicas e conformação microscópica
    state = model.compute_macrostate(n_R)
    x_coords, y_coords, steps_dir = model.generate_microstate_walk(n_R, seed=seed)
    curves = model.get_theoretical_curves(num_points=500)

    # Configuração do Grid de Subplots
    # Linha 0: Conformação do Polímero (ampla)
    # Linha 1: [Entropia S vs X] e [Tensão J vs X] lado a lado
    gs = GridSpec(2, 2, height_ratios=[1.1, 1.3], hspace=0.35, wspace=0.25, figure=fig)
    
    ax_poly = fig.add_subplot(gs[0, :])
    ax_entropy = fig.add_subplot(gs[1, 0])
    ax_tension = fig.add_subplot(gs[1, 1])

    # Paleta de Cores e Estilo Visual Dark Theme
    COLOR_BG = "#1e293b"
    COLOR_TEXT = "#f8fafc"
    COLOR_MUTED = "#94a3b8"
    COLOR_GRID = "#334155"
    COLOR_RIGHT = "#38bdf8"   # Azul/Ciano para passos à direita (+1)
    COLOR_LEFT = "#fb923c"    # Laranja/Coral para passos à esquerda (-1)
    COLOR_MARKER = "#f43f5e"  # Rosa/Rubi vibrante para estado atual
    COLOR_HOOK = "#a855f7"    # Roxo suave para Lei de Hooke

    # =========================================================================
    # SUBPLOT 1: Visualização da Conformação do Polímero (Microestado 2D/1D)
    # =========================================================================
    ax_poly.set_facecolor(COLOR_BG)
    ax_poly.grid(True, linestyle="--", alpha=0.3, color=COLOR_GRID)

    # Plota os segmentos individuais coloridos de acordo com a direção (+x ou -x)
    for i in range(model.N):
        x_seg = [x_coords[i], x_coords[i+1]]
        y_seg = [y_coords[i], y_coords[i+1]]
        c = COLOR_RIGHT if steps_dir[i] > 0 else COLOR_LEFT
        ax_poly.plot(x_seg, y_seg, color=c, lw=2.2, alpha=0.85, zorder=2)

    # Plota as articulações (beads/monômeros)
    ax_poly.scatter(x_coords, y_coords, s=16, color="#cbd5e1", edgecolors="#475569", lw=0.5, zorder=3)

    # Destaque: Ponto de Fixação (Origem x=0)
    ax_poly.scatter([0], [0], s=140, color="#22c55e", edgecolors="#ffffff", lw=2, zorder=5, label="Origem Fixa $(x=0)$")

    # Destaque: Extremidade Livre Tracionada (Ponta x=X)
    end_x = x_coords[-1]
    end_y = y_coords[-1]
    ax_poly.scatter([end_x], [end_y], s=160, color=COLOR_MARKER, edgecolors="#ffffff", lw=2, zorder=5, label=f"Extremidade $(X={state['X']:.1f})$")

    # Desenha a linha de extensão líquida X projetada na base
    y_min_val = np.min(y_coords) - 2.5 * model.ell
    ax_poly.plot([0, end_x], [y_min_val, y_min_val], color="#fbbf24", lw=3.0, ls="-", zorder=4)
    ax_poly.scatter([0, end_x], [y_min_val, y_min_val], color="#fbbf24", s=60, zorder=5)
    ax_poly.text(end_x / 2.0, y_min_val - 1.2 * model.ell, rf"Extensão Líquida $X = (n_R - n_L)\ell = {state['X']:.1f}$",
                 color="#fbbf24", fontsize=11, fontweight="bold", ha="center", va="top")

    # Vetor de Força de Tração Externa aplicada na ponta
    force_arrow_scale = np.sign(state['X']) * min(max(abs(state['x_frac']) * 8.0 * model.ell, 2.0), 12.0) if state['X'] != 0 else 0
    if abs(force_arrow_scale) > 0.1:
        ax_poly.annotate(
            "", xy=(end_x + force_arrow_scale, end_y), xytext=(end_x, end_y),
            arrowprops=dict(arrowstyle="-|>", color="#f43f5e", lw=3.0, mutation_scale=18)
        )
        ax_poly.text(end_x + force_arrow_scale * 1.1, end_y, f"  $J = {state['J_exact']:.1f}$",
                     color="#f43f5e", fontsize=11, fontweight="bold", va="center")

    ax_poly.set_title(f"Conformação Microscópica do Polímero ($N = {model.N}$ elos | $n_R = {state['n_R']}$ [Azul] | $n_L = {state['n_L']}$ [Laranja])",
                      color=COLOR_TEXT, fontsize=13, fontweight="bold", pad=12)
    ax_poly.set_xlabel(r"Posição Longitudinal $x/\ell$", color=COLOR_TEXT, fontsize=11)
    ax_poly.set_ylabel(r"Flutuação $y/\ell$", color=COLOR_TEXT, fontsize=11)
    ax_poly.tick_params(colors=COLOR_MUTED)
    
    # Limites coerentes e simétricos para o eixo x
    max_span = model.N * model.ell * 1.08
    ax_poly.set_xlim(-max_span, max_span)
    y_range = max(np.ptp(y_coords), 10.0 * model.ell)
    y_center = np.mean(y_coords)
    ax_poly.set_ylim(y_center - y_range * 0.75 - 3.0 * model.ell, y_center + y_range * 0.75)
    
    # Legenda compacta
    ax_poly.legend(loc="upper left", facecolor="#0f172a", edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=9.5)

    # Caixa Informativa de Microestados
    info_poly = (
        f"Microestados: $\\Omega \\approx {state['ln_omega']:.1f}$ (em $\\ln$)\n"
        f"Alinhamento: $x = X/(N\\ell) = {state['x_frac']:+.2f}$\n"
        f"Passos: $\\rightarrow {state['n_R']} \\quad \\leftarrow {state['n_L']}$"
    )
    ax_poly.text(0.985, 0.92, info_poly, transform=ax_poly.transAxes,
                 fontsize=10, color=COLOR_TEXT, va="top", ha="right",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#0f172a", edgecolor="#3b82f6", alpha=0.85, lw=1.2))

    # =========================================================================
    # SUBPLOT 2: Entropia S vs Extensão X
    # =========================================================================
    ax_entropy.set_facecolor(COLOR_BG)
    ax_entropy.grid(True, linestyle="--", alpha=0.3, color=COLOR_GRID)

    # Curva Teórica S(X)
    ax_entropy.plot(curves["X"], curves["S"] / model.kB, color="#38bdf8", lw=2.5, label=r"Entropia Teórica $S(X)/k_B$")
    
    # Linha de Entropia Máxima S_max
    ax_entropy.axhline(state["S_max"] / model.kB, color="#22c55e", ls=":", lw=1.5,
                       label=rf"Máx. Desordem: $N\ln 2 = {state['S_max']/model.kB:.1f}$")

    # Linhas de guia para o estado atual
    curr_S = state["S"] / model.kB
    ax_entropy.plot([state["X"], state["X"]], [0, curr_S], color=COLOR_MARKER, ls="--", lw=1.2, alpha=0.7)
    ax_entropy.plot([-model.N * model.ell, state["X"]], [curr_S, curr_S], color=COLOR_MARKER, ls="--", lw=1.2, alpha=0.7)

    # Marcador Dinâmico do Estado Atual
    ax_entropy.scatter([state["X"]], [curr_S], color=COLOR_MARKER, s=120, edgecolors="#ffffff", lw=2, zorder=5,
                       label=rf"Estado Atual ($S/k_B = {curr_S:.1f}$)")

    # Área sombreada evidenciando a perda de entropia
    ax_entropy.fill_between(curves["X"], curves["S"] / model.kB, state["S_max"] / model.kB,
                            color="#38bdf8", alpha=0.08, label=r"Perda Entrópica ($\Delta S < 0$)")

    ax_entropy.set_title(r"Entropia Configuracional vs Extensão $S(X)$", color=COLOR_TEXT, fontsize=12.5, fontweight="bold", pad=10)
    ax_entropy.set_xlabel(r"Extensão Líquida $X = (n_R - n_L)\ell$", color=COLOR_TEXT, fontsize=11)
    ax_entropy.set_ylabel(r"Entropia $S / k_B$", color=COLOR_TEXT, fontsize=11)
    ax_entropy.set_xlim(-model.N * model.ell, model.N * model.ell)
    ax_entropy.set_ylim(0, state["S_max"] / model.kB * 1.15)
    ax_entropy.tick_params(colors=COLOR_MUTED)
    ax_entropy.legend(loc="lower center", facecolor="#0f172a", edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=8.5)

    # Anotação de Física
    entropy_reduction_pct = (1.0 - (state["S"] / state["S_max"])) * 100.0
    entropy_note = (
        f"Redução de Entropia: $\\Delta S = -{entropy_reduction_pct:.1f}\\%$\n"
        f"Quanto mais esticada a cadeia,\n"
        f"menor a multiplicidade $\\Omega$ de microestados!"
    )
    ax_entropy.text(0.04, 0.25, entropy_note, transform=ax_entropy.transAxes,
                    fontsize=9.5, color="#fde047", va="bottom", ha="left",
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#0f172a", edgecolor="#fde047", alpha=0.8, lw=1))

    # =========================================================================
    # SUBPLOT 3: Tensão Entrópica J vs Extensão X (Exata vs Hooke)
    # =========================================================================
    ax_tension.set_facecolor(COLOR_BG)
    ax_tension.grid(True, linestyle="--", alpha=0.3, color=COLOR_GRID)

    # Curva Exata: J = (k_B T / 2l) * ln(n_R / n_L)
    ax_tension.plot(curves["X"], curves["J_exact"], color="#f43f5e", lw=2.8,
                    label=r"Tensão Real Exata: $J = -T\left(\frac{\partial S}{\partial X}\right)$")

    # Linha Linear: Lei de Hooke J = kappa * X
    ax_tension.plot(curves["X"], curves["J_hooke"], color=COLOR_HOOK, lw=2.0, ls="--",
                    label=rf"Lei de Hooke: $J \approx \frac{{k_B T}}{{N\ell^2}} X$ ($\kappa={state['kappa_hooke']:.2f}$)")

    # Região de Validade Linear (pequenas extensões |X| <= 0.3 N*l)
    hooke_limit = 0.35 * model.N * model.ell
    ax_tension.axvspan(-hooke_limit, hooke_limit, color=COLOR_HOOK, alpha=0.08,
                       label=r"Regime Linear ($X \ll N\ell$)")

    # Linhas de guia para o estado atual
    ax_tension.plot([state["X"], state["X"]], [0, state["J_exact"]], color="#38bdf8", ls=":", lw=1.5, alpha=0.7)
    ax_tension.plot([-model.N * model.ell, state["X"]], [state["J_exact"], state["J_exact"]], color="#38bdf8", ls=":", lw=1.5, alpha=0.7)

    # Marcador Dinâmico do Estado Atual
    ax_tension.scatter([state["X"]], [state["J_exact"]], color="#38bdf8", s=120, edgecolors="#ffffff", lw=2, zorder=5,
                       label=rf"Força Atual ($J = {state['J_exact']:.1f}$)")

    ax_tension.set_title(r"Tensão Entrópica de Restauração $J(X)$", color=COLOR_TEXT, fontsize=12.5, fontweight="bold", pad=10)
    ax_tension.set_xlabel(r"Extensão Líquida $X = (n_R - n_L)\ell$", color=COLOR_TEXT, fontsize=11)
    ax_tension.set_ylabel(r"Tensão / Força $J$", color=COLOR_TEXT, fontsize=11)
    ax_tension.set_xlim(-model.N * model.ell, model.N * model.ell)
    
    # Limite dinâmico e agradável para o eixo Y
    max_j_display = max(abs(curves["J_hooke"][-1]) * 2.2, 500.0)
    ax_tension.set_ylim(-max_j_display, max_j_display)
    ax_tension.tick_params(colors=COLOR_MUTED)
    ax_tension.legend(loc="upper left", facecolor="#0f172a", edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=8.5)

    # Anotação de Divergência Não-Linear
    diff_hooke = abs(state["J_exact"] - state["J_hooke"])
    tension_note = (
        f"Rigidez Efetiva: $\\kappa = \\frac{{k_B T}}{{N\\ell^2}} = {state['kappa_hooke']:.2f}$\n"
        f"Desvio de Hooke: $\\Delta J = {diff_hooke:.1f}$\n"
        f"Conforme $X \\to N\\ell$, a força diverge\n"
        f"assintoticamente ($J \\to \\infty$)!"
    )
    ax_tension.text(0.96, 0.08, tension_note, transform=ax_tension.transAxes,
                    fontsize=9.5, color="#38bdf8", va="bottom", ha="right",
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#0f172a", edgecolor="#38bdf8", alpha=0.8, lw=1))

    plt.suptitle(r"$\mathbf{Simulação\ de\ Elasticidade\ Entrópica\ no\ Modelo\ FJC\ 1D}$",
                 color="#ffffff", fontsize=15, y=0.985)
    
    return fig


# =============================================================================
# INTERFACE INTERATIVA PARA JUPYTER NOTEBOOK (ipywidgets)
# =============================================================================
def create_jupyter_interactive_dashboard(N_default: int = 100, T_default: float = 300.0, ell_default: float = 1.0):
    """
    Cria e exibe o dashboard interativo completo utilizando ipywidgets para Jupyter Notebooks.
    """
    if not HAS_IPYWIDGETS:
        print("[AVISO] 'ipywidgets' ou 'IPython' não encontrados. Use a versão interativa Matplotlib standalone.")
        return

    # Instância inicial do modelo físico
    model = FreelyJointedChain1D(N=N_default, ell=ell_default, kB=1.0, T=T_default)

    # Controles Interativos (Widgets)
    slider_nR = widgets.IntSlider(
        value=N_default // 2,
        min=1,
        max=N_default - 1,
        step=1,
        description=r'Elos Direita ($n_R$):',
        continuous_update=True,
        layout=widgets.Layout(width='550px'),
        style={'description_width': '160px'}
    )

    slider_T = widgets.FloatSlider(
        value=T_default,
        min=50.0,
        max=800.0,
        step=10.0,
        description='Temperatura $T$ (K):',
        continuous_update=True,
        layout=widgets.Layout(width='450px'),
        style={'description_width': '160px'}
    )

    slider_N = widgets.IntSlider(
        value=N_default,
        min=20,
        max=300,
        step=10,
        description='Total Elos ($N$):',
        continuous_update=False,
        layout=widgets.Layout(width='450px'),
        style={'description_width': '160px'}
    )

    btn_resample = widgets.Button(
        description='🎲 Nova Conformação (Amostragem)',
        button_style='info',
        tooltip='Gera uma nova conformação microscópica aleatória mantendo n_R fixo.',
        layout=widgets.Layout(width='280px', height='38px')
    )

    html_stats = widgets.HTML()
    output_plot = widgets.Output()

    # Estado interno da semente aleatória
    seed_state = {'seed': 42}

    def update_stats(n_R, T, N):
        model.N = N
        model.T = T
        state = model.compute_macrostate(n_R)
        
        html_content = rf"""
        <div style="background-color: #1e293b; padding: 14px 20px; border-radius: 8px; border-left: 5px solid #38bdf8; font-family: monospace; color: #f8fafc; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div><strong>Extensão Líquida ($X$):</strong> <span style="color: #fbbf24;">{state['X']:+.1f} &ell; ({state['x_frac']:+.2%})</span></div>
                <div><strong>Microestados ($\ln \Omega$):</strong> <span style="color: #38bdf8;">{state['ln_omega']:.1f} / {state['S_max']/model.kB:.1f}</span></div>
                <div><strong>Entropia ($S/k_B$):</strong> <span style="color: #22c55e;">{state['S']:.1f}</span></div>
                <div><strong>Tensão Real ($J$):</strong> <span style="color: #f43f5e; font-weight: bold;">{state['J_exact']:+.2f}</span></div>
                <div><strong>Hooke ($J_{{Hooke}}$):</strong> <span style="color: #a855f7;">{state['J_hooke']:+.2f}</span></div>
                <div><strong>Rigidez ($\kappa$):</strong> <span style="color: #94a3b8;">{state['kappa_hooke']:.3f}</span></div>
            </div>
        </div>
        """
        html_stats.value = html_content

    def redraw(*args):
        # Atualiza limites do slider de n_R se N mudar
        if slider_nR.max != slider_N.value - 1:
            slider_nR.max = slider_N.value - 1
            if slider_nR.value >= slider_N.value:
                slider_nR.value = slider_N.value // 2

        model.N = slider_N.value
        model.T = slider_T.value
        n_R = slider_nR.value

        update_stats(n_R, model.T, model.N)

        with output_plot:
            clear_output(wait=True)
            fig = plot_polymer_dashboard(model, n_R, seed=seed_state['seed'])
            plt.show()

    def on_resample_clicked(b):
        seed_state['seed'] = np.random.randint(0, 1000000)
        redraw()

    def on_N_changed(change):
        slider_nR.max = change['new'] - 1
        slider_nR.value = change['new'] // 2
        redraw()

    slider_nR.observe(redraw, names='value')
    slider_T.observe(redraw, names='value')
    slider_N.observe(on_N_changed, names='value')
    btn_resample.on_click(on_resample_clicked)

    # Layout de controles organizados
    controls_box = widgets.VBox([
        widgets.HBox([slider_nR, btn_resample]),
        widgets.HBox([slider_T, slider_N]),
        html_stats,
        output_plot
    ])

    # Inicializa renderização
    redraw()
    display(controls_box)


# =============================================================================
# INTERFACE STANDALONE MATPLOTLIB (Para execução fora do Jupyter)
# =============================================================================
def run_standalone_matplotlib_gui(N_default: int = 100, T_default: float = 300.0, ell_default: float = 1.0):
    """
    Inicia uma interface interativa nativa do Matplotlib com sliders e botões GUI,
    permitindo executar a simulação diretamente pelo terminal (python script.py).
    """
    model = FreelyJointedChain1D(N=N_default, ell=ell_default, kB=1.0, T=T_default)
    current_seed = [42]

    # Cria a figura principal com espaço reservado na base para os sliders GUI
    fig = plt.figure(figsize=(15, 10), facecolor="#0f172a")
    plt.subplots_adjust(bottom=0.18)

    # Função de atualização
    def update_view(val=None):
        n_R = int(slider_nR_gui.val)
        model.T = float(slider_T_gui.val)
        
        # Limpa e redesenha mantendo os sliders intactos
        plot_polymer_dashboard(model, n_R, seed=current_seed[0], fig=fig)
        fig.canvas.draw_idle()

    # Adiciona eixos para os Sliders do Matplotlib
    ax_slider_nR = fig.add_axes([0.15, 0.08, 0.40, 0.03], facecolor="#1e293b")
    slider_nR_gui = Slider(
        ax_slider_nR, r"Elos p/ Direita ($n_R$)", 1, model.N - 1,
        valinit=model.N // 2, valstep=1, color="#38bdf8"
    )
    slider_nR_gui.label.set_color("#f8fafc")
    slider_nR_gui.valtext.set_color("#f8fafc")

    ax_slider_T = fig.add_axes([0.15, 0.03, 0.40, 0.03], facecolor="#1e293b")
    slider_T_gui = Slider(
        ax_slider_T, r"Temperatura $T$ (K)", 50.0, 800.0,
        valinit=model.T, valstep=10.0, color="#f43f5e"
    )
    slider_T_gui.label.set_color("#f8fafc")
    slider_T_gui.valtext.set_color("#f8fafc")

    ax_btn_rand = fig.add_axes([0.65, 0.04, 0.22, 0.06], facecolor="#1e293b")
    btn_rand_gui = Button(ax_btn_rand, "🎲 Nova Conformação", color="#0284c7", hovercolor="#0369a1")
    btn_rand_gui.label.set_color("#ffffff")
    btn_rand_gui.label.set_fontweight("bold")

    def on_button_click(event):
        current_seed[0] = np.random.randint(0, 1000000)
        update_view()

    slider_nR_gui.on_changed(update_view)
    slider_T_gui.on_changed(update_view)
    btn_rand_gui.on_clicked(on_button_click)

    # Primeira renderização
    update_view()
    plt.show()


# =============================================================================
# BLOCO PRINCIPAL DE EXECUÇÃO
# =============================================================================
if __name__ == "__main__":
    import sys
    print("=" * 78)
    print(" SIMULAÇÃO DE TENSÃO ENTRÓPICA EM UM POLÍMERO (FJC 1D)")
    print("=" * 78)
    print("1. Para usar em Jupyter Notebook: chame create_jupyter_interactive_dashboard()")
    print("2. Iniciando interface gráfica nativa interativa Matplotlib...")
    print("=" * 78)
    
    # Executa a interface standalone interativa ou salva um frame caso em ambiente sem display
    try:
        run_standalone_matplotlib_gui()
    except Exception as e:
        print(f"[INFO] Execução interativa finalizada ou ambiente headless detectado ({e}).")
        print("[INFO] Gerando e salvando imagem estática de demonstração 'entropia_polimero_demo.png'...")
        m = FreelyJointedChain1D(N=100, ell=1.0, kB=1.0, T=300.0)
        fig_demo = plot_polymer_dashboard(m, n_R=75, seed=42)
        fig_demo.savefig("entropia_polimero_demo.png", dpi=180, bbox_inches="tight", facecolor=fig_demo.get_facecolor())
        print("✓ Gráfico de demonstração salvo com sucesso em 'entropia_polimero_demo.png'!")
