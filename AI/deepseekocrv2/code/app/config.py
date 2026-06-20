import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_path: str = "/models/DeepSeek-OCR-2"
    dtype: str = "bfloat16"
    gpu_memory_utilization: float = 0.8
    default_max_tokens: int = 4096
    default_temperature: float = 0.0
    default_prompt: str = "<image>\nOCR this image."
    request_timeout_s: float = 300.0


def get_settings() -> Settings:
    return Settings(
        model_path=os.getenv("DEEPSEEK_OCR_MODEL_PATH", "/models/DeepSeek-OCR-2"),
        dtype=os.getenv("DEEPSEEK_OCR_DTYPE", "bfloat16"),
        gpu_memory_utilization=float(
            os.getenv("DEEPSEEK_OCR_GPU_MEMORY_UTILIZATION", "0.8")
        ),
        default_max_tokens=int(os.getenv("DEEPSEEK_OCR_MAX_TOKENS", "4096")),
        default_temperature=float(os.getenv("DEEPSEEK_OCR_TEMPERATURE", "0.0")),
        default_prompt=os.getenv(
            "DEEPSEEK_OCR_PROMPT", "<image>\nOCR this image."
        ),
        request_timeout_s=float(os.getenv("DEEPSEEK_OCR_REQUEST_TIMEOUT_S", "300")),
    )
