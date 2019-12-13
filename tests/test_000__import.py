#!/usr/bin/env python

"""Tests for `nodedge` package."""


import unittest
from nodedge.scene import Scene


class TestNodedge(unittest.TestCase):
    """Tests for `nodedge` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_sceneGotHasBeenModifiedProperty(self):
        """Test if scene got hasBeenModified property."""
        assert(hasattr(Scene, "hasBeenModified"))
