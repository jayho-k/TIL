# DeepSeekOCR2 vLLM FastAPI Server

FastAPI endpoint for batched DeepSeek-OCR-2 inference through vLLM `AsyncLLM`.

## Environment

Always use the local virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
```

For local API tests without vLLM:

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest tests -q
```

For the GPU server runtime:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

`vllm==0.23.0` is intended for the GPU server environment. Validate the wheel,
CUDA, torch, and H200 MIG environment before using this in the internal network.

## Model Files

Do not put model weights inside this git repository. Keep the model snapshot in
a separate local model directory and point the app to that directory.

Recommended Windows path:

```text
C:\models\DeepSeek-OCR-2
```

Recommended Linux/GPU server path:

```text
/models/DeepSeek-OCR-2
```

The app reads the model location from `DEEPSEEK_OCR_MODEL_PATH`. If the variable
is not set, the code uses `/models/DeepSeek-OCR-2`.

Windows PowerShell:

```powershell
$env:DEEPSEEK_OCR_MODEL_PATH="C:\models\DeepSeek-OCR-2"
```

Linux shell:

```bash
export DEEPSEEK_OCR_MODEL_PATH=/models/DeepSeek-OCR-2
```

The directory must contain the full Hugging Face snapshot for
`deepseek-ai/DeepSeek-OCR-2`. Do not copy only the `.safetensors` file.

Expected layout:

```text
C:\models\DeepSeek-OCR-2\
  config.json
  processor_config.json
  tokenizer.json
  tokenizer_config.json
  special_tokens_map.json
  model-00001-of-000001.safetensors
  model.safetensors.index.json

  configuration_deepseek_v2.py
  modeling_deepseekocr2.py
  modeling_deepseekv2.py
  deepencoderv2.py
  conversation.py

  README.md
  LICENSE.txt
  .gitattributes
```

External network machine download example:

```powershell
huggingface-cli download deepseek-ai/DeepSeek-OCR-2 `
  --local-dir C:\models\DeepSeek-OCR-2 `
  --local-dir-use-symlinks False
```

Then copy the entire `C:\models\DeepSeek-OCR-2` directory into the internal GPU
server. Preserve the directory structure.

The DeepSeek GitHub repository is not the model directory. Use it as a reference
for prompts and example settings only. This app first tries the vLLM built-in
model path:

```text
FastAPI app
  -> vLLM 0.23.0 AsyncLLM
  -> local Hugging Face model snapshot
```

Only vendor or copy DeepSeek GitHub code if the vLLM built-in smoke test fails
and you decide to run the upstream DeepSeek example implementation separately.

## Configuration

Environment variables:

```text
DEEPSEEK_OCR_MODEL_PATH=/models/DeepSeek-OCR-2
DEEPSEEK_OCR_DTYPE=bfloat16
DEEPSEEK_OCR_GPU_MEMORY_UTILIZATION=0.8
DEEPSEEK_OCR_MAX_TOKENS=4096
DEEPSEEK_OCR_TEMPERATURE=0.0
DEEPSEEK_OCR_REQUEST_TIMEOUT_S=300
```

Offline Hugging Face mode:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
$env:HF_DATASETS_OFFLINE="1"
```

## Async Smoke Test

Run this before starting the API server on the GPU machine.

```powershell
.\.venv\Scripts\python scripts\smoke_async_deepseekocr2.py `
  --model-path C:\models\DeepSeek-OCR-2 `
  --image C:\data\sample_page.png `
  --requests 1
```

Then test multiple concurrent requests into the same `AsyncLLM` engine:

```powershell
.\.venv\Scripts\python scripts\smoke_async_deepseekocr2.py `
  --model-path C:\models\DeepSeek-OCR-2 `
  --image C:\data\sample_page.png `
  --requests 4
```

If the smoke test fails, do not deploy `/infer/batch` yet. First check vLLM
version, model snapshot files, prompt format, processor files, and GPU memory.

## Run API

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoint

`POST /infer/batch`

Input: `multipart/form-data`

- `files`: one or more image files
- `prompt`: optional OCR prompt
- `max_tokens`: optional integer
- `temperature`: optional float

Example:

```powershell
curl.exe -X POST "http://localhost:8000/infer/batch" `
  -F "files=@C:\data\page_001.png" `
  -F "files=@C:\data\page_002.png" `
  -F "max_tokens=4096" `
  -F "temperature=0"
```

Response shape:

```json
{
  "count": 2,
  "elapsed_ms": 12345,
  "results": [
    {
      "index": 0,
      "filename": "page_001.png",
      "text": "...",
      "elapsed_ms": 1000,
      "error": null
    }
  ]
}
```
