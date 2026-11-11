"""Independent exact-cent and unauthenticated-release boundaries for the actual offline GUI adapter. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: execute — line 78
# parameter: parameters — line 78
# parameter: tmp_path — line 78
# variable: stage — line 80
# variable: state — line 84
# variable: files — line 85
# variable: kind — line 85
# variable: summary — line 85
# variable: identity — line 86
# definition: test_actual_inventory_exact_cent_oracles — line 94
# parameter: expected — line 94
# parameter: index — line 94
# parameter: tmp_path — line 94
# variable: _ — line 96
# variable: files — line 96
# variable: summary — line 96
# variable: result — line 97
# variable: row — line 102
# definition: test_real_unsigned_preflight_never_becomes_authentication — line 107
# parameter: index — line 107
# parameter: tmp_path — line 107
# variable: _ — line 109
# variable: files — line 109
# variable: summary — line 109
# variable: result — line 110
# variable: rows — line 120
# variable: row — line 121
# definition: test_actual_file_picker_input_stays_private_and_unchanged — line 124
# parameter: tmp_path — line 124
# variable: source — line 126
# variable: raw — line 127
# variable: parameters — line 129
# variable: _ — line 131
# variable: files — line 131
# variable: result — line 132
# definition: test_rewritten_matching_manifest_is_still_only_integrity — line 138
# parameter: tmp_path — line 138
# variable: source — line 140
# variable: policy — line 141
# variable: manifest — line 142
# variable: validation — line 143
# variable: row — line 145
# variable: parameters — line 148
# variable: _ — line 150
# variable: files — line 150
# variable: result — line 151
# definition: test_independent_identity_and_exact_asset_refusals — line 168
# parameter: fault — line 168
# parameter: tmp_path — line 168
# variable: source — line 170
# variable: parameters — line 172
# variable: name — line 175
# variable: path — line 184
# definition: test_invalid_real_inventory_retains_original_schema — line 198
# parameter: rows — line 198
# parameter: tmp_path — line 198
# variable: source — line 200
# variable: parameters — line 202
# definition: test_no_unknown_mode_or_prepared_execution_path — line 208
# parameter: tmp_path — line 208
# variable: parameters — line 212
# END CODE MAP

import hashlib
import json
from contextlib import closing

import pytest

from delivery import desktop_project as project
from delivery.desktop_io import canonical, json_value
from delivery.desktop_state import Workspace
from delivery.verify import TrustPolicy


def execute(tmp_path, parameters):
    """Use a fresh real owned workspace and analysis directory, with no attestation mock or executed payload."""
    stage = tmp_path / "stage"
    stage.mkdir()
    with closing(
        Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT, synthetic=True)
    ) as state:
        kind, summary, files = project.analyze(state, parameters, stage)
        identity = state.save(kind, summary, parameters, files)
        assert state.files(identity) == files
        return kind, summary, files


@pytest.mark.parametrize(
    "index,expected", [(0, "1727.40"), (1, "0.30"), (2, "0.00"), (3, "19999999999.98")]
)
def test_actual_inventory_exact_cent_oracles(tmp_path, index, expected):
    """Literal monetary oracles independently verify totals and per-stock contributions without binary floats."""
    _, summary, files = execute(tmp_path, project.scenario(project.SCENARIOS[index]))
    result = json_value(files["inventory.json"])
    assert result["totals"]["inventory_value_usd"] == expected and expected in summary
    assert len(result["products"]) == result["totals"]["products"]
    assert project.views(files)["Stock and exact values"]
    assert all(
        "USD" in project.cells(row)[2] for row in project.views(files)["Stock and exact values"]
    )


@pytest.mark.parametrize("index", [4, 5])
def test_real_unsigned_preflight_never_becomes_authentication(tmp_path, index):
    """Original real preflight accepts bounded fixture bytes while every authentication/execution claim stays false."""
    _, summary, files = execute(tmp_path, project.scenario(project.SCENARIOS[index]))
    result = json_value(files["preflight.json"])
    assert result["status"] == "INTEGRITY_ONLY_NOT_AUTHENTICATED"
    assert (
        result["authentication_verified"]
        is result["signer_workflow_verified"]
        is result["execution_permitted"]
        is False
    )
    assert result["prepared_unsigned_fixture"] is True and "NOT AUTHENTICATED" in summary
    assert len(result["manifest"]["assets"]) == 3 and len(result["members"]) == 6
    for rows in project.views(files).values():
        assert all(len(project.cells(row)) == 4 for row in rows)


def test_actual_file_picker_input_stays_private_and_unchanged(tmp_path):
    """A selected real JSON stock file produces actual totals without exporting its private source path."""
    source = tmp_path / "private-stock.json"
    raw = canonical([{"id": "PRIVATE-STOCK", "units": 3, "unit_price_usd": "0.10"}])
    source.write_bytes(raw)
    parameters = project.scenario(project.SCENARIOS[0])
    parameters.update(mode=project.MODES[0], inventory=str(source))
    _, _, files = execute(tmp_path, parameters)
    result = json_value(files["inventory.json"])
    assert result["totals"] == {"products": 1, "units": 3, "inventory_value_usd": "0.30"}
    assert result["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert str(source).encode() not in files["inventory.json"] and source.read_bytes() == raw


def test_rewritten_matching_manifest_is_still_only_integrity(tmp_path):
    """Model the key limitation: a rewritten unsigned payload+matching hash may pass structure, never signer trust."""
    source = tmp_path / "unsigned"
    policy = project.unsigned_fixture(source, changed=True)
    manifest = json.loads((source / "release.json").read_bytes())
    validation = b'{"attacker_can_rewrite_matching_hashes":true}\n'
    (source / "validation.json").write_bytes(validation)
    row = next(row for row in manifest["assets"] if row["name"] == "validation.json")
    row.update(size=len(validation), sha256=hashlib.sha256(validation).hexdigest())
    (source / "release.json").write_bytes(canonical(manifest))
    parameters = project.scenario(project.SCENARIOS[4])
    parameters.update(mode=project.MODES[1], directory=str(source))
    _, _, files = execute(tmp_path, parameters)
    result = json_value(files["preflight.json"])
    assert result["authentication_verified"] is False and result["execution_permitted"] is False
    assert result["expected_identity"]["commit"] == policy.commit
    assert "attacker_can_rewrite" not in files["preflight.json"].decode()


@pytest.mark.parametrize(
    "fault",
    [
        "wrong-commit",
        "wrong-version",
        "wrong-repository",
        "extra-file",
        "tamper",
        "duplicate-manifest-key",
    ],
)
def test_independent_identity_and_exact_asset_refusals(tmp_path, fault):
    """Real original preflight rejects altered bytes, unsupported directory contents and mismatched caller identities."""
    source = tmp_path / "release-input"
    project.unsigned_fixture(source)
    parameters = project.scenario(project.SCENARIOS[4])
    parameters.update(mode=project.MODES[1], directory=str(source))
    if fault.startswith("wrong-"):
        name = fault.removeprefix("wrong-")
        parameters[name] = {"commit": "b" * 40, "version": "9.0.0", "repository": "Other/repo"}[
            name
        ]
    elif fault == "extra-file":
        (source / "extra.txt").write_text("not admitted")
    elif fault == "tamper":
        (source / "validation.json").write_bytes(b"tampered")
    else:
        path = source / "release.json"
        path.write_bytes(path.read_bytes().replace(b'"schema":1', b'"schema":1,"schema":1'))
    with pytest.raises(ValueError):
        execute(tmp_path, parameters)


@pytest.mark.parametrize(
    "rows",
    [
        [{"id": "A", "units": True, "unit_price_usd": "0.10"}],
        [{"id": "A", "units": 1, "unit_price_usd": 0.10}],
        [{"id": "A", "units": 1, "unit_price_usd": "0.10"}] * 2,
    ],
)
def test_invalid_real_inventory_retains_original_schema(tmp_path, rows):
    """Boolean units, floating prices and duplicate IDs remain errors instead of coerced GUI defaults."""
    source = tmp_path / "invalid.json"
    source.write_bytes(canonical(rows))
    parameters = project.scenario(project.SCENARIOS[0])
    parameters.update(mode=project.MODES[0], inventory=str(source))
    with pytest.raises(ValueError):
        execute(tmp_path, parameters)


def test_no_unknown_mode_or_prepared_execution_path(tmp_path):
    """Only reviewed modes/exercises and independently valid source policies are selectable."""
    with pytest.raises(ValueError):
        project.scenario("execute incoming zipapp")
    parameters = project.scenario(project.SCENARIOS[0])
    parameters["mode"] = "promote"
    with pytest.raises(ValueError):
        execute(tmp_path, parameters)
    parameters.update(mode=project.MODES[2], exercise="foreign")
    with pytest.raises(ValueError):
        project.analyze(None, parameters, tmp_path)
    with pytest.raises(ValueError):
        project.inventory_example("foreign")
    with pytest.raises(ValueError):
        TrustPolicy(project.REPOSITORY, "b" * 40, "1.2.0", "../foreign")
