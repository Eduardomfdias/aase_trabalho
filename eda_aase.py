"""
EDA — AASE 2026/27
Análise exploratória dos dados de internamento neonatal.

Uso:
    python eda_aase.py              # gera e mostra os gráficos
    python eda_aase.py --save       # guarda em graficos/
"""

import argparse
import csv
import math
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

# ── paleta ────────────────────────────────────────────────────────────────────
C = {
    "blue":   "#2a78d6",
    "orange": "#eb6834",
    "teal":   "#1baf7a",
    "yellow": "#eda100",
    "red":    "#d03b3b",
    "grey":   "#8996ae",
    "bg":     "#f4f7fc",
    "surf":   "#ffffff",
    "text":   "#0d1219",
    "text2":  "#4a5568",
}

# ── estilo global ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  C["bg"],
    "axes.facecolor":    C["surf"],
    "axes.edgecolor":    "#dce3f0",
    "axes.labelcolor":   C["text2"],
    "axes.grid":         True,
    "axes.axisbelow":    True,
    "grid.color":        "#e6eaf3",
    "grid.linewidth":    0.8,
    "xtick.color":       C["text2"],
    "ytick.color":       C["text2"],
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.titlesize":    12,
    "axes.titleweight":  "semibold",
    "axes.titlepad":     10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        120,
    "savefig.dpi":       150,
    "savefig.bbox":      "tight",
    "savefig.facecolor": C["bg"],
})


# ── carregamento e limpeza ────────────────────────────────────────────────────
def carregar_dados(pasta: str = "dados_aase_202627"):
    sv_raw, pat_raw = [], []

    with open(f"{pasta}/1_sinais_vitais_por_hora-1.csv", newline="", encoding="utf-8") as f:
        sv_raw = list(csv.DictReader(f))

    with open(f"{pasta}/3_patologias_por_dia-1.csv", newline="", encoding="utf-8") as f:
        pat_raw = list(csv.DictReader(f))

    return sv_raw, pat_raw


def safe_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def limpar_sv(sv_raw):
    limpos, invalidos = [], []
    for r in sv_raw:
        sat  = safe_float(r["sat_o2"])
        puls = safe_float(r["puls_rate"])
        perf = safe_float(r["perfusion"])
        hora = safe_float(r["hora"])
        ok = (
            sat  is not None and 50 <= sat  <= 100 and
            puls is not None and 50 <= puls <= 350 and
            perf is not None and 0  <= perf <= 20  and
            hora is not None and 0  <= hora <= 23
        )
        (limpos if ok else invalidos).append(r)
    return limpos, invalidos


def normalizar_patologia(p: str) -> str:
    mapa = {
        "doenca das membranas hialinas":    "Doença das Membranas Hialinas",
        "doença das membranas hialinas":    "Doença das Membranas Hialinas",
        "dmh":                              "Doença das Membranas Hialinas",
        "icterícia neonatal":               "Icterícia Neonatal",
        "ictericia neonatal":               "Icterícia Neonatal",
        "anemia":                           "Anemia",
        "citomegalovírus":                  "Citomegalovírus",
        "citomegalovirus":                  "Citomegalovírus",
        "cmv":                              "Citomegalovírus",
        "displasia broncopulmonar":         "Displasia Broncopulmonar",
        "persistência do canal arterial":   "Persistência do Canal Arterial",
        "refluxo gastroesofágico":          "Refluxo Gastroesofágico",
        "sépsis":                           "Sépsis",
        "lesão renal aguda":                "Lesão Renal Aguda",
        "retinopatia da prematuridade":     "Retinopatia da Prematuridade",
    }
    return mapa.get(p.strip().lower(), p.strip().title())


# ── figura 1 — visão geral ────────────────────────────────────────────────────
def fig_overview(sv_clean, sv_raw, pat_raw):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("Visão Geral — AASE 2026/27", fontsize=14, fontweight="bold",
                 color=C["text"], x=0.05, ha="left")
    fig.subplots_adjust(top=0.82, wspace=0.35)

    # 1. Qualidade dos dados
    ax = axes[0]
    validos   = len(sv_clean)
    invalidos = len(sv_raw) - validos
    bars = ax.bar(["Válidos", "Inválidos"], [validos, invalidos],
                  color=[C["teal"], C["orange"]], width=0.5, zorder=3)
    ax.set_title("Qualidade dos Registos")
    ax.set_ylabel("Nº registos")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", " ")))
    for bar, v in zip(bars, [validos, invalidos]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
                f"{v:,}".replace(",", " "), ha="center", va="bottom",
                fontsize=9, color=C["text2"])
    ax.text(0.5, 0.97, f"{validos/len(sv_raw)*100:.1f}% válidos",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8.5, color=C["grey"])

    # 2. Duração episódios
    ax = axes[1]
    ep_dias = defaultdict(set)
    for r in sv_clean:
        ep_dias[r["episodio"]].add(r["data"])
    duracoes = sorted(len(v) for v in ep_dias.values())
    ax.hist(duracoes, bins=range(1, max(duracoes)+2), color=C["blue"],
            edgecolor=C["surf"], linewidth=0.5, zorder=3, align="left")
    ax.axvline(statistics.median(duracoes), color=C["orange"], linewidth=1.5,
               linestyle="--", label=f"Mediana {statistics.median(duracoes):.0f}d")
    ax.set_title("Duração dos Episódios")
    ax.set_xlabel("Dias de internamento")
    ax.set_ylabel("Nº episódios")
    ax.legend(fontsize=8.5, frameon=False)

    # 3. Nº patologias por episódio
    ax = axes[2]
    ep_pats = defaultdict(set)
    for r in pat_raw:
        if r["patologia"].strip():
            ep_pats[r["episodio"]].add(normalizar_patologia(r["patologia"]))
    npats = Counter(len(v) for v in ep_pats.values())
    xs = sorted(npats.keys())
    ax.bar(xs, [npats[x] for x in xs], color=C["teal"],
           width=0.6, zorder=3)
    ax.set_title("Patologias por Episódio")
    ax.set_xlabel("Nº de diagnósticos distintos")
    ax.set_ylabel("Nº episódios")
    ax.set_xticks(xs)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# ── figura 2 — distribuições sinais vitais ────────────────────────────────────
