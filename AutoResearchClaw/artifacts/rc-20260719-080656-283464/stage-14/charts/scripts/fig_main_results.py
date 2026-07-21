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
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

methods = [
    "CaRE",
    "Signed Top-2\nrank 16",
    "Hard Top-2\nrank 16",
    "Dense softmax\nrank 4",
    "Hard Top-2\nscale 0.1",
    "Signed Top-2\nscale 0.1",
]
average_accuracy = np.array([91.550, 86.165, 86.165, 85.790, 90.055, 89.455])
final_accuracy = np.array([89.700, 83.910, 83.910, 83.740, 88.890, 88.310])

x = np.arange(len(methods))
bar_width = 0.36

fig, ax = plt.subplots(figsize=(7.0, 3.0), constrained_layout=True)

average_bars = ax.bar(
    x - bar_width / 2,
    average_accuracy,
    width=bar_width,
    color=COLORS[0],
    edgecolor="#222222",
    linewidth=0.5,
    label="Average accuracy",
    zorder=3,
)
final_bars = ax.bar(
    x + bar_width / 2,
    final_accuracy,
    width=bar_width,
    color=COLORS[1],
    edgecolor="#222222",
    linewidth=0.5,
    label="Final accuracy",
    zorder=3,
)

ax.set_title("Smoke-Test Performance Across Routing Variants", fontsize=12)
ax.set_xlabel("Method", fontsize=10)
ax.set_ylabel("Accuracy (%)", fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=9)
ax.tick_params(axis="y", labelsize=9)
ax.set_ylim(80, 94)
ax.set_yticks(np.arange(80, 95, 2))
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

for bars in (average_bars, final_bars):
    for bar in bars:
        value = bar.get_height()
        ax.annotate(
            f"{value:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5,
            rotation=90,
        )

ax.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False,
    borderaxespad=0,
)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_main_results.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")