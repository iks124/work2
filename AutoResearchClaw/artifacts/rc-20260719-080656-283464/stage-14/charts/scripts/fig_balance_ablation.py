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

balance_weights = ["0", "0.1", "1.0"]
task0_accuracy = np.array([91.22, 88.52, 88.44])
average_accuracy = np.array([90.055, 87.545, 86.925])
final_accuracy = np.array([88.89, 86.57, 85.41])
forgetting = np.array([3.22, 1.00, 2.14])

x = np.arange(len(balance_weights))
bar_width = 0.24

fig, (ax_accuracy, ax_forgetting) = plt.subplots(
    1,
    2,
    figsize=(7.0, 3.0),
    constrained_layout=True,
    gridspec_kw={"width_ratios": [1.65, 1.0]},
)
fig.suptitle(
    "Load-Balancing Accuracy–Forgetting Trade-off",
    fontsize=12,
    y=1.08,
)

task0_bars = ax_accuracy.bar(
    x - bar_width,
    task0_accuracy,
    width=bar_width,
    color=COLORS[0],
    edgecolor="#222222",
    linewidth=0.5,
    label="Task-0 accuracy",
    zorder=3,
)
average_bars = ax_accuracy.bar(
    x,
    average_accuracy,
    width=bar_width,
    color=COLORS[2],
    edgecolor="#222222",
    linewidth=0.5,
    label="Average accuracy",
    zorder=3,
)
final_bars = ax_accuracy.bar(
    x + bar_width,
    final_accuracy,
    width=bar_width,
    color=COLORS[1],
    edgecolor="#222222",
    linewidth=0.5,
    label="Final accuracy",
    zorder=3,
)

ax_accuracy.set_xlabel("Load-Balancing Weight")
ax_accuracy.set_ylabel("Accuracy (%)")
ax_accuracy.set_xticks(x)
ax_accuracy.set_xticklabels(balance_weights)
ax_accuracy.set_ylim(82, 94)
ax_accuracy.set_yticks(np.arange(82, 95, 2))
ax_accuracy.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
ax_accuracy.grid(axis="x", visible=False)
ax_accuracy.set_axisbelow(True)
ax_accuracy.spines["top"].set_visible(False)
ax_accuracy.spines["right"].set_visible(False)

for bars in (task0_bars, average_bars, final_bars):
    for bar in bars:
        value = bar.get_height()
        ax_accuracy.annotate(
            f"{value:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5,
            rotation=90,
        )

forgetting_bars = ax_forgetting.bar(
    x,
    forgetting,
    width=0.58,
    color=COLORS[3],
    edgecolor="#222222",
    linewidth=0.5,
    zorder=3,
)

ax_forgetting.set_xlabel("Load-Balancing Weight")
ax_forgetting.set_ylabel("Forgetting (points)")
ax_forgetting.set_xticks(x)
ax_forgetting.set_xticklabels(balance_weights)
ax_forgetting.set_ylim(0, 4)
ax_forgetting.set_yticks(np.arange(0, 4.1, 1))
ax_forgetting.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
ax_forgetting.grid(axis="x", visible=False)
ax_forgetting.set_axisbelow(True)
ax_forgetting.spines["top"].set_visible(False)
ax_forgetting.spines["right"].set_visible(False)

for bar in forgetting_bars:
    value = bar.get_height()
    ax_forgetting.annotate(
        f"{value:.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
    )

fig.legend(
    handles=[task0_bars, average_bars, final_bars],
    labels=["Task-0 accuracy", "Average accuracy", "Final accuracy"],
    loc="upper center",
    bbox_to_anchor=(0.5, 1.02),
    ncol=3,
    frameon=False,
)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_balance_ablation.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")