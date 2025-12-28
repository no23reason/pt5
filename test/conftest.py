import os

import pytest

__current_dir__ = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def simple_ncp():
    with open(os.path.join(__current_dir__, "fixtures/simple.ncp")) as f:
        yield f


@pytest.fixture
def switching_modes_ncp():
    with open(os.path.join(__current_dir__, "fixtures/switching_modes.ncp")) as f:
        yield f
