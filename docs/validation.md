# Release verification

Verification was executed from a fresh local Git clone in an isolated Python virtual environment.
No system/user packages or pre-existing experiment outputs were used. Imported package paths were checked against the clone.

- Platform: Windows; Python 3.12.14.
- Complete distributed suite: **622 passed, 6 skipped, 0 failures, 0 errors**.
- Dependency consistency: `python -m pip check` passed.
- Fourteen primary reproduction entrypoints passed `--help` import checks.
- Runtime versions are pinned in `requirements-test.lock.txt`; the project itself is installed separately.

## Commands

```bash
python -m pip install -r requirements-test.lock.txt
python -m pip install --no-deps -e .
python -m pip check
python -m pytest -q
```

The recorded run used an explicit short temporary base directory to avoid Windows path-length limitations.
Tests generate synthetic inputs and outputs in a temporary workspace. No real data/model rerun is claimed.

## Integration tests requiring external resources

- `tests.test_dofa_checkpoint_compatibility::test_official_dofav2_checkpoint_loads_exactly_through_adapter_when_assets_are_available`: Set DOFAV2_OFFICIAL_REPO and DOFAV2_OFFICIAL_CHECKPOINT for the real compatibility test.
- `tests.test_prithvi_sen1_inference_contract::test_wrapped_cpu_model_is_moved_to_requested_cuda`: CUDA is required to verify the real wrapped-model migration contract.
- `tests.test_terramind_sen1_config::test_generated_fit_yaml_parses_with_frozen_terratorch_cli`: TerraTorch CLI integration test requires the frozen TerraTorch runtime.
- `tests.test_terramind_sen1_config::test_real_terratorch_dataset_builds_for_all_sensor_modes`: Real TerraTorch dataset construction requires TerraTorch and rasterio.
- `tests.test_terramind_sen1_config::test_real_terratorch_fast_dev_run_uses_adapted_split`: Set RSFM_RUN_TERRAMIND_GPU_INTEGRATION=1 with real Sen1 paths to run the GPU fast-dev regression.
- `tests.test_terratorch_predict_cli::test_exact_terratorch_1210_callback_and_mapping_writer_path`: Exact TerraTorch callback integration requires the frozen Colab runtime.

These skips are explicit resource prerequisites, not suppressed test failures.
Historical private evidence/presentation packages and their corresponding tests are outside this distribution.
The release includes the mathematical API, model/data contracts, preprocessing and cache identity checks,
support/validity gates, leakage tests, and input-driven paper/supplementary computations.

## Privacy and publication gates

See [the release scan](release_scan.json), [file list](../FILES.txt), and [content manifest](../release_manifest.json).
The scan covers all candidate files and matches both common credential patterns and known private values
from the source repository. Raw imagery, weights, embeddings, frozen predictions, browser profiles,
internal reports, chats and local tool dependencies are excluded. Only explicitly synthetic test fixtures remain.
The source repository tracked-file hashes and the seven central statistical modules were also verified unchanged.
A separate pre-push gate checks the new repository history and noreply commit identity.

Dataset/checkpoint redistribution rights are not inferred by this scan. No such external assets are distributed.
