"""Actual workflow policy mutants for signed disposable-runner APT acquisition. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 54
# definition: validate_jobs — line 57
# parameter: document — line 57
# variable: found — line 59
# variable: job — line 60
# variable: steps — line 61
# variable: apt — line 62
# variable: i — line 62
# variable: s — line 62
# variable: guards — line 65
# variable: i — line 67
# variable: s — line 67
# variable: s — line 71
# variable: text — line 73
# variable: required — line 74
# variable: i — line 88
# variable: found — line 93
# definition: workflow — line 97
# variable: source — line 99
# variable: body — line 100
# variable: jobs — line 101
# variable: match — line 102
# variable: steps — line 105
# variable: block — line 106
# variable: item — line 107
# variable: key — line 108
# variable: field — line 109
# variable: item — line 116
# definition: test_actual_signed_runner_acquisition_policy — line 125
# definition: test_actual_workflow_admission_mutants — line 133
# parameter: mutation — line 133
# variable: doc — line 135
# variable: job — line 136
# variable: j — line 138
# variable: s — line 139
# variable: steps — line 141
# variable: i — line 142
# variable: i — line 144
# variable: s — line 144
# variable: s — line 152
# variable: target — line 152
# variable: new — line 155
# variable: old — line 155
# END CODE MAP

import re
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def validate_jobs(document):
    """Require admission before each APT job; ordinary tests/packages remain mandatory and no trust bypass exists."""
    found = 0
    for job in document["jobs"].values():
        steps = job.get("steps", [])
        apt = [i for i, s in enumerate(steps) if "apt-get" in s.get("run", "")]
        if not apt:
            continue
        guards = [
            i
            for i, s in enumerate(steps)
            if s.get("name") == "Bound official mirror access on the disposable Ubuntu runner"
        ]
        assert len(guards) == 1 and guards[0] < min(apt)
        s = steps[guards[0]]
        assert s["if"] == "runner.os == 'Linux'" and s["timeout-minutes"] == "1"
        text = s["run"]
        for required in [
            'test "$GITHUB_ACTIONS" = "true"',
            'test "$RUNNER_OS" = "Linux"',
            'test "$ID" = "ubuntu"',
            'test "$VERSION_ID" = "24.04"',
            "/usr/share/keyrings/ubuntu-archive-keyring",
            "^Signed-By:",
            "https://archive.ubuntu.com/ubuntu/",
            "https://security.ubuntu.com/ubuntu/",
            'Acquire::Retries "0";',
            'Acquire::https::Timeout "15";',
            "apt-config dump",
        ]:
            assert required in text
        for i in apt:
            assert (
                "--allow-unauthenticated" not in steps[i]["run"]
                and "|| true" not in steps[i]["run"]
            )
        found += 1
    assert found >= 1


def workflow():
    """Read the actual authored source, including all original source/sanitizer/native jobs."""
    source = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf8")
    body = source.split("\njobs:\n", 1)[1]
    jobs = {}
    for match in re.finditer(
        r"^  ([a-z][a-z0-9-]*):\n(.*?)(?=^  [a-z][a-z0-9-]*:|\Z)", body, re.M | re.S
    ):
        steps = []
        for block in re.findall(r"^      - .*?(?=^      - |\Z)", match[2], re.M | re.S):
            item = {}
            for key in ("name", "if", "timeout-minutes", "run"):
                field = re.search(r"^ {6,8}(?:- )?" + key + r": (.*)$", block, re.M)
                if field:
                    item[key] = (
                        block[field.end() :] if key == "run" and field[1] == "|" else field[1]
                    )
            steps.append(item)
        if "apt-get" in match[2]:
            assert any("apt-get" in item.get("run", "") for item in steps), (
                "Unsupported APT step layout"
            )
        jobs[match[1]] = {"steps": steps}
    # This is an intentionally narrow authored-step contract. Native actionlint
    # separately parses the complete YAML; this helper is not a YAML parser.
    return {"jobs": jobs}


def test_actual_signed_runner_acquisition_policy():
    """The actual whole workflow must keep signed source admission before all APT consumers."""
    validate_jobs(workflow())


@pytest.mark.parametrize(
    "mutation", ["missing", "late", "signature", "remotehost", "retry", "ignoreauth"]
)
def test_actual_workflow_admission_mutants(mutation):
    """Real YAML mutations cannot silently remove ordering/keyring/host/no-retry constraints or weaken authentication."""
    doc = deepcopy(workflow())
    job = next(
        j
        for j in doc["jobs"].values()
        if any("apt-get" in s.get("run", "") for s in j.get("steps", []))
    )
    steps = job["steps"]
    i = next(
        i
        for i, s in enumerate(steps)
        if s.get("name") == "Bound official mirror access on the disposable Ubuntu runner"
    )
    if mutation == "missing":
        steps.pop(i)
    elif mutation == "late":
        steps.append(steps.pop(i))
    elif mutation == "ignoreauth":
        target = next(s for s in steps if "apt-get" in s.get("run", ""))
        target["run"] += " --allow-unauthenticated"
    else:
        old, new = {
            "signature": ("^Signed-By:", "^Unverified:"),
            "remotehost": (
                "https://archive.ubuntu.com/ubuntu/",
                "https://foreign.invalid/ubuntu/",
            ),
            "retry": ('Acquire::Retries "0";', 'Acquire::Retries "3";'),
        }[mutation]
        steps[i]["run"] = steps[i]["run"].replace(old, new)
    with pytest.raises(AssertionError):
        validate_jobs(doc)
