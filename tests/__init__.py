# -*- coding: utf-8 -*-

from contextlib import contextmanager

import pytest


@contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"{exception}")
