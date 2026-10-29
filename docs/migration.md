# Tailgap naming and compatibility

The software and repository are named **Tailgap**, matching the paper.
Install this repository with `python -m pip install -e .`, import from `tailgap`,
and use `tailgap` or `python -m tailgap` for commands.

| Earlier entrypoint | Tailgap entrypoint |
| --- | --- |
| `from rsfm_fairness_audit import BWERProtocol, audit` | `from tailgap import TailgapProtocol, audit` |
| `run_geobwer_model_panel` | `from tailgap import run_model_panel` |
| `rsfm-audit geobwer-audit` | `tailgap audit` |
| `rsfm-audit geobwer-compare` | `tailgap compare` |
| `rsfm-audit geobwer-inventory` | `tailgap inventory` |
| `rsfm-audit geobwer-multiclass-uncertainty` | `tailgap multiclass-uncertainty` |
| `rsfm-audit geobwer-multilabel-uncertainty` | `tailgap multilabel-uncertainty` |
| `rsfm-audit geobwer-spatial-conformal-upgrade` | `tailgap spatial-conformal-upgrade` |

The previous imports and `rsfm-audit` commands continue to work. Other command
names and arguments are unchanged. The public API calls the same implementation;
`TailgapProtocol` is an alias of the existing protocol class.

Scientific protocol identifiers, hashes, configuration paths under
`configs/geobwer/`, experiment script filenames, serialized class locations,
and output filenames/fields such as `bwer` and `geobwer_*` remain stable.
The excess-risk quantity D remains T - M. Existing artifacts require no renaming
or recomputation. This naming update does not change the estimand, inference,
support thresholds, or calibration requirements.

If an environment already has the earlier `geobwer-release` editable distribution,
uninstall it before installing Tailgap, or create a fresh virtual environment.
Installing both distributions into one environment is unsupported because the
compatibility implementation has the same import namespace.
