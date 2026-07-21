import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Academic styling
try:
    plt.style.use(['science', 'ieee'])
except Exception:
    try:
        plt.style.use(['seaborn-v0_8-whitegrid'])
    except Exception:
        pass  # Use default matplotlib style

# Colorblind-safe palette
COLORS = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']
LINE_STYLES = ['-', '--', '-.', ':']
MARKERS = ['o', 's', '^', 'D', 'v', 'P', '*', 'X']

# Publication settings
plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

methods = ["CaRE", "Signed\nTop-2", "Hard\nTop-2", "Dense\nsoftmax"]
forgetting = np.array([2.96, 3.76, 3.78, 3.16])
x = np.arange(len(methods))

fig, ax = plt.subplots(figsize=(3.5, 3.0), constrained_layout=True)

bars = ax.bar(
    x,
    forgetting,
    width=0.68,
    color=[COLORS[0], COLORS[1], COLORS[2], COLORS[3]],
    edgecolor="#333333",
    linewidth=0.7,
)

for bar, value in zip(bars, forgetting):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.07,
        f"{value:.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax.set_title(
    "Observed Forgetting in the\nTwo-Phase Smoke Run",
    fontsize=12,
)
ax.set_xlabel("Method", fontsize=10)
ax.set_ylabel("Forgetting (percentage points)", fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=9)
ax.tick_params(axis="y", labelsize=9)
ax.set_ylim(0, 4.35)
ax.set_yticks(np.arange(0, 4.1, 1.0))
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_smoke_forgetting_analysis.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")