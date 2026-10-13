"""Disposable authored release fixtures; fake hashes are never real attestations. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: policy — line 23
# definition: release — line 29
# parameter: policy — line 29
# parameter: tmp_path — line 29
# variable: output — line 31
# END CODE MAP

from pathlib import Path

import pytest
from hypothesis import settings

from delivery.build import build_release
from delivery.verify import REPOSITORY, TrustPolicy

settings.register_profile("ci", max_examples=100, derandomize=True, deadline=None)
settings.load_profile("ci")


@pytest.fixture
def policy() -> TrustPolicy:
    """Return an explicitly fictional source SHA for isolated unit tests only."""
    return TrustPolicy(REPOSITORY, "a" * 40, "1.0.0")


@pytest.fixture
def release(tmp_path: Path, policy: TrustPolicy) -> Path:
    """Build a deterministic unsigned test bundle using only authored source files."""
    output = tmp_path / "release"
    build_release(Path(__file__).resolve().parents[1], output, policy, {"fixture": True})
    return output
