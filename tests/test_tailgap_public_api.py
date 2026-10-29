"""Exercise the public name against the established scientific contracts."""
import argparse
from pathlib import Path

import pytest
import rsfm_fairness_audit as legacy
from rsfm_fairness_audit import cli as legacy_cli
import tailgap
from tailgap.cli import build_parser, main


def test_public_api_preserves_protocol_and_implementation():
    assert tailgap.TailgapProtocol is legacy.BWERProtocol
    assert tailgap.audit is legacy.audit
    assert tailgap.run_model_panel is legacy.run_geobwer_model_panel
    assert tailgap.TailgapProtocol().signature == legacy.BWERProtocol().signature


def test_readme_example_reports_same_risks():
    protocol = tailgap.TailgapProtocol(
        beta=0.25, audit_measure="observed", deployment_weighting="empirical",
        inference_method="none", dependence_design="fixed_universe_descriptive",
    )
    point = tailgap.audit(
        loss=[0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.8, 0.8],
        groups=["a", "a", "b", "b", "c", "c", "d", "d"],
        unit_id=[f"sample_{i}" for i in range(8)], protocol=protocol,
    ).axes[0].point
    assert point.mean_risk == pytest.approx(0.35)
    assert point.tail_risk == pytest.approx(0.8)
    assert point.bwer == pytest.approx(0.45)


def test_every_command_retains_argument_defaults_and_validation():
    def commands(parser):
        return next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices
    old = commands(legacy_cli.build_parser())
    new = commands(build_parser())
    assert set(new) == {name.removeprefix("geobwer-") for name in old}
    for name, command in old.items():
        original = [a for a in command._actions if a.dest not in {"command", "help"}]
        public = [a for a in new[name.removeprefix("geobwer-")]._actions if a.dest not in {"command", "help"}]
        assert [(a.dest, a.required, a.default, a.type, a.choices) for a in public] == [
            (a.dest, a.required, a.default, a.type, a.choices) for a in original
        ]
    args = build_parser().parse_args(["audit", "--audit-table", "input.csv", "--output-dir", "out"])
    assert args.command == "geobwer-audit"
    assert args.diagnostic is False
    assert args.protocol == Path("configs/geobwer/default.yaml")
    with pytest.raises(SystemExit):
        build_parser().parse_args(["audit"])


def test_inventory_command_dispatches_to_existing_engine(tmp_path, capsys):
    output = tmp_path / "inventory"
    main(["inventory", "--input", str(tmp_path / "missing.csv"), "--output-dir", str(output)])
    assert output.is_dir()
    assert list(output.glob("*.json"))
    assert "inventory complete" in capsys.readouterr().out


def test_public_help_uses_tailgap(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    text = capsys.readouterr().out
    assert "usage: tailgap " in text
    assert "Tailgap" in text
    assert "GeoBWER" not in text
