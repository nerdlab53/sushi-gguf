# SUSHI-GGUF

![SUSHI-GGUF](./assets/logo.png)

> A minimalist framework to convert and quantize SDXL models to GGUF format

## Overview

SUSHI-GGUF is a tool that helps you:
- Extract UNet, CLIP, and VAE components from SDXL models
- Convert UNet to GGUF format for optimized inference
- Create quantized versions with reduced precision

## Setup

```bash
git clone --recursive https://github.com/nerdlab53/sushi-gguf.git
cd sushi-gguf
conda create -n sushi-gguf python=3.10
conda activate sushi-gguf
pip install -r requirements.txt

```


## Usage

**Convert local model**
```bash
python main.py --model_path /path/to/your/model.safetensors --output_dir ./output
```

**Download and convert from CivitAI**
```bash
python main.py --civitai --model_name "my_model" --model_version_id "12345" --civitai_token "YOUR_TOKEN"
```

**Specify quantization types**
```bash
python main.py --model_path /path/to/model.safetensors --quant_types Q5_K_S Q8_0
```

## Features

- Extract model components
- Convert to GGUF format
- Quantize to various precision levels (Q4_K_S, Q5_K_S, Q8_0)
- Download models directly from CivitAI

## Requirements

- Python 3.8+
- `safetensors`
- `gguf`
- `rich` (for terminal UI)
- `wget` (for downloads)


## Credits

- [LLama.cpp](https://github.com/ggerganov/llama.cpp)
- [CivitAI](https://civitai.com)
- [Rich](https://github.com/Textualize/rich)
- [Wget](https://www.gnu.org/software/wget/)
- [old_fisherman at civitai](https://civitai.com/user/old_fisherman)
- [bluepencil-XL at civitai](https://civitai.com/models/119012?modelVersionId=592322)
