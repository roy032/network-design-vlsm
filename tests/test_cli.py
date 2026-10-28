from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tests.conftest import ROOT, SPEC
from vlsmkit.cli import main


def test_plan_table(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["plan", "192.168.0.0/24", "A=50", "B=20", "C=2"]) == 0
    out = capsys.readouterr().out
    assert "| A | 50 | 62 | 192.168.0.0/26 |" in out
    assert "192.168.0.64/27" in out


def test_plan_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["plan", "10.0.0.0/8", "Dog=1200", "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["network"] == "10.0.0.0/21"
    assert data[0]["wildcard"] == "0.0.7.255"


def test_plan_tree(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["plan", "10.0.0.0/24", "A=100", "B=50", "--format", "tree"]) == 0
    out = capsys.readouterr().out
    assert "10.0.0.0/25  <- A" in out
    assert "10.0.0.192/26  (free)" in out


def test_plan_errors(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["plan", "10.0.0.0/30", "A=100"]) == 2
    assert "error:" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        main(["plan", "10.0.0.0/8", "nohosts"])


def test_repository_generated_files_are_current(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--spec", str(SPEC), "--out", str(ROOT)]) == 0
    assert "OK" in capsys.readouterr().out


def test_build_then_check_and_detect_drift(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec = tmp_path / "network.toml"
    shutil.copy(SPEC, spec)
    assert main(["check", "--spec", str(spec), "--out", str(tmp_path)]) == 1
    assert main(["build", "--spec", str(spec), "--out", str(tmp_path)]) == 0
    assert (tmp_path / "configs" / "R-Lion.ios").exists()
    assert main(["check", "--spec", str(spec), "--out", str(tmp_path)]) == 0

    cfg = tmp_path / "configs" / "R-Dog.ios"
    cfg.write_text(cfg.read_text().replace("10.0.0.1", "10.0.0.99"))
    capsys.readouterr()
    assert main(["check", "--spec", str(spec), "--out", str(tmp_path)]) == 1
    assert "STALE" in capsys.readouterr().out


def test_check_fails_on_unreachable_lan(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    spec = tmp_path / "network.toml"
    spec.write_text(SPEC.read_text().replace('redistribute = ["static"]', "redistribute = []"))
    main(["build", "--spec", str(spec), "--out", str(tmp_path)])
    capsys.readouterr()
    assert main(["check", "--spec", str(spec), "--out", str(tmp_path)]) == 1
    assert "UNREACHABLE" in capsys.readouterr().out


def test_invalid_spec_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    spec = tmp_path / "network.toml"
    broken = SPEC.read_text().replace('subnet = "lion-lan"\nhost = 2', 'subnet = "x"\nhost = 2')
    spec.write_text(broken)
    assert main(["build", "--spec", str(spec), "--out", str(tmp_path)]) == 2
    assert "unknown subnet 'x'" in capsys.readouterr().err


def test_ping_and_routes(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["ping", "10.0.0.2", "10.0.12.130", "--spec", str(SPEC)]) == 0
    assert "R-Dog -> R-Elephant -> R-Lion" in capsys.readouterr().out
    assert main(["ping", "10.0.0.2", "10.0.12.145", "--spec", str(SPEC)]) == 1
    assert main(["routes", "R-Cat", "--spec", str(SPEC)]) == 0
    assert "O E2 10.0.12.128/28" in capsys.readouterr().out
    assert main(["routes", "R-Nope", "--spec", str(SPEC)]) == 2