def fig_distribuicoes(sv_clean):
    sat_vals  = [safe_float(r["sat_o2"])    for r in sv_clean]
    puls_vals = [safe_float(r["puls_rate"]) for r in sv_clean]
    perf_vals = [safe_float(r["perfusion"]) for r in sv_clean]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("Distribuições dos Sinais Vitais (registos válidos)", fontsize=14,
                 fontweight="bold", color=C["text"], x=0.05, ha="left")

    # SpO₂
    ax = axes[0]
    bins_sat = [x - 0.5 for x in range(82, 102)]
    n, _, bars = ax.hist(sat_vals, bins=bins_sat, zorder=3, edgecolor=C["surf"], linewidth=0.5)
    for bar in bars:
        bar.set_facecolor(C["orange"] if bar.get_x() + 0.5 < 90 else C["blue"])
    ax.axvline(statistics.mean(sat_vals), color=C["orange"], linewidth=1.5,
               linestyle="--", label=f"Média {statistics.mean(sat_vals):.1f}%")
    ax.axvline(90, color=C["red"], linewidth=1, linestyle=":",
               label="Limiar 90%")
    ax.set_title("SpO₂ (%)")
    ax.set_xlabel("Saturação (%)")
    ax.set_ylabel("Nº registos")
    ax.legend(fontsize=8.5, frameon=False)
    below90 = sum(1 for v in sat_vals if v < 90)
    ax.text(0.03, 0.97, f"{below90} registos < 90%\n({below90/len(sat_vals)*100:.1f}%)",
            transform=ax.transAxes, va="top", fontsize=8, color=C["orange"])

    # Frequência de pulso
    ax = axes[1]
    ax.hist(puls_vals, bins=range(90, 200, 10), color=C["orange"],
            edgecolor=C["surf"], linewidth=0.5, zorder=3)
    ax.axvline(statistics.mean(puls_vals), color=C["blue"], linewidth=1.5,
               linestyle="--", label=f"Média {statistics.mean(puls_vals):.0f} bpm")
    ax.set_title("Frequência de Pulso (bpm)")
    ax.set_xlabel("Pulso (bpm)")
    ax.set_ylabel("Nº registos")
    ax.legend(fontsize=8.5, frameon=False)

    # Índice de perfusão
    ax = axes[2]
    perf_clip = [min(v, 6) for v in perf_vals]
    ax.hist(perf_clip, bins=np.arange(0, 6.25, 0.25), color=C["teal"],
            edgecolor=C["surf"], linewidth=0.5, zorder=3)
    ax.axvline(statistics.mean(perf_vals), color=C["orange"], linewidth=1.5,
               linestyle="--", label=f"Média {statistics.mean(perf_vals):.2f}")
    ax.set_title("Índice de Perfusão")
    ax.set_xlabel("Perfusão")
    ax.set_ylabel("Nº registos")
    ax.legend(fontsize=8.5, frameon=False)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# ── figura 3 — padrão circadiano ──────────────────────────────────────────────
