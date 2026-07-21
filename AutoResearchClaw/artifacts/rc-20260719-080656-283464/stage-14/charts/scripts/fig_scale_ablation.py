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

scale_settings = ["Original", "Scale = 0.1"]
task0_accuracy = np.array([88.42, 91.22])
average_accuracy = np.array([86.165, 90.055])
final_accuracy = np.array([83.91, 88.89])
forgetting = np.array([3.78, 3.22])

x = np.arange(len(scale_settings))
bar_width = 0.23

fig, (ax_accuracy, ax_forgetting) = plt.subplots(
    2,
    1,
    figsize=(3.5, 3.0),
    constrained_layout=True,
    gridspec_kw={"height_ratios": [2.0, 1.0]},
)

task0_bars = ax_accuracy.bar(
    x - bar_width,
    task0_accuracy,
    width=bar_width,
    color=COLORS[0],
    edgecolor="#222222",
    linewidth=0.45,
    label="Task-0",
    zorder=3,
)
average_bars = ax_accuracy.bar(
    x,
    average_accuracy,
    width=bar_width,
    color=COLORS[2],
    edgecolor="#222222",
    linewidth=0.45,
    label="Average",
    zorder=3,
)
final_bars = ax_accuracy.bar(
    x + bar_width,
    final_accuracy,
    width=bar_width,
    color=COLORS[1],
    edgecolor="#222222",
    linewidth=0.45,
    label="Final",
    zorder=3,
)

ax_accuracy.set_title("Effect of Adapter Residual Scale", fontsize=12)
ax_accuracy.set_ylabel("Accuracy (%)", fontsize=10)
ax_accuracy.set_xticks(x)
ax_accuracy.set_xticklabels(scale_settings, fontsize=9)
ax_accuracy.tick_params(axis="y", labelsize=9)
ax_accuracy.set_ylim(80, 94)
ax_accuracy.set_yticks(np.arange(80, 95, 4))
ax_accuracy.grid(axis="y", linestyle="--", linewidth=0.55, alpha=0.45, zorder=0)
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
            fontsize=7,
            rotation=90,
        )

ax_accuracy.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False,
    borderaxespad=0,
)

forgetting_bars = ax_forgetting.bar(
    x,
    forgetting,
    width=0.46,
    color=COLORS[3],
    edgecolor="#222222",
    linewidth=0.45,
    zorder=3,
)

ax_forgetting.set_xlabel("Hard Top-2 Scale Setting", fontsize=10)
ax_forgetting.set_ylabel("Forgetting\n(points)", fontsize=10)
ax_forgetting.set_xticks(x)
ax_forgetting.set_xticklabels(scale_settings, fontsize=9)
ax_forgetting.tick_params(axis="y", labelsize=9)
ax_forgetting.set_ylim(0, 4.5)
ax_forgetting.set_yticks([0, 2, 4])
ax_forgetting.grid(axis="y", linestyle="--", linewidth=0.55, alpha=0.45, zorder=0)
ax_forgetting.grid(axis="x", visible=False)
ax_forgetting.set_axisbelow(True)
ax_forgetting.spines["top"].set_visible(False)
ax_forgetting.spines["right"].set_visible(False)

for bar in forgetting_bars:
    value = bar.get_height()
    ax_forgetting.annotate(
        f"{value:.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, 2),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
    )

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_scale_ablation.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")