import unittest

from shapely.geometry import LineString
from traits.api import TraitError

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
        self.assertEqual(len(resulting.coords), len(TREFOIL) + 1)

    def test_do_not_close_if_unnecessary(self):
        # Given
        close_trefoil_list = TREFOIL + [(0, 0)]
        close_trefoil = LineString(close_trefoil_list)
        self.assertTrue(close_trefoil.is_closed)

        # When
        diagram = Diagram(line=close_trefoil)
        resulting = diagram.line

        # Then
        self.assertEqual(len(resulting.coords), len(close_trefoil.coords))

    def test_create_from_coords(self):
        # When/Then
        try:
            Diagram(line=TREFOIL)
        except Exception:
            self.fail("Should have worked")

    def test_create_from_other(self):
        # When/Then
        with self.assertRaises(TraitError):
            # Tuples are rejected by type validation
            Diagram(line=((9, 1), (1, 1)))

        # When/Then
        with self.assertRaises(ValueError):
            # List of non-coords rejected by shapely
            Diagram(line=["a", "b"])
