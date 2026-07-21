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
    "Signed Top-2\n(rank 16)",
    "Hard Top-2\n(rank 16)",
    "Dense softmax\n(rank 4)",
]
task0_accuracy = np.array([93.40, 88.42, 88.42, 87.84])
final_accuracy = np.array([89.70, 83.91, 83.91, 83.74])
average_accuracy = np.array([91.55, 86.165, 86.165, 85.79])

x = np.arange(len(methods))
bar_width = 0.24

fig, ax = plt.subplots(figsize=(7.0, 3.0), constrained_layout=True)

ax.bar(
    x - bar_width,
    task0_accuracy,
    width=bar_width,
    color=COLORS[0],
    edgecolor="#333333",
    linewidth=0.6,
    label="Task-0",
)
ax.bar(
    x,
    final_accuracy,
    width=bar_width,
    color=COLORS[1],
    edgecolor="#333333",
    linewidth=0.6,
    label="Final",
)
ax.bar(
    x + bar_width,
    average_accuracy,
    width=bar_width,
    color=COLORS[2],
    edgecolor="#333333",
    linewidth=0.6,
    label="Two-stage average",
)

ax.set_title("CIFAR-100 Smoke Accuracy by Read Mechanism", fontsize=12)
ax.set_xlabel("Method", fontsize=10)
ax.set_ylabel("Top-1 Accuracy (%)", fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=9)
ax.tick_params(axis="y", labelsize=9)
ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 20))
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
ax.grid(axis="x", visible=False)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False,
    borderaxespad=0,
)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_smoke_accuracy_comparison.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")