import unittest

from shapely.geometry import LineString

from knodia.diagram import Diagram

TREFOIL = [
    (0, 0),
    (2, 0),
    (2, -2),
    (4, -2),
    (4, -4),
    (1, -4),
    (1, -1),
    (3, -1),
    (3, -3),
    (0, -3),
]


class TestDiagram(unittest.TestCase):
    def test_auto_close(self):
        # Given
        open_trefoil = LineString(TREFOIL)
        self.assertFalse(open_trefoil.is_closed)

        # When
        diagram = Diagram(line=open_trefoil)
        resulting = diagram.line

        # Then
        self.assertTrue(resulting.is_closed)
        # same thing
        self.assertEqual(resulting.coords[-1], (0.0, 0.0))
