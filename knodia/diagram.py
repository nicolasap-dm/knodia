from shapely.geometry import LineString
from traits.api import HasStrictTraits, Instance, Property


class Diagram(HasStrictTraits):
    """ A projection of a knot (in R3) onto the plane. """

    #: A line string representation of the knot diagram without over/under decorations.
    #: If the first and last point don't correspond, the line will be closed
    #: automatically upon setting.
    line = Property(Instance(LineString), observe="_line")
    _line = Instance(LineString)

    def _set_line(self, line):
        # ensure line is closed
        x, y = line.coords.xy
        if (x[0], y[0]) != (x[-1], y[-1]):
            x = list(x) + [x[0]]
            y = list(y) + [y[0]]
            line = LineString(zip(x, y))
        self._line = line

    def _get_line(self):
        return self._line
