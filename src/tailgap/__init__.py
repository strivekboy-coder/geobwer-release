"""Tailgap: support-aware geospatial deployment-tail risk auditing.

Public names delegate to the established implementation so protocol identities,
result schemas, and previously serialized experiments remain compatible.
"""
from rsfm_fairness_audit import (
    __version__, BWERProtocol, Protocol, EvidenceStatus, Validity, RiskSpec,
    SpatialConformalConfig, audit, audit_rows, compare, confirm,
    run_geobwer_model_panel, run_multiclass_spatial_upgrade,
    run_multiclass_uncertainty_suite, run_multilabel_uncertainty_suite,
    run_segmentation_uncertainty_suite,
)

TailgapProtocol = BWERProtocol
run_model_panel = run_geobwer_model_panel

__all__ = [
    "__version__", "TailgapProtocol", "Protocol", "EvidenceStatus", "Validity",
    "RiskSpec", "SpatialConformalConfig", "audit", "audit_rows", "compare",
    "confirm", "run_model_panel", "run_multiclass_spatial_upgrade",
    "run_multiclass_uncertainty_suite", "run_multilabel_uncertainty_suite",
    "run_segmentation_uncertainty_suite",
]
