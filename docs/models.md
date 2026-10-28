# Model environments

Install PyTorch/torchvision builds suitable for your platform from the official
[PyTorch installation guide](https://pytorch.org/get-started/locally/). The CPU
verification lock records a mutually compatible pair; it is not a CUDA environment.
For real inference, install the relevant extras (`.[models,geo]`) in a separate
environment and record its resolved dependencies, checkpoint hashes and device.
Prithvi/TerraMind workflows additionally require the compatible TerraTorch version
specified by the relevant runner/configuration. They are not vendored here.

Official implementations/checkpoints:

- [DOFA](https://github.com/zhu-xlab/DOFA) and [DOFAv2](https://github.com/xiong-zhitong/terratorch)
- [CROMA](https://github.com/antofuller/CROMA)
- [Prithvi EO 2.0](https://github.com/NASA-IMPACT/Prithvi-EO-2.0)
- [TerraMind](https://github.com/IBM/terramind)

Use explicit checkpoint paths and verify model source/version and license.
The model adapters do not make checkpoints part of this repository. Preserve
input scale, resize, band profile/wavelengths, pooling and manifest hash in cache
identity. Never interpret cached embeddings from a different protocol as current.
