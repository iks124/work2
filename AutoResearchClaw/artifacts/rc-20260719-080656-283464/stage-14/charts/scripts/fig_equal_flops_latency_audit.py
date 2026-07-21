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

mechanisms = [
    "Signed Top-2\nrank 16\n619.8M FLOPs",
    "Dense softmax\nrank 4\n619.8M FLOPs",
]
latency_ms = np.array([0.753, 0.533])
x = np.arange(len(mechanisms))

fig, ax = plt.subplots(figsize=(3.5, 3.0), constrained_layout=True)

bars = ax.bar(
    x,
    latency_ms,
    width=0.62,
    color=[COLORS[0], COLORS[1]],
    edgecolor="#333333",
    linewidth=0.7,
)

for bar, value in zip(bars, latency_ms):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.018,
        f"{value:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax.set_title(
    "Equal Analytical FLOPs,\nUnequal Measured Latency",
    fontsize=12,
)
ax.set_xlabel("Read Mechanism", fontsize=10)
ax.set_ylabel("Latency per Layer (ms)", fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(mechanisms, fontsize=9)
ax.tick_params(axis="y", labelsize=9)
ax.set_ylim(0, 0.86)
ax.set_yticks(np.arange(0, 0.81, 0.2))
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_equal_flops_latency_audit.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")