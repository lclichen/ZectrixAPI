"""API Key 配置管理 - 存储在用户本地目录"""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".zectrix"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_api_key() -> str | None:
    """从本地配置读取 API Key"""
    if not CONFIG_FILE.exists():
        return None
    data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return data.get("api_key")


def save_api_key(api_key: str) -> None:
    """保存 API Key 到本地配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps({"api_key": api_key}, ensure_ascii=False),
        encoding="utf-8",
    )


def clear_api_key() -> None:
    """删除本地 API Key"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
