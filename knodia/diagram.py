from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union
from traits.api import cached_property, HasStrictTraits, Instance, List, Property, Union


class Diagram(HasStrictTraits):
    """ A projection of a knot (in R3) onto the plane. """

    #: A line string representation of the knot diagram without over/under decorations.
    #: Will always return a LineString, but it can be set using a list of coordinates.
    #: If the first and last point don't match, the line will be closed automatically
    #: upon setting.
    line = Property(Union(Instance(LineString), List()), observe="_line")
    _line = Instance(LineString)

    #: Simple polygons representing the individual regions defined by the diagram. The
    #: region containing infinity is not included.
    regions = Property(observe="line")

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
        # Sort by bottom-left-most coordinate in the region (to ensure consistency).
        # Users shouldn't rely on any particular sorting – just a deterministic one.
        return sorted(regions, key=lambda r: list(r.boundary.coords))
