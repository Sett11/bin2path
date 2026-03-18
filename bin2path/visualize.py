"""Visualize a 3D path."""

from bin2path.path import Path3D
from bin2path.orient import infer_dirs_from_path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # needed for 3d projection
import numpy as np
from typing import Optional, Dict


def visualize(
    path: Path3D,
    figsize: tuple[float, float] = (12, 10),
    show_vertices: bool = True,
    vertex_size: float = 30,
    vertex_color: str = "#FF5733",
    show_edges: bool = True,
    edge_color: str = "#2E86AB",
    edge_linewidth: float = 2.8,
    min_edge_linewidth: float = 1.8,
    edge_outline: bool = True,
    edge_outline_color: Optional[str] = None,
    edge_outline_width: float = 1.6,
    show_start: bool = True,
    start_color: str = "#28A745",
    start_size: float = 100,
    show_end: bool = True,
    end_color: str = "#DC3545",
    end_size: float = 100,
    axis_equal: bool = True,
    hide_axes: bool = False,
    center: bool = False,
    normalize: bool = False,
    color_by_z: bool = True,
    color_by_step: bool = True,
    show_cube: bool = False,
    auto_view: bool = False,
    dark_theme: bool = False,
    highlight_nodes: bool = True,
    title: Optional[str] = None,
    azim: float = -60,
    elev: float = 30,
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize a 3D path.
    
    Args:
        path: Path3D object to visualize.
        figsize: Figure size (width, height).
        show_vertices: Whether to show vertex markers.
        vertex_size: Size of vertex markers.
        vertex_color: Color of vertices.
        show_edges: Whether to show edge lines.
        edge_color: Color of edges.
        edge_linewidth: Width of edge lines.
        show_start: Whether to highlight start point.
        start_color: Color of start point.
        start_size: Size of start point marker.
        show_end: Whether to highlight end point.
        end_color: Color of end point.
        end_size: Size of end point marker.
        axis_equal: Whether to set equal axis scaling (before centering/normalizing).
        hide_axes: If True, hide axes, ticks and grid (show pure figure).
        center: If True, center vertices around origin before plotting.
        normalize: If True, scale vertices to fit into [-1,1] cube.
        color_by_z: If True, color vertices by their Z coordinate (depth cue).
        color_by_step: If True, color edges by step type (L/R/U/D).
        show_cube: If True, draw a wireframe cube around normalized figure.
        title: Optional title for the plot.
        azim: Azimuth angle for 3D view.
        elev: Elevation angle for 3D view.
        save_path: Optional path to save the figure.
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    # optional dark background for лучшего 3D-эффекта
    if dark_theme:
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")
        # на тёмном фоне тонкие линии хуже читаются
        edge_linewidth *= 1.25
        min_edge_linewidth *= 1.25

    # outline settings (auto-contrast if color not provided)
    if edge_outline_color is None:
        edge_outline_color = "#FFFFFF" if dark_theme else "#000000"
    
    # raw integer vertices for direction classification (L/R/U/D)
    raw_vertices = np.array(path.vertices, dtype=float)
    # working copy (may be centered/normalized for plotting)
    vertices = raw_vertices.copy()

    # Optional centering / normalization (to view figure "out of axes")
    if center or normalize:
        cx, cy, cz = vertices.mean(axis=0)
        vertices[:, 0] -= cx
        vertices[:, 1] -= cy
        vertices[:, 2] -= cz

        if normalize:
            span = np.max(np.ptp(vertices, axis=0))  # max range among axes
            if span > 0:
                vertices /= span
    
    # подготовка диапазона Z для глубинных эффектов
    z_min = z_max = None
    z_span = None
    if len(vertices) > 0:
        zs_all = vertices[:, 2]
        z_min = float(zs_all.min())
        z_max = float(zs_all.max())
        z_span = z_max - z_min or 1.0

    if show_edges and len(path.edges) > 0:
        # Draw edges as lines, optionally colored by step type (L/R/U/D)
        if color_by_step:
            step_colors: Dict[str, str] = {
                "L": "#FF5733",  # orange/red
                "R": "#2E86AB",  # blue
                "U": "#28A745",  # green
                "D": "#FFC300",  # yellow
            }
            dirs = infer_dirs_from_path(path.vertices, path.edges)
            for i, (from_idx, to_idx) in enumerate(path.edges):
                sym = dirs[i] if i < len(dirs) else None
                c = step_colors.get(sym or "", edge_color)
                # draw using transformed vertices for correct placement
                from_plot = vertices[from_idx]
                to_plot = vertices[to_idx]
                # простая глубинная подсветка по Z: ближе — толще и ярче
                if z_span is not None:
                    z_mid = 0.5 * (from_plot[2] + to_plot[2])
                    depth_factor = 0.45 + 0.55 * ((z_mid - z_min) / z_span)
                else:
                    depth_factor = 1.0
                ax.plot(
                    [from_plot[0], to_plot[0]],
                    [from_plot[1], to_plot[1]],
                    [from_plot[2], to_plot[2]],
                    color=edge_outline_color if edge_outline else c,
                    linewidth=(
                        max(min_edge_linewidth, edge_linewidth * depth_factor)
                        + (edge_outline_width if edge_outline else 0.0)
                    ),
                    alpha=(0.75 + 0.25 * depth_factor) if edge_outline else (0.65 + 0.35 * depth_factor),
                    solid_capstyle="round",
                    solid_joinstyle="round",
                    antialiased=True,
                )
                if edge_outline:
                    ax.plot(
                        [from_plot[0], to_plot[0]],
                        [from_plot[1], to_plot[1]],
                        [from_plot[2], to_plot[2]],
                        color=c,
                        linewidth=max(min_edge_linewidth, edge_linewidth * depth_factor),
                        alpha=0.65 + 0.35 * depth_factor,
                        solid_capstyle="round",
                        solid_joinstyle="round",
                        antialiased=True,
                    )
        else:
            for from_idx, to_idx in path.edges:
                from_v = vertices[from_idx]
                to_v = vertices[to_idx]
                if z_span is not None:
                    z_mid = 0.5 * (from_v[2] + to_v[2])
                    depth_factor = 0.45 + 0.55 * ((z_mid - z_min) / z_span)
                else:
                    depth_factor = 1.0
                ax.plot(
                    [from_v[0], to_v[0]],
                    [from_v[1], to_v[1]],
                    [from_v[2], to_v[2]],
                    color=edge_outline_color if edge_outline else edge_color,
                    linewidth=(
                        max(min_edge_linewidth, edge_linewidth * depth_factor)
                        + (edge_outline_width if edge_outline else 0.0)
                    ),
                    alpha=(0.75 + 0.25 * depth_factor) if edge_outline else (0.65 + 0.35 * depth_factor),
                    solid_capstyle="round",
                    solid_joinstyle="round",
                    antialiased=True,
                )
                if edge_outline:
                    ax.plot(
                        [from_v[0], to_v[0]],
                        [from_v[1], to_v[1]],
                        [from_v[2], to_v[2]],
                        color=edge_color,
                        linewidth=max(min_edge_linewidth, edge_linewidth * depth_factor),
                        alpha=0.65 + 0.35 * depth_factor,
                        solid_capstyle="round",
                        solid_joinstyle="round",
                        antialiased=True,
                    )
    
    if show_vertices:
        xs, ys, zs = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        if color_by_z:
            # Нормализуем Z для цветовой карты, чтобы глубина была видна визуально
            z_min_s, z_max_s = zs.min(), zs.max()
            span = z_max_s - z_min_s or 1.0
            colors = (zs - z_min_s) / span
            sc = ax.scatter(
                xs,
                ys,
                zs,
                c=colors,
                cmap="viridis",
                s=vertex_size,
                alpha=0.8,
                depthshade=True,
            )
        else:
            ax.scatter(
                xs,
                ys,
                zs,
                c=vertex_color,
                s=vertex_size,
                alpha=0.6,
                depthshade=True,
            )

    # подсветка "узлов" — вершин, в которые путь входит несколько раз
    if highlight_nodes and len(vertices) > 0:
        coords_map: Dict[tuple[float, float, float], int] = {}
        for vx, vy, vz in vertices:
            key = (float(vx), float(vy), float(vz))
            coords_map[key] = coords_map.get(key, 0) + 1
        node_x, node_y, node_z = [], [], []
        for (vx, vy, vz), cnt in coords_map.items():
            if cnt > 1:
                node_x.append(vx)
                node_y.append(vy)
                node_z.append(vz)
        if node_x:
            ax.scatter(
                node_x,
                node_y,
                node_z,
                c="#FFFFFF" if dark_theme else "#8E44AD",
                s=vertex_size * 1.5,
                alpha=0.9,
                marker="o",
                label="Nodes",
                depthshade=False,
            )
    
    if show_start and len(vertices) > 0:
        start = vertices[0]
        ax.scatter(
            [start[0]], [start[1]], [start[2]],
            c=start_color,
            s=start_size,
            marker="o",
            label="Start",
            depthshade=False,
        )
    
    if show_end and len(vertices) > 1:
        end = vertices[-1]
        ax.scatter(
            [end[0]], [end[1]], [end[2]],
            c=end_color,
            s=end_size,
            marker="s",
            label="End",
            depthshade=False,
        )
    
    # Labels and title
    if not hide_axes:
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
    
    if title is None:
        title = f"bin2path: {path.metadata.original_number} (bits: {path.metadata.bits_length})"
    ax.set_title(title, fontsize=14, fontweight="bold")
    
    # Set viewing angle (with optional авто-подбором)
    if auto_view and len(vertices) > 1:
        # грубая эвристика: смотрим так, чтобы был виден и Z, и самые вытянутые оси
        ranges = np.ptp(vertices, axis=0)
        # если Z почти плоский, чуть больше сверху
        if ranges[2] < 0.2 * max(ranges[0], ranges[1]):
            use_elev, use_azim = 70, 45
        else:
            use_elev, use_azim = 30, 45
        ax.view_init(elev=use_elev, azim=use_azim)
    else:
        ax.view_init(elev=elev, azim=azim)
    
    # Equal aspect ratio
    if axis_equal:
        # Get the max range to set limits
        max_range = np.max(np.abs(vertices).max(axis=0)) * 1.1
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])

    # Optional wireframe cube to emphasize 3D space
    if show_cube:
        r = max_range if axis_equal else np.max(np.abs(vertices).max(axis=0)) * 1.1
        # 8 cube vertices
        corners = np.array(
            [
                [-r, -r, -r],
                [r, -r, -r],
                [r, r, -r],
                [-r, r, -r],
                [-r, -r, r],
                [r, -r, r],
                [r, r, r],
                [-r, r, r],
            ]
        )
        # 12 edges of the cube
        cube_edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]
        for i0, i1 in cube_edges:
            p0, p1 = corners[i0], corners[i1]
            ax.plot(
                [p0[0], p1[0]],
                [p0[1], p1[1]],
                [p0[2], p1[2]],
                color="#CCCCCC",
                linewidth=0.5,
                alpha=0.5,
            )
    
    # Add legend: Start/End + step type colors
    handles = []
    if show_start:
        handles.append(mpatches.Patch(color=start_color, label="Start"))
    if show_end:
        handles.append(mpatches.Patch(color=end_color, label="End"))

    if color_by_step:
        # Same colors as in edge rendering
        handles.extend(
            [
                mpatches.Patch(color="#FF5733", label="L (Left)"),
                mpatches.Patch(color="#2E86AB", label="R (Right)"),
                mpatches.Patch(color="#28A745", label="U (Up)"),
                mpatches.Patch(color="#FFC300", label="D (Down)"),
            ]
        )

    if handles:
        ax.legend(handles=handles, loc="upper left")
    
    # Optionally hide axes / ticks / grid
    if hide_axes:
        ax.set_axis_off()

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
        print(f"Figure saved to {save_path}")
    
    plt.show()