def fig_circadiano(sv_clean):
    horas = list(range(24))
    medias = {}
    for h in horas:
        recs = [r for r in sv_clean if int(safe_float(r["hora"])) == h]
        medias[h] = {
            "sat":  statistics.mean(safe_float(r["sat_o2"])    for r in recs),
            "puls": statistics.mean(safe_float(r["puls_rate"]) for r in recs),
            "perf": statistics.mean(safe_float(r["perfusion"]) for r in recs),
            "n":    len(recs),
        }

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)
    fig.suptitle("Padrão Circadiano — Médias Horárias", fontsize=14,
                 fontweight="bold", color=C["text"], x=0.05, ha="left")

    specs = [
        ("sat",  "SpO₂ (%)",            C["blue"],   (95.0, 97.2)),
        ("puls", "Frequência Pulso (bpm)", C["orange"], (144, 152)),
        ("perf", "Índice de Perfusão",   C["teal"],   (1.05, 1.45)),
    ]
    for ax, (key, ylabel, col, ylim) in zip(axes, specs):
        vals = [medias[h][key] for h in horas]
        ax.fill_between(horas, vals, min(ylim), alpha=0.12, color=col)
        ax.plot(horas, vals, color=col, linewidth=2, zorder=3)
        ax.scatter(horas, vals, color=col, s=18, zorder=4)
        # destacar min e max
        idx_max = int(np.argmax(vals))
        idx_min = int(np.argmin(vals))
        ax.scatter([idx_max], [vals[idx_max]], color=C["teal"], s=50, zorder=5)
        ax.scatter([idx_min], [vals[idx_min]], color=C["orange"], s=50, zorder=5)
        ax.set_xlim(-0.5, 23.5)
        ax.set_ylim(*ylim)
        ax.set_title(ylabel)
        ax.set_xlabel("Hora")
        ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21])
        ax.set_xticklabels([f"{h}h" for h in [0, 3, 6, 9, 12, 15, 18, 21]])

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# ── figura 4 — patologias ─────────────────────────────────────────────────────
def fig_patologias(pat_raw):
    pat_norm = Counter(
        normalizar_patologia(r["patologia"])
        for r in pat_raw if r["patologia"].strip()
    )
    top = pat_norm.most_common(12)
    nomes = [n for n, _ in top]
    counts = [c for _, c in top]

    cores = [C["blue"], C["orange"], C["teal"], C["yellow"],
             C["blue"], C["orange"], C["teal"], C["yellow"],
             C["blue"], C["orange"], C["teal"], C["yellow"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle("Top Patologias — Nº de Ocorrências", fontsize=14,
                 fontweight="bold", color=C["text"], x=0.03, ha="left")

    bars = ax.barh(range(len(nomes)), counts, color=cores, height=0.65,
                   zorder=3, edgecolor=C["surf"], linewidth=0.5)
    ax.set_yticks(range(len(nomes)))
    ax.set_yticklabels(nomes, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Nº de ocorrências (episódio × dia)")
    ax.set_xlim(0, max(counts) * 1.18)
    ax.grid(axis="y", visible=False)

    for bar, v in zip(bars, counts):
        ax.text(v + 4, bar.get_y() + bar.get_height()/2,
                str(v), va="center", ha="left", fontsize=9, color=C["text2"])

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# ── figura 5 — boxplots por episódio ──────────────────────────────────────────
def fig_boxplots(sv_clean):
    ep_sat  = defaultdict(list)
    ep_puls = defaultdict(list)
    for r in sv_clean:
        ep_sat[r["episodio"]].append(safe_float(r["sat_o2"]))
        ep_puls[r["episodio"]].append(safe_float(r["puls_rate"]))

    eps = sorted(ep_sat.keys())
    sat_data  = [ep_sat[e]  for e in eps]
    puls_data = [ep_puls[e] for e in eps]

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle("Distribuição por Episódio", fontsize=14,
                 fontweight="bold", color=C["text"], x=0.03, ha="left")

    bp_props = dict(
        patch_artist=True,
        medianprops=dict(color=C["orange"], linewidth=2),
        whiskerprops=dict(color=C["grey"], linewidth=1),
        capprops=dict(color=C["grey"], linewidth=1),
        flierprops=dict(marker="o", markersize=2, color=C["grey"], alpha=0.5),
    )
    for ax, data, title, ylabel, col in [
        (axes[0], sat_data,  "SpO₂ por Episódio",                "SpO₂ (%)",   C["blue"]),
        (axes[1], puls_data, "Frequência de Pulso por Episódio", "FC (bpm)",   C["orange"]),
    ]:
        bplot = ax.boxplot(data, positions=range(len(eps)), widths=0.6, **bp_props)
        for patch in bplot["boxes"]:
            patch.set_facecolor(col)
            patch.set_alpha(0.4)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticks(range(len(eps)))
        ax.set_xticklabels(eps, rotation=75, ha="right", fontsize=7.5)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Guardar figuras em graficos/")
    args = parser.parse_args()

    print("A carregar dados...")
    sv_raw, pat_raw = carregar_dados()
    sv_clean, sv_inv = limpar_sv(sv_raw)
    print(f"  {len(sv_clean):,} registos válidos de {len(sv_raw):,} ({len(sv_clean)/len(sv_raw)*100:.1f}%)")
    print(f"  {len(set(r['episodio'] for r in sv_clean))} episódios  |  {len(pat_raw)} registos de patologias")

    figs = {
        "01_visao_geral":        fig_overview(sv_clean, sv_raw, pat_raw),
        "02_distribuicoes":      fig_distribuicoes(sv_clean),
        "03_circadiano":         fig_circadiano(sv_clean),
        "04_patologias":         fig_patologias(pat_raw),
        "05_boxplots_episodios": fig_boxplots(sv_clean),
    }

    if args.save:
        out = Path("graficos")
        out.mkdir(exist_ok=True)
        for nome, fig in figs.items():
            path = out / f"{nome}.png"
            fig.savefig(path)
            print(f"  Guardado: {path}")
        print("Pronto.")
    else:
        plt.show()


if __name__ == "__main__":
    main()
