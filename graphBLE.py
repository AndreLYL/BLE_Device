# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang
"""
In this module  functions related to the visualization of voltages and surfaces are declared.
"""

import sys
import global_constant as glc
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors
import numpy as np
from scipy.interpolate import interp2d
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d


def realtime_plot_v(sensor_data_sharing):
    """ Visualize the collected voltage data.

    The function creates a figure to visualize the voltages of sensor elements with 3D bar plot.
    Then the function update the plot in a dead loop.

    Args:
        sensor_data_sharing (list): sensor_data_sharing: The multiprocess sharing variable in global_variable,
                                    which stores the voltage and coordinate data.

    Returns:
        None

    """
    plt.ion()

    fig = plt.figure('Sensor signal', figsize=(7, 6))
    ax = plt.axes(projection='3d')

    # set figure
    fig.canvas.manager.window.move(0, 0)
    fig.canvas.mpl_connect('close_event', figure_close_event)

    # set axis
    ax.set_xlim(0, glc.sensor_num_x)
    ax.set_ylim(0, glc.sensor_num_y)
    ax.set_zlim(0, 4)

    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.set_zlabel('Voltage [V]')

    ax.set_xticks(np.arange(glc.sensor_num_x) + 0.4)
    ax.set_xticklabels(np.arange(glc.sensor_num_x))
    ax.set_yticks(np.arange(glc.sensor_num_x) + 0.4)
    ax.set_yticklabels(np.arange(glc.sensor_num_x))

    # The image and the real view are mirrored, so the view needs to be adjusted. The reason is that in reality (0,0)
    # is at the top left, while in figure (0,0) is at the bottom left.
    ax.invert_yaxis()

    # Adjust the orientation of the figure to match the realistic placement
    ax.view_init(azim=-45)

    # set color bar
    vmin = 0
    vmax = 4.0
    m = cm.ScalarMappable(cmap=cm.jet, norm=colors.Normalize(vmin=vmin, vmax=vmax))
    cbar = fig.colorbar(m, shrink=0.4, pad=0.15, fraction=0.03)
    cbar.set_ticks([vmin, vmin / 2, 0.0, vmax / 2, vmax])
    cbar.set_ticklabels([vmin, vmin / 2, 0.0, vmax / 2, vmax])
    cbar.ax.set_ylabel('Voltage [V]')

    fig.canvas.draw()

    x, y = np.meshgrid(np.arange(glc.sensor_num_x), np.arange(glc.sensor_num_y))
    x = x.flatten()
    y = y.flatten()
    bottom = np.zeros_like(x)
    width = depth = 0.8

    sensor_values = sensor_data_sharing
    update_v(fig, ax, sensor_values, x, y, bottom, width, depth)


def realtime_plot_xyz(sensor_data_sharing):
    """Visualize the reconstructed surface.

    The function creates a figure to visualize the reconstructed surface with 3D surface plot.
    Then the function update the plot in a dead loop.

    Args:
        sensor_data_sharing (list): The multiprocess sharing variable in global_variable, which stores the voltage and
                                    coordinate data.

    Returns:
        None

    """
    plt.ion()

    fig = plt.figure('Surface reconstruction', figsize=(7, 6))
    ax = plt.axes(projection='3d')

    # set figure
    fig.canvas.manager.window.move(700, 0)
    fig.canvas.mpl_connect('close_event', figure_close_event)

    # set axis
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-15, 15)
    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]')
    ax.view_init(azim=135)  # 调整了图的朝向，使其符合现实里摆放

    # set color bar
    vmin = -12.0
    vmax = 12.0
    m = cm.ScalarMappable(cmap=cm.jet, norm=colors.Normalize(vmin=vmin, vmax=vmax))
    cbar = fig.colorbar(m, shrink=0.4, pad=0.15, fraction=0.03)
    cbar.set_ticks([vmin, vmin / 2, 0.0, vmax / 2, vmax])
    cbar.set_ticklabels([vmin, vmin / 2, 0.0, vmax / 2, vmax])
    cbar.ax.set_ylabel('Z [mm]')

    plot_arrow(ax, [0, 0, -15], 10)

    fig.canvas.draw()

    while True:
        _, sensor_xyz = sensor_data_sharing
        update_xyz(fig, ax, sensor_xyz)


def update_v(fig, ax, sensor_values, x, y, bottom, width, depth):
    """Update the 3D bar plot for sensor voltages.

    The function delete old 3D bar object in the figure and plot a new 3D bar object to realize the refresh the graph.

    Args:
        fig (figure object): The figure object for voltage visualization
        ax (axis object): The axis object for voltage visualization
        sensor_values (list): The new voltage data to update the graph
        x (float): The x coordinate of each bar
        y (float): The y coordinate of each bar
        bottom (float): The z coordinate of each bar's the bottom.
        width (float): The width of each bar
        depth (float): The height of each bar

    Returns:
        None

    """
    top = sensor_values.flatten()
    bar = ax.bar3d(x, y, bottom, width, depth, top, shade=True, color=get_bar_color(sensor_values, 0, 6))
    fig.canvas.flush_events()
    bar.remove()


