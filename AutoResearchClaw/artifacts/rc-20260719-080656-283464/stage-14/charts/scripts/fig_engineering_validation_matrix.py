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

checks = [
    "Unit tests",
    "ViT forward/\nbackward",
    "Top-2\nsparsity",
    "Finite nonzero\ngradients",
    "Fixed cross-task\ncapacity",
    "CUDA AMP",
    "Sparse\nexecution",
]
status = np.ones((1, len(checks)), dtype=float)
cell_labels = ["4/4", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS"]

cmap = matplotlib.colors.ListedColormap([COLORS[6], COLORS[2]])
norm = matplotlib.colors.BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)

fig, ax = plt.subplots(figsize=(7.0, 3.0), constrained_layout=True)

ax.imshow(
    status,
    cmap=cmap,
    norm=norm,
    aspect="auto",
    interpolation="nearest",
)

for column, label in enumerate(cell_labels):
    ax.text(
        column,
        0,
        label,
        ha="center",
        va="center",
        color="white",
        fontsize=10,
        fontweight="bold",
    )

ax.set_title("Engineering Validation Coverage", fontsize=12)
ax.set_xlabel("Validation Check", fontsize=10)
ax.set_ylabel("Implementation Component", fontsize=10)
ax.set_xticks(np.arange(len(checks)))
ax.set_xticklabels(checks, fontsize=9)
ax.set_yticks([0])
ax.set_yticklabels(["Read-only basis memory"], fontsize=9)

ax.set_xticks(np.arange(-0.5, len(checks), 1), minor=True)
ax.set_yticks([-0.5, 0.5], minor=True)
ax.grid(which="minor", color="white", linestyle="-", linewidth=1.5)
ax.tick_params(which="minor", bottom=False, left=False)
ax.tick_params(axis="x", length=0, pad=7)
ax.tick_params(axis="y", length=0)

for spine in ax.spines.values():
    spine.set_visible(False)

output_path = "/home/shihoukun/project/work2/AutoResearchClaw/artifacts/rc-20260719-080656-283464/stage-14/charts/fig_engineering_validation_matrix.png"
fig.savefig(output_path, dpi=300)
plt.close(fig)
print(f"Saved: {output_path}")