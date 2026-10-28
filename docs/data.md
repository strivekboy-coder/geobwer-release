# Data and external assets

Download from official providers, verify their terms, then prepare local files.
This repository contains neither dataset imagery nor frozen per-sample outputs.

| Task | Official entrypoint | Preparation/requirements |
| --- | --- | --- |
| fMoW-Sentinel | [SatMAE](https://github.com/sustainlab-group/SatMAE) and [Stanford release](https://purl.stanford.edu/vg497d2105) | Official metadata and local tar archive; verify location-disjoint splits and geographic metadata. Use `prepare_fmow_sentinel_clean_subset.py` and `colab/prepare_fmow_formal_splits_colab.py`. |
| reBEN / BigEarthNet | [BigEarthNet](https://bigearth.net/) | Official paired S1/S2 data, 19-label mapping, official train/val/test metadata, source-tile lineage. See `colab/prepare_reben_croma_sensor_audit_colab.py`. |
| Sen1Floods11 | [Official dataset](https://github.com/cloudtostreet/Sen1Floods11) | Real image/mask pairs and official split metadata. Use `prepare_sen1floods11_subset.py`; TL and frozen-diagnostic band/resolution profiles must stay separate. |
| AlphaEarth / WorldCover | [AlphaEarth](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL) and [WorldCover](https://esa-worldcover.org/) | Your own authorized Earth Engine project; verified coordinates, spatial blocks and reference labels. Use the AlphaEarth export and preflight runners. |

Names above identify sources, not permission to redistribute. Check the license
of the exact dataset variant and checkpoint you use, including attribution,
derived-data and geographic-metadata conditions. Frozen probabilities, labels,
coordinates and sample IDs require a separate release decision. No Zenodo data
deposit or redistribution permission is asserted by this repository.

Prepared datasets should contain a manifest plus readable local image/mask paths.
Keep portable relative paths and supply the data root to the runner. In Colab,
copy/extract prepared archives into local runtime storage before inference; use
Drive only as persistent cache. Do not invent coordinates or substitute synthetic
chips for real-data experiments. Preserve all model/preprocessing/split hashes.
