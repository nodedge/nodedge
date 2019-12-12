#!/usr/bin/env python

"""Tests for `nodeledge` package."""


import unittest
from nodeledge.ack_scene import AckScene


class TestNodeledge(unittest.TestCase):
    """Tests for `nodeledge` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_sceneGotHasBeenModifiedProperty(self):
        """Test if scene got hasBeenModified property."""
        assert(hasattr(AckScene, "hasBeenModified"))