def update_xyz(fig, ax, sensor_xyz):
    """Update the 3D surface plot for surface shape.

    The function delete old 3D surface object in the figure and plot a new 3D surface object to realize the refresh
    the graph.

    Args:
        fig: The figure object for surface visualization
        ax: The axis object for surface visualization
        sensor_xyz: The new surface vertices coordinates data to update the graph

    Returns:
        None

    """
    x, y, z = sensor_xyz
    x, y, z = interpolate_surface(x, y, z, 26)
    surf = ax.plot_surface(x, y, z, shade=True, cmap='jet', vmin=-12, vmax=12)
    fig.canvas.flush_events()
    surf.remove()


def get_bar_color(value, value_min, value_max):
    """Generate jet color for given value.

    Because for function 3Dbar , this is no argument defining the value range of color map. So we use this function
    to assignment jet color for given value based on the given minimum value and maximum value.

    Args:
        value (float): The height of the bar we want to color
        value_min (float): The maximum height of the bar
        value_max (float): The minimum height of the bar

    Returns:
        color_values (float): The jet color for given value

    """
    # value_max = glc.dacRef * 3 / 4
    # value_min = -glc.dacRef * 3 / 4
    value_mid = (value_max + value_min) / 2
    fractions = 1 / 2 + (value.flatten() - value_mid) / (value_max - value_min)
    color_values = cm.jet(fractions)
    return color_values


def interpolate_surface(x, y, z, new_grid_size):
    """ Interpolate the surface shape of 6x6 grid

    The reconstructed surface is a 6x6 grid. For better visual effect, this function is used to smooth the grid
    surface by linear interpolation.

    Args:
        x (list): The x coordinates of 36 vertices arranged in 1x36 list.
        y (list): The y coordinates of 36 vertices arranged in 1x36 list.
        z (list): The z coordinates of 36 vertices arranged in 1x36 list.
        new_grid_size (int): The new size of the grid after interpolation. For example, new_grid_size=10 means the
                            new size is 10x10.

    Returns:
        None

    """
    grid_x = np.linspace(1, 6, 6)
    grid_y = np.linspace(1, 6, 6)

    f_x = interp2d(grid_x, grid_y, x, kind='linear')
    f_y = interp2d(grid_x, grid_y, y, kind='linear')
    f_z = interp2d(grid_x, grid_y, z, kind='linear')

    grid_x_new = np.linspace(1, 6, new_grid_size)
    grid_y_new = np.linspace(1, 6, new_grid_size)

    x_interp = f_x(grid_x_new, grid_y_new)
    y_interp = f_y(grid_x_new, grid_y_new)
    z_interp = f_z(grid_x_new, grid_y_new)

    return x_interp, y_interp, z_interp


def plot_arrow(ax, origin, length):
    """Plot a coordinate system sign in the surface plot.

    To clearly explain the orientation of the sensor in the graph, coordinate system arrows are added to the
    figure to indicate the orientation of the sensor.

    reference: https://hyunyoung2.github.io/2017/05/16/How_To_Plot_Vector_And_Plane_With_Python/

    Args:
        ax: The axis object for surface visualization
        origin: The coordinate of the coordinate system origin.
        length: The length of the axis arrow.

    Returns:
        None

    """
    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)

    x, y, z = origin

    ax.scatter(x, y, z, color="black", s=30, zorder=20, alpha=0.5)

    x_arrow = Arrow3D([x, length + x], [y, y], [z, z], mutation_scale=20, lw=1, arrowstyle="-|>", color="r")
    y_arrow = Arrow3D([x, x], [y, length + y], [z, z], mutation_scale=20, lw=1, arrowstyle="-|>", color="g")
    # z_arrow = Arrow3D([x, x], [y, y], [z, length + z], mutation_scale=20, lw=1, arrowstyle="-|>", color="b")
    ax.add_artist(x_arrow)
    ax.add_artist(y_arrow)
    # ax.add_artist(z_arrow)

    ax.text(x + length * 1.1, y, z, "X", size=10, color="r", horizontalalignment='center', verticalalignment='center')
    ax.text(x, y + length * 1.1, z, "Y", size=10, color="g", horizontalalignment='center', verticalalignment='center')
    # ax.text(x, y, z+length*1.1, "Z", size=10,color="b",horizontalalignment='center',verticalalignment='center')


def figure_close_event(event):
    """ After clicking on the x button of the window, exit the children process.

    To solve the problem of children process for graph still running in the background after closing figure,
    use this function to define the action to be taken when the figure window is closed: exit the process.

    Args:
        event: fixed argument for the usage of function mpl_connect.

    Returns:
        None

    """
    # After closing a window, exit the process it is in
    sys.exit()
