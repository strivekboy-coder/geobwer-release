# Reproduction entrypoints

Run commands from the repository root. Pass local input/output paths explicitly
and inspect each runner with `--help` before execution. Missing real inputs are
blocking conditions; do not lower scientific thresholds to make plots appear.

## Main model panels

| Task | Entrypoint | Protocol |
| --- | --- | --- |
| fMoW DOFAv2 | `scripts/colab/run_fmow_dofav2_final_colab.py` | `configs/geobwer/fmow_sentinel.yaml` |
| fMoW ResNet50 | `scripts/colab/run_fmow_resnet50_common9_final_colab.py` | Same split/label mapping and common support |
| reBEN panel | `scripts/colab/run_reben_geofm_full_panel_colab.py` | `configs/geobwer/reben.yaml` |
| Sen1 supervised panel | `scripts/colab/run_sen1_supervised_panel_colab.py` | `configs/geobwer/sen1floods11.yaml` |
| Sen1 TerraMind | `scripts/colab/run_terramind_sen1floods11_final_colab.py` | Modality, threshold and split contracts |
| AlphaEarth | `scripts/colab/run_alphaearth_geobwer_final_colab.py` | `configs/geobwer/alphaearth.yaml` |

The stages are preparation -> embeddings/predictions -> normalized audit table
-> support/preflight -> formal audit -> tables/figures. Reuse completed stage
outputs only when their protocol identity matches. Frozen encoders use cached
embeddings; supervised training and GPU inference are not run by the unit suite.
Keep classification sample support separate from segmentation pixel support.
The native segmentation confusion-count adapter and chip-level risk are distinct
estimands; retain the task protocol chosen by each experiment.

## Comparisons and paper analyses

- Labels/budget: `scripts/run_reben_label_budget_colab.py`.
- Paired S2-to-S1 shift: `scripts/run_reben_terramind_paired_shift_colab.py` and
  `scripts/run_reben_croma_paired_shift_colab.py`.
- Adaptation stages: `scripts/colab/run_experiment8_reben_adaptation_colab.py`.
- Task-wise model comparisons: `scripts/colab/run_experiment9_model_task_generalization_colab.py`.
- Geography: `scripts/analysis/build_geographic_risk_atlas.py`,
  `prepare_geographic_risk_covariates.py`, `build_geographic_risk_association.py`.
- Supplement: `scripts/colab/run_paper_supplementary_analyses_v1_colab.py`.
  Its order is `preflight`, `cpu`, `start-ee`, then `finish-ee` after your exports
  finish. Supply your own `--project-root` and `--ee-project` when required.
- Paper table/figure assembly:

```bash
python scripts/analysis/build_final_paper_package.py --source-dir data/inputs/paper --output-dir outputs/paper
```

The figure builder requires six metric tables:
`experiment9_cell_seed_metrics.csv`, `experiment8_adaptation_stage_metrics.csv`,
`experiment8_adaptation_recovery.csv`, `reben_terramind_country_label_burden.csv`,
`reben_terramind_label_diagnostics.csv`, `reben_croma_label_diagnostics.csv`.
These are produced by the relevant experiment/postprocessing stages. They are
not supplied frozen results. The builder computes its tables from those inputs,
records hashes, checks source immutability and never substitutes embedded numbers.

For a frozen-input re-audit, provide `--registry` explicitly. An asset registry
declares immutable local inputs and allowed use; it is not a list of private Drive
URLs. Reference configurations set scientific protocol, not evidence of completion.
Unsupported slices remain invalid/descriptive; no fallback grants formal status.
