"""Simple animation utility for bin2path paths."""

from bin2path.path import Path3D
from bin2path.orient import infer_dirs_from_path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
from typing import Optional


def animate(
    path: Path3D,
    interval: int = 150,
    title: Optional[str] = None,
) -> None:
    """Animate building the path step by step, coloring segments by step type (L/R/U/D)."""
    raw_vertices = np.array(path.vertices, dtype=float)
    vertices = raw_vertices.copy()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # тёмный фон и более "объёмный" вид
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    if title is None:
        title = f"Animation of number {path.metadata.original_number}"
    # Заголовок сверху вне области осей
    fig.suptitle(title, fontsize=14, fontweight="bold", color="white", y=0.98)
    fig.subplots_adjust(top=0.90)

    # limits
    max_range = np.max(np.abs(vertices).max(axis=0)) * 1.1
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    # базовый ракурс
    ax.view_init(elev=30, azim=45)

    # step colors by L/R/U/D
    step_colors = {
        "L": "#FF5733",
        "R": "#2E86AB",
        "U": "#28A745",
        "D": "#FFC300",
    }

    # precompute per-edge colors и глубину по Z
    dirs = infer_dirs_from_path(path.vertices, path.edges)
    edge_colors = []
    edge_depth = []
    z_min = float(vertices[:, 2].min()) if len(vertices) > 0 else 0.0
    z_max = float(vertices[:, 2].max()) if len(vertices) > 0 else 1.0
    z_span = (z_max - z_min) or 1.0
    for i, (from_idx, to_idx) in enumerate(path.edges):
        sym = dirs[i] if i < len(dirs) else None
        edge_colors.append(step_colors.get(sym or "", "#999999"))
        # глубина относительно наблюдателя по Z
        z_mid = 0.5 * (vertices[from_idx][2] + vertices[to_idx][2])
        depth_factor = 0.45 + 0.55 * ((z_mid - z_min) / z_span)
        edge_depth.append(depth_factor)

    # line segments drawn progressively
    lines = []

    def update(i: int):
        # draw segment i-1 -> i
        if i > 0:
            from_v = vertices[i - 1]
            to_v = vertices[i]
            color = edge_colors[i - 1]
            depth_factor = edge_depth[i - 1]
            # outline first (for better readability)
            ax.plot(
                [from_v[0], to_v[0]],
                [from_v[1], to_v[1]],
                [from_v[2], to_v[2]],
                color="#FFFFFF",
                linewidth=max(3.2, 4.6 * depth_factor),
                alpha=0.85,
                solid_capstyle="round",
                solid_joinstyle="round",
                antialiased=True,
            )
            line, = ax.plot(
                [from_v[0], to_v[0]],
                [from_v[1], to_v[1]],
                [from_v[2], to_v[2]],
                color=color,
                linewidth=max(2.2, 3.2 * depth_factor),
                alpha=0.7 + 0.3 * depth_factor,
                solid_capstyle="round",
                solid_joinstyle="round",
                antialiased=True,
            )
            lines.append(line)
        return lines

    # Legend for step types
    legend_handles = [
        mpatches.Patch(color=step_colors["L"], label="L (Left)"),
        mpatches.Patch(color=step_colors["R"], label="R (Right)"),
        mpatches.Patch(color=step_colors["U"], label="U (Up)"),
        mpatches.Patch(color=step_colors["D"], label="D (Down)"),
    ]
    ax.legend(handles=legend_handles, loc="upper left")

    from matplotlib.animation import FuncAnimation

    # ВАЖНО: держим ссылку на объект анимации, чтобы его не уничтожил GC до show()
    ani = FuncAnimation(
        fig,
        update,
        frames=len(vertices),
        interval=interval,
        blit=False,
        repeat=False,
    )
    # сохраняем на объекте фигуры, чтобы точно не пропал
    fig._bin2path_animation = ani  # type: ignore[attr-defined]

    plt.show()


def rotate_view(
    path: Path3D,
    frames: int = 120,
    interval: int = 80,
    title: Optional[str] = None,
) -> None:
    """Простая анимация вращения камеры вокруг уже построенного пути."""
    raw_vertices = np.array(path.vertices, dtype=float)
    vertices = raw_vertices.copy()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    if title is None:
        title = f"Rotation of number {path.metadata.original_number}"
    # Заголовок сверху вне области осей
    fig.suptitle(title, fontsize=14, fontweight="bold", color="white", y=0.98)
    fig.subplots_adjust(top=0.90)

    max_range = np.max(np.abs(vertices).max(axis=0)) * 1.1
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    # нарисуем весь путь как в визуализации (L/R/U/D цвета)
    step_colors = {
        "L": "#FF5733",
        "R": "#2E86AB",
        "U": "#28A745",
        "D": "#FFC300",
    }
    dirs = infer_dirs_from_path(path.vertices, path.edges)
    for i, (from_idx, to_idx) in enumerate(path.edges):
        sym = dirs[i] if i < len(dirs) else None
        color = step_colors.get(sym or "", "#999999")
        p0 = vertices[from_idx]
        p1 = vertices[to_idx]
        # outline (white) underlay for contrast
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            [p0[2], p1[2]],
            color="#FFFFFF",
            linewidth=3.6,
            alpha=0.85,
            solid_capstyle="round",
            solid_joinstyle="round",
            antialiased=True,
        )
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            [p0[2], p1[2]],
            color=color,
            linewidth=2.0,
            alpha=0.9,
            solid_capstyle="round",
            solid_joinstyle="round",
            antialiased=True,
        )

    # start/end точки
    if len(vertices) > 0:
        s = vertices[0]
        ax.scatter(
            [s[0]],
            [s[1]],
            [s[2]],
            c="#FFFFFF",
            s=80,
            marker="o",
        )
    if len(vertices) > 1:
        e = vertices[-1]
        ax.scatter(
            [e[0]],
            [e[1]],
            [e[2]],
            c="#FF0000",
            s=80,
            marker="s",
        )

    # легенда направлений
    legend_handles = [
        mpatches.Patch(color=step_colors["L"], label="L (Left)"),
        mpatches.Patch(color=step_colors["R"], label="R (Right)"),
        mpatches.Patch(color=step_colors["U"], label="U (Up)"),
        mpatches.Patch(color=step_colors["D"], label="D (Down)"),
    ]
    ax.legend(handles=legend_handles, loc="upper left")

    from matplotlib.animation import FuncAnimation

    def update_view(i: int):
        az = 360.0 * (i / frames)
        ax.view_init(elev=30, azim=az)
        return []

    ani = FuncAnimation(
        fig,
        update_view,
        frames=frames,
        interval=interval,
        blit=False,
        repeat=True,
    )
    fig._bin2path_rotation = ani  # type: ignore[attr-defined]

    plt.show()

