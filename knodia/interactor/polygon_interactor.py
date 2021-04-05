# Based on https://matplotlib.org/3.4.0/gallery/event_handling/poly_editor.html
#
# Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved.
# Edits by Nicola De Mitri and the knodia authors are visible in this file Git
# commit history.
#
# This code is open source. See license for the original code in the
# ``LICENSE_MATPLOTLIB`` file.

import numpy as np
from matplotlib.artist import Artist
from matplotlib.lines import Line2D


def dist(x, y):
    """
    Return the distance between two points.
    """
    d = x - y
    return np.sqrt(np.dot(d, d))


def dist_point_to_segment(p, s0, s1):
    """
    Get the distance of a point to a segment.
      *p*, *s0*, *s1* are *xy* sequences
    This algorithm from
    http://geomalgorithms.com/a02-_lines.html
    """
    v = s1 - s0
    w = p - s0
    c1 = np.dot(w, v)
    if c1 <= 0:
        return dist(p, s0)
    c2 = np.dot(v, v)
    if c2 <= c1:
        return dist(p, s1)
    b = c1 / c2
    pb = s0 + b * v
    return dist(p, pb)


class PolygonInteractor:
    """
    A polygon editor.

    Key-bindings

      'd' delete the vertex under point

      'i' insert a vertex at point.  You must be within epsilon of the
          line connecting two existing vertices

      'x' inserts a 'x' point.

    For every destructive action, sends back the current poly and "x" point index to
    ``poly_callback``.
    """

    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, ax, poly, x_point, poly_callback):
        if poly.figure is None:
            raise RuntimeError(
                "You must first add the polygon to a figure "
                "or canvas before defining the interactor"
            )
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly
        self.poly_callback = poly_callback

        self.x_point = x_point

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x, y, marker="o", markerfacecolor="r", animated=True)
        self.ax.add_line(self.line)

        x_marker_coords = (
            ([x[x_point]], [y[x_point]]) if x_point is not None else ([], [])
        )
        self.x_marker = Line2D(*x_marker_coords, marker="x", ms=30, animated=True)
        self.ax.add_line(self.x_marker)

        self.cid = self.poly.add_callback(self.poly_changed)
        self._ind = None  # the active vert

        canvas.mpl_connect("draw_event", self.on_draw)
        canvas.mpl_connect("button_press_event", self.on_button_press)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        canvas.mpl_connect("button_release_event", self.on_button_release)
        canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas = canvas

    def on_draw(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.ax.draw_artist(self.x_marker)

    def poly_changed(self, poly):
        """This method is called whenever the pathpatch object is called."""
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def get_ind_under_point(self, event):
        """
        Return the index of the point closest to the event position or *None*
        if no point is within ``self.epsilon`` to the event position.
        """
        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.hypot(xt - event.x, yt - event.y)
        (indseq,) = np.nonzero(d == d.min())
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        return ind

    def on_button_press(self, event):
        """Callback for mouse button presses."""
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)

    def on_button_release(self, event):
        """Callback for mouse button releases."""
        if event.button != 1:
            return
        self._ind = None
        self.poly_callback(self.poly, self.x_point)

    def on_key_press(self, event):
        """Callback for key presses."""
        if not event.inaxes:
            return
        if event.key == "d":
            ind = self.get_ind_under_point(event)
            if ind is not None and ind != 0:
                # TODO make it possible to remove point with ind == 0
                self.poly.xy = np.delete(self.poly.xy, ind, axis=0)
                self.line.set_data(zip(*self.poly.xy))
                if ind == self.x_point:
                    self.x_point = None
                    self.x_marker.set_data([[], []])
                elif self.x_point is not None and ind < self.x_point:
                    self.x_point -= 1
                self.poly_callback(self.poly, self.x_point)
        elif event.key == "i" or event.key == "x":
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y  # display coords
            for i in range(len(xys) - 1):
                s0 = xys[i]
                s1 = xys[i + 1]
                d = dist_point_to_segment(p, s0, s1)
                if d <= self.epsilon:
                    self.poly.xy = np.insert(
                        self.poly.xy, i + 1, [event.xdata, event.ydata], axis=0
                    )
                    self.line.set_data(zip(*self.poly.xy))
                    if event.key == "x":
                        self.x_point = i + 1
                        self.x_marker.set_data([event.xdata, event.ydata])
                    elif self.x_point is not None and self.x_point > i:
                        self.x_point += 1
                    self.poly_callback(self.poly, self.x_point)
                    break
        if self.line.stale:
            self.canvas.draw_idle()

    def on_mouse_move(self, event):
        """Callback for mouse movements."""
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x, y
        if self._ind == 0:
            self.poly.xy[-1] = x, y
        elif self._ind == len(self.poly.xy) - 1:
            self.poly.xy[0] = x, y
        self.line.set_data(zip(*self.poly.xy))
        if self._ind == self.x_point:
            self.x_marker.set_data([x, y])

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.ax.draw_artist(self.x_marker)
        self.canvas.blit(self.ax.bbox)
