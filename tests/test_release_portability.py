"""Release contracts exercised entirely with invented inputs."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from rsfm_fairness_audit.evidence_registry import load_canonical_evidence_registry

ROOT = Path(__file__).resolve().parents[1]


def test_asset_registry_accepts_explicit_local_inputs_without_remote_identifiers(tmp_path):
    path = tmp_path / "registry.json"
    asset = dict(asset_id="fixture", task="test", role="input", status="canonical_source",
                 local_path="data/fixture.csv", immutable=True, allowed_use=["test"])
    payload = dict(schema="geobwer.canonical_evidence_registry.v1", assets=[asset])
    path.write_text(json.dumps(payload), encoding="utf-8")
    registry = load_canonical_evidence_registry(path)
    assert registry.resolve(task="test", role="input").drive_path == "data/fixture.csv"
    del asset["local_path"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="explicit local_path"):
        load_canonical_evidence_registry(path)


def test_paper_builder_rejects_missing_inputs_before_creating_results(tmp_path):
    source = tmp_path / "empty"
    source.mkdir()
    output = tmp_path / "results"
    command = [sys.executable, str(ROOT / "scripts/analysis/build_final_paper_package.py"),
               "--source-dir", str(source), "--output-dir", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Missing paper inputs" in result.stderr
    assert not output.exists()


def test_paper_builder_computes_tables_and_figures_from_supplied_metrics(tmp_path):
    source = tmp_path / "input"
    source.mkdir()
    output = tmp_path / "results"

    def save(name, rows):
        with (source / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    exp9 = []
    stages = []
    recovery = []
    for seed in (42, 73, 101):
        for task in ("fmow", "reben"):
            for model, risk in (("dofav2", .8), ("terramind", .6)):
                exp9.append(dict(task=task, model=model, seed=seed, primary_risk=risk,
                                 M=risk, T=risk+.1, D=.1))
        for stage, split in (("A", "test_id"), ("A", "test_shifted"), ("B", "test"), ("C", "test")):
            stages.append(dict(seed=seed, stage=stage, split_role=split, macro_auroc=.8,
                               mean_risk=.2, tail_risk_beta_0_10=.3, geobwer_beta_0_10=.1))
        for stage in ("B", "C"):
            for metric in ("macro_auroc", "mean_risk", "tail_risk_beta_0_10", "geobwer_beta_0_10"):
                recovery.append(dict(seed=seed, stage=stage, split_role="test", metric=metric, recovery=.5))
    labels = []
    burden = []
    for index, label in enumerate(("A", "B", "C", "D")):
        labels.append(dict(class_label=label, mean_delta_auroc=-.2, mean_delta_ap=-.3,
                           mean_delta_predicted_positive_rate=(.8, .7, -.3, -.5)[index]))
        for country, delta, positive in (("X", .9-index*.1, 3), ("Y", -.1-index*.1, 0)):
            burden.append(dict(country=country, class_label=label, seed_count=3, mean_delta_risk=delta,
                               delta_risk_sd=.01, positive_seed_count=positive, minimum_cell_support=2000))
    save("experiment9_cell_seed_metrics.csv", exp9)
    save("experiment8_adaptation_stage_metrics.csv", stages)
    save("experiment8_adaptation_recovery.csv", recovery)
    save("reben_terramind_country_label_burden.csv", burden)
    save("reben_terramind_label_diagnostics.csv", labels)
    croma = [{**row, "mean_delta_predicted_positive_rate": (.1, -.2, .4, .2)[index]}
             for index, row in enumerate(labels)]
    save("reben_croma_label_diagnostics.csv", croma)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    result = subprocess.run([sys.executable, str(ROOT / "scripts/analysis/build_final_paper_package.py"),
                             "--source-dir", str(source), "--output-dir", str(output)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["source_sha256"] == before
    assert manifest["source_immutable"] is True
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()} == before
    assert len(list((output / "figures").glob("*.png"))) == 3
    assert len(list((output / "figures").glob("*.pdf"))) == 3
    with (output / "tables/experiment9_summary.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert all(abs(float(r["mean_delta_dofav2_minus_terramind"])-.2) < 1e-12
               for r in rows if r["metric"] == "M")
