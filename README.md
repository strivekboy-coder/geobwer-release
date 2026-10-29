# GeoBWER

**Geospatial deployment-tail risk auditing for remote sensing.**

GeoBWER examines how prediction risk is distributed across deployment slices,
such as countries, locations, events, and classes. It complements aggregate
performance by measuring the concentration of risk in the upper tail of a
specified deployment distribution.

The method reports three quantities together:

- **M — mean risk:** average risk under the chosen deployment weights.
- **T — tail risk:** average risk in the worst-performing fraction `beta` of deployment mass, using fractional tail allocation.
- **D — excess risk:** the difference `T - M`.

Read M, T, and D jointly: a smaller excess risk can coexist with higher mean
and tail risks.

## Features

- Observed-risk and composition-standardised slice audits.
- Explicit deployment weights, tail fractions, and protocol identities.
- Support-aware validity states and partial-identification bounds.
- Cluster-aware uncertainty and spatial analyses subject to the specified support and calibration requirements.
- Paired model comparisons on common support.
- Risk profiles, tables, figures, and structured reports.

GeoBWER operates on losses or normalised audit tables. Task adapters connect
classification, multi-label classification, segmentation, and reference-map
agreement workflows to the same audit framework.

## Installation

Python 3.10+ and Git are required. The pinned environment was verified on
Windows with Python 3.12 and CPU PyTorch.

```bash
git clone https://github.com/strivekboy-coder/geobwer-release.git
cd geobwer-release
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell, or
`source .venv/bin/activate` in bash. Then install:

```bash
python -m pip install -r requirements-test.lock.txt
python -m pip install --no-deps -e .
```

For a development install, use `python -m pip install -e ".[test]"`.
Task-specific model environments are described in [model environments](docs/models.md).

## Quick start

This small synthetic example computes descriptive point estimates for four
equally represented regions:

```python
from rsfm_fairness_audit import BWERProtocol, audit

protocol = BWERProtocol(
    beta=0.25,
    audit_measure="observed",
    deployment_weighting="empirical",
    inference_method="none",
    dependence_design="fixed_universe_descriptive",
)

result = audit(
    loss=[0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.8, 0.8],
    groups=["a", "a", "b", "b", "c", "c", "d", "d"],
    unit_id=[f"sample_{i}" for i in range(8)],
    protocol=protocol,
)

point = result.axes[0].point
print(f"M={point.mean_risk:.3f}, T={point.tail_risk:.3f}, D={point.bwer:.3f}")
# M=0.350, T=0.800, D=0.450
```

For inferential analyses, specify the task protocol, independent units,
clusters or spatial blocks, and applicable support/calibration requirements.

## Applications

| Dataset / representation | Task | Example audit slices |
| --- | --- | --- |
| fMoW-Sentinel | Scene classification | Country, location, category |
| reBEN / BigEarthNet | Multi-label classification and paired sensor shift | Country, label, country × label |
| Sen1Floods11 | Flood segmentation | Disaster event |
| AlphaEarth–WorldCover | Reference-map agreement | Country, reference class |

Task protocols and experiment entrypoints are listed in the
[reproduction guide](docs/reproduction.md).

## Repository structure

```text
src/rsfm_fairness_audit/  Core methods, task adapters, and analysis modules
scripts/                 Data preparation, experiment, and plotting entrypoints
configs/                 Scientific protocols and model/task settings
tests/                   Mathematical, adapter, and workflow regression tests
docs/                    Data, model, reproduction, and validation guides
```

## Documentation and tests

- [Data sources and preparation](docs/data.md)
- [Model environments](docs/models.md)
- [Experiment and analysis entrypoints](docs/reproduction.md)
- [Input directory conventions](configs/inputs.example.yaml)
- [Validation coverage](docs/validation.md)

```bash
python -m pip check
python -m pytest -q
```

## Citation and license

Software author: **Weilun Zhong**. Citation metadata is provided in
[CITATION.cff](CITATION.cff).

Project code is distributed under the [MIT License](LICENSE). External datasets,
checkpoints, and model implementations retain their respective licenses.
