"""Shared reference-product diagnostics; no embedded scientific result snapshots."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Mapping, Sequence
import numpy as np
from rsfm_fairness_audit.io import read_csv_rows


REQUIRED_DW_COLUMNS = ["sample_id", "dynamic_world_label"]


PLACEHOLDER_VALUES = {"", "-1", "None", "none", "nan", "NaN"}


DW_CONFIDENCE_ALIASES = ["dw_confidence", "dynamic_world_confidence", "dw_top_probability", "dynamic_world_top_probability"]


DW_ENTROPY_ALIASES = ["dw_entropy", "dynamic_world_entropy"]


DW_TO_WORLDCOVER = {
    "0": "80",  # water
    "1": "10",  # trees
    "2": "30",  # grass
    "3": "90",  # flooded vegetation
    "4": "40",  # crops
    "5": "20",  # shrub and scrub
    "6": "50",  # built
    "7": "60",  # bare
    "8": "70",  # snow and ice
    "water": "80",
    "trees": "10",
    "grass": "30",
    "flooded_vegetation": "90",
    "crops": "40",
    "shrub_and_scrub": "20",
    "built": "50",
    "bare": "60",
    "snow_and_ice": "70",
}


def _float(value: Any, default: float = float("nan")) -> float:
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _read(path: Path) -> list[dict[str, str]]:
    return read_csv_rows(path) if path.exists() else []


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _first_present(row: Mapping[str, Any], names: Sequence[str]) -> Any:
    for name in names:
        value = row.get(name)
        if _clean(value) not in PLACEHOLDER_VALUES:
            return value
    return ""


def _valid_label(value: Any) -> bool:
    return _clean(value) not in PLACEHOLDER_VALUES


def _label_equal(left: Any, right: Any) -> int:
    return int(_valid_label(left) and _clean(left) == _clean(right))


def _confidence_bin(value: Any) -> str:
    score = _float(value)
    if math.isnan(score):
        return "missing"
    if score < 0.4:
        return "0.0-0.4"
    if score < 0.6:
        return "0.4-0.6"
    if score < 0.8:
        return "0.6-0.8"
    return "0.8-1.0"


def _entropy_bin(row: Mapping[str, Any]) -> str:
    entropy = _float(_first_present(row, DW_ENTROPY_ALIASES))
    if math.isnan(entropy):
        top = _float(_first_present(row, DW_CONFIDENCE_ALIASES))
        if math.isnan(top):
            return "missing"
        entropy = 1.0 - top
    if entropy < 0.2:
        return "low"
    if entropy < 0.4:
        return "medium"
    return "high"


def _to_worldcover_label(value: Any) -> str:
    label = _clean(value)
    if not label:
        return ""
    return DW_TO_WORLDCOVER.get(label, label)


def _dw_column(row: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = _clean(row.get(name))
        if value:
            return value
    return ""


def _lookup_from_rows(predictions: Sequence[Mapping[str, Any]], split_filter: set[str] | None = None) -> dict[str, Mapping[str, Any]]:
    lookup = {}
    for row in predictions:
        if split_filter is not None and _clean(row.get("split")) not in split_filter:
            continue
        sample_id = _clean(row.get("sample_id"))
        if sample_id:
            lookup[sample_id] = row
    return lookup


def _prediction_scopes(audit_root: Path) -> dict[str, tuple[list[dict[str, str]], set[str] | None, str]]:
    eval_rows = _read(audit_root / "alphaearth_full_eval_predictions.csv")
    if not eval_rows:
        eval_rows = _read(audit_root / "alphaearth_full_predictions.csv")
    all_rows = _read(audit_root / "alphaearth_full_all_split_predictions.csv")
    scopes: dict[str, tuple[list[dict[str, str]], set[str] | None, str]] = {
        "eval_calibration_test": (eval_rows, None, "formal_eval"),
        "test_only": (eval_rows, {"test"}, "formal_test"),
    }
    if all_rows:
        scopes["all_split_descriptive"] = (all_rows, None, "descriptive_background_only")
    return scopes


def _joined_dw_rows(aligned: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]], split_filter: set[str] | None = None) -> tuple[list[dict[str, Any]], int, int]:
    lookup = _lookup_from_rows(predictions, split_filter)
    joined: list[dict[str, Any]] = []
    placeholder_count = 0
    for row in aligned:
        sample_id = _clean(row.get("sample_id"))
        pred = lookup.get(sample_id)
        raw_wc = _dw_column(row, "worldcover_label", "label")
        raw_ae = _dw_column(row, "alphaearth_prediction", "ae_pred", "prediction")
        if not _valid_label(raw_wc) or not _valid_label(raw_ae):
            placeholder_count += 1
        if not pred:
            continue
        wc = _dw_column(pred, "label", "worldcover_label")
        ae = _dw_column(pred, "prediction", "alphaearth_prediction", "ae_pred")
        if not _valid_label(wc) or not _valid_label(ae):
            continue
        item = dict(row)
        item["worldcover_label"] = wc
        item["alphaearth_prediction"] = ae
        item["alphaearth_correct"] = pred.get("correct", _label_equal(ae, wc))
        item["alphaearth_risk"] = pred.get("risk", 1 - _label_equal(ae, wc))
        item["matched_prediction_row"] = 1
        joined.append(item)
    return joined, len(lookup), placeholder_count


def _group_metric(rows: Sequence[Mapping[str, Any]], metric_name: str, group_name: str, value_getter: Any) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        key = str(value_getter(row))
        grouped.setdefault(key, []).append(_float(row.get(metric_name)))
    return [
        {
            "metric": metric_name,
            "group": group_name,
            "group_value": key,
            "value": float(np.mean([value for value in values if not math.isnan(value)])) if any(not math.isnan(value) for value in values) else "",
            "support_count": len(values),
            "claim_scope": "Dynamic World is map-product agreement / label ambiguity diagnostic only, not human ground truth.",
        }
        for key, values in sorted(grouped.items())
    ]


def build_dynamic_world_diagnostic(audit_root: Path) -> tuple[list[dict[str, Any]], str]:
    aligned_path = audit_root / "alphaearth_full_dw_aligned.csv"
    aligned = _read(aligned_path)
    if not aligned:
        return (
            [
                {
                    "status": "unavailable",
                    "reason": "missing_alphaearth_full_dw_aligned_csv",
                    "required_action": "Create alphaearth_full_dw_aligned.csv with sample_id, worldcover_label, dynamic_world_label, Dynamic World confidence/probability, and AlphaEarth prediction columns.",
                    "claim_scope": "Dynamic World is optional diagnostic evidence only, not human ground truth.",
                }
            ],
            "Dynamic World diagnostic unavailable because alphaearth_full_dw_aligned.csv is missing. No claim was fabricated.",
        )
    missing_columns = [column for column in REQUIRED_DW_COLUMNS if column not in aligned[0]]
    if missing_columns:
        return (
            [
                {
                    "status": "invalid",
                    "reason": "missing_required_columns",
                    "missing_columns": ";".join(missing_columns),
                    "claim_scope": "Dynamic World diagnostic rejected; no empirical DW claim should be made.",
                }
            ],
            f"Dynamic World diagnostic invalid because required columns are missing: {', '.join(missing_columns)}.",
        )
    sample_ids = [_clean(row.get("sample_id")) for row in aligned]
    unique_sample_ids = len(set(sample_ids))
    output_rows = []
    valid_scope_count = 0
    ambiguity_labels = {"20", "30", "40", "Shrubland", "Grassland", "Cropland"}
    for scope, (predictions, split_filter, claim_kind) in _prediction_scopes(audit_root).items():
        joined, prediction_row_count, placeholder_count = _joined_dw_rows(aligned, predictions, split_filter)
        if not joined:
            output_rows.append(
                {
                    "scope": scope,
                    "status": "invalid",
                    "reason": "no_valid_prediction_label_join",
                    "dw_aligned_rows": len(aligned),
                    "matched_prediction_rows": 0,
                    "prediction_table_rows": prediction_row_count,
                    "unique_sample_id_count": unique_sample_ids,
                    "raw_aligned_placeholder_label_count": placeholder_count,
                    "claim_scope": "No valid AlphaEarth prediction/WorldCover label join exists for this scope.",
                }
            )
            continue
        valid_scope_count += 1
        validation = {
            "scope": scope,
            "metric": "dw_aligned_table_validation",
            "group": "all",
            "group_value": "all",
            "value": "",
            "dw_aligned_rows": len(aligned),
            "matched_prediction_rows": len(joined),
            "prediction_table_rows": prediction_row_count,
            "support_count": len(joined),
            "unique_sample_id_count": unique_sample_ids,
            "matched_unique_sample_id_count": len({_clean(row.get("sample_id")) for row in joined}),
            "expected_row_count": 156246,
            "row_count_status": "ok" if len(aligned) == 156246 else "unexpected",
            "unique_sample_id_status": "ok" if unique_sample_ids == len(aligned) else "duplicate_sample_ids",
        "raw_aligned_placeholder_label_count": placeholder_count,
            "diagnostic_scope": "matched_subset" if len(joined) < len(aligned) else "full_aligned_table",
            "claim_scope": "paper_facing_formal_evaluation" if claim_kind in {"formal_eval", "formal_test"} else "descriptive_background_only",
        }
        output_rows.append(validation)
        enriched = []
        for row in joined:
            wc = _dw_column(row, "worldcover_label", "label")
            dw = _to_worldcover_label(_dw_column(row, "dynamic_world_label"))
            ae = _dw_column(row, "alphaearth_prediction", "ae_pred", "prediction")
            wc_dw = _label_equal(wc, dw)
            ae_wc = _label_equal(ae, wc)
            ae_dw = _label_equal(ae, dw)
            item = dict(row)
            item["worldcover_dynamicworld_agreement"] = wc_dw
            item["alphaearth_worldcover_accuracy"] = ae_wc
            item["alphaearth_dynamicworld_agreement"] = ae_dw
            item["dw_confidence_bin"] = _confidence_bin(_first_present(row, DW_CONFIDENCE_ALIASES))
            item["dw_entropy_bin"] = _entropy_bin(row)
            item["worldcover_dynamicworld_agreement_group"] = "agree" if wc_dw else "disagree"
            item["grassland_shrubland_cropland_ambiguity"] = int(wc in ambiguity_labels or dw in ambiguity_labels or ae in ambiguity_labels)
            enriched.append(item)
        claim_scope = "paper_facing_formal_evaluation" if claim_kind in {"formal_eval", "formal_test"} else "descriptive_background_only_not_formal_model_accuracy"
        for metric in ["worldcover_dynamicworld_agreement", "alphaearth_worldcover_accuracy", "alphaearth_dynamicworld_agreement", "grassland_shrubland_cropland_ambiguity"]:
            values = [_float(row.get(metric)) for row in enriched]
            output_rows.append(
                {
                    "scope": scope,
                    "metric": metric,
                    "group": "all",
                    "group_value": "all",
                    "value": float(np.mean(values)) if values else "",
                    "support_count": len(values),
                    "dw_aligned_rows": len(aligned),
                    "matched_prediction_rows": len(joined),
                    "unique_sample_id_count": unique_sample_ids,
                    "claim_scope": claim_scope,
                }
            )
        for row in _group_metric(enriched, "alphaearth_worldcover_accuracy", "dw_confidence_bin", lambda item: item.get("dw_confidence_bin")):
            output_rows.append({"scope": scope, **row, "claim_scope": claim_scope})
        for row in _group_metric(enriched, "alphaearth_worldcover_accuracy", "worldcover_dynamicworld_agreement", lambda item: item.get("worldcover_dynamicworld_agreement_group")):
            output_rows.append({"scope": scope, **row, "claim_scope": claim_scope})
        error_rows = []
        for row in enriched:
            item = dict(row)
            item["alphaearth_error"] = 1 - int(_float(row.get("alphaearth_worldcover_accuracy"), 0))
            error_rows.append(item)
        for row in _group_metric(error_rows, "alphaearth_error", "dw_entropy_bin", lambda item: item.get("dw_entropy_bin")):
            output_rows.append({"scope": scope, **row, "claim_scope": claim_scope})
    if valid_scope_count == 0:
        return output_rows, "Dynamic World diagnostic invalid because no valid prediction/label join exists in any scope. No accuracy was reported."
    return output_rows, "Dynamic World diagnostic computed by scope from alphaearth_full_dw_aligned.csv joined to formal eval and all-split prediction tables."
