import numpy as np
from matplotlib import get_backend
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union
from traits.api import (
    Bool,
    HasStrictTraits,
    Instance,
    List,
    Property,
    Union,
    cached_property,
)

from knodia.interactor.polygon_interactor import PolygonInteractor


class Diagram(HasStrictTraits):
    """ A projection of a knot (in R3) onto the plane. """

    #: A line string representation of the knot diagram without over/under decorations.
    #: Will always return a LineString, but it can be set using a list of coordinates.
    #: If the first and last point don't match, the line will be closed automatically
    #: upon setting.
    line = Property(Union(Instance(LineString), List()), observe="_line")
    _line = Instance(LineString)

    #: Simple polygons representing the individual regions defined by the diagram. The
    #: region containing infinity is not included (see ``boundary``).
    regions = Property(observe="line")

    #: Line encompassing the diagram. One of the two region it defines is the region
    #: containing infinity.
    boundary = Property(Union(Instance(LineString)), observe="regions")

    #: Whether there is an open editor.
    _editing = Bool(False)

    def _set_line(self, line):
        if not isinstance(line, LineString):
            try:
                line = LineString(line)
            except Exception:
                raise ValueError(
                    "`line` must be passed as a LineString or a list of coordinates"
                )

        # ensure line is closed
        x, y = line.coords.xy
        if (x[0], y[0]) != (x[-1], y[-1]):
            x = list(x) + [x[0]]
            y = list(y) + [y[0]]
            line = LineString(zip(x, y))
        self._line = line

    def _get_line(self):
        return self._line

    @cached_property
    def _get_regions(self):
        # Based on Shapely documentation, unary_union fixes "invalid geometry":
        # https://shapely.readthedocs.io/en/stable/manual.html#shapely.ops.unary_union
        # Here we use it to clear overlapping geometry (which is expected, for knots)
        # and separate the diagram area into disjoint regions.
        regions = []
        for region in polygonize(unary_union(self.line)):
            if not region.is_simple:
                # This should not happen
                raise ValueError("A non-simple region was generated.")
            regions.append(region)
        # TODO: make a decent sorting, and test it
        return sorted(regions, key=lambda r: list(r.boundary.coords))

    @cached_property
    def _get_boundary(self):
        return unary_union(self.regions).boundary

    def visual_edit(self):
        if "tkagg" not in get_backend().lower():
            raise RuntimeError(
                "This method requires matplotlib to run with the TkAgg backend. If "
                "running from a notebook, use '%matplotlib tk' and restart the kernel."
            )
        if self._editing:
            raise RuntimeError(
                "The diagram is already being edited. " "Close all other editors first."
            )
        editing_poly = Polygon(
            np.column_stack(self.line.xy)[:-1], animated=True, fill=False
        )

        fig, ax = plt.subplots()
        fig.canvas.mpl_connect("close_event", self._visual_edit_finished)
        ax.add_patch(editing_poly)
        PolygonInteractor(ax, editing_poly, poly_callback=self._update_line)

        xl, yl = _lims(self.line.xy)
        ax.set_xlim(xl)
        ax.set_ylim(yl)
        plt.show()

    def _update_line(self, poly):
        """ Called every time the polygon is updated in a interactor."""
        self.line = poly.xy.tolist()

    def _visual_edit_finished(self, event):
        self._editing = False


def _lims(xy):
    def _mid_and_span(pts):
        return (max(pts) + min(pts)) / 2, (max(pts) - min(pts)) / 2

    xm, xs, ym, ys = *_mid_and_span(xy[0]), *_mid_and_span(xy[1])
    span = max(xs, ys) * 1.1

    return (xm - span, xm + span), (ym - span, ym + span)
