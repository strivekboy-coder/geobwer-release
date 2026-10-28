# GeoBWER

GeoBWER measures geospatial deployment-tail risk from normalized audit tables.
It reports deployment mean risk **M**, fractional upper-tail risk **T**, and
excess risk **D = T - M**, alongside support and inference validity.
Read M, T, and D jointly: a smaller disparity alone need not imply less risk.

This repository contains code and scientific configuration for four tasks:
fMoW-Sentinel scene classification, reBEN multi-label classification and paired
sensor shift, Sen1Floods11 segmentation, and AlphaEarth–WorldCover reference-map
agreement. Historical BWER helpers remain where required by model adapters and
regression tests; use the GeoBWER API/configuration for the paper protocol.

## Install

Python 3.10+ and Git are required. The lock records the verified Windows,
Python 3.12 CPU environment. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/strivekboy-coder/geobwer-release.git
cd geobwer-release
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell, or
`source .venv/bin/activate` in bash. Then install and verify:

```bash
python -m pip install -r requirements-test.lock.txt
python -m pip install --no-deps -e .
python -m pip check
python -m pytest -q
```

For an unpinned development install, use `python -m pip install -e ".[test]"`.
Model tests use PyTorch on CPU. GPU inference requires compatible model/runtime
dependencies and the official checkpoints. See [model environments](docs/models.md).

## Minimal API example

```python
from rsfm_fairness_audit import BWERProtocol, audit

protocol = BWERProtocol(beta=0.10, audit_measure="raw")
result = audit(
    loss=[0.0, 0.2, 0.8, 1.0],
    groups=["region_a", "region_a", "region_b", "region_b"],
    unit_id=["a1", "a2", "b1", "b2"],
    protocol=protocol,
)
```

This invented four-row example demonstrates the API only. It does not establish
formal inference or reproduce the paper's data/results. Formal runs must satisfy
their registered independent-unit, support, cluster, and calibration requirements.

## Reproduce the research workflow

1. Obtain data and checkpoints from the [official sources](docs/data.md).
2. Prepare local manifests/chips and check leakage, band order and scale.
3. Run the selected model with the task protocol; retain prediction lineage.
4. Run support/preflight checks before formal GeoBWER or uncertainty analysis.
5. Run task comparisons and the [paper and supplementary analyses](docs/reproduction.md).
6. Generate tables/figures from your resulting metrics; preserve input hashes.

Use the directory conventions in [configs/inputs.example.yaml](configs/inputs.example.yaml).
Every runner documents its actual arguments with `--help`; this example file is
a directory guide, not an implicit configuration loader for all runners.
Data, checkpoints, embeddings, frozen predictions, browser files, and internal
documents are intentionally absent. No private Drive file identifier is required.
The same raw data alone is insufficient to match frozen results: checkpoint,
preprocessing, split manifests, seeds, probability/label mappings, and calibration
contracts must also match. This release does not claim that those external assets
have been deposited or that a CPU test run reproduces the published numbers.

## Tests and validation

Tests use synthetic inputs and temporary working directories. They do not read
an author's existing `outputs/` directory or download model weights.
[Validation](docs/validation.md) records the executed suite and release scan.
Optional real-data/GPU workflows are documented separately from unit tests.

## Citation and license

Software author: **Weilun Zhong**. See [CITATION.cff](CITATION.cff).
Project code is distributed under the [MIT License](LICENSE). External datasets,
model implementations, checkpoints, and services keep their own licenses/terms;
the project license does not grant rights to redistribute those materials.
