from __future__ import annotations

import copy
import tomllib
from pathlib import Path
from typing import Any

import pytest

from vlsmkit.spec import Network, load

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "network.toml"


@pytest.fixture(scope="session")
def network() -> Network:
    return load(SPEC)


@pytest.fixture
def raw_spec() -> dict[str, Any]:
    """A fresh, mutable copy of the decoded spec for negative tests."""
    with SPEC.open("rb") as fh:
        return copy.deepcopy(tomllib.load(fh))
