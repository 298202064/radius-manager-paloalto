import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DYNAMIC_DIR = Path(os.getenv("DYNAMIC_LIST_DIR", "/app/dynamic"))
IP_LIST_FILE = DYNAMIC_DIR / "ip-list.txt"
URL_LIST_FILE = DYNAMIC_DIR / "url-list.txt"


def _ensure_dir() -> None:
    DYNAMIC_DIR.mkdir(parents=True, exist_ok=True)


def _read_lines(path: Path) -> list[str]:
    _ensure_dir()
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def _write_lines(path: Path, lines: list[str]) -> None:
    _ensure_dir()
    text = "\n".join(lines) + ("\n" if lines else "")
    path.write_text(text, encoding="utf-8")


def get_ip_list() -> list[str]:
    return _read_lines(IP_LIST_FILE)


def set_ip_list(lines: list[str]) -> list[str]:
    _write_lines(IP_LIST_FILE, lines)
    return lines


def get_url_list() -> list[str]:
    return _read_lines(URL_LIST_FILE)


def set_url_list(lines: list[str]) -> list[str]:
    _write_lines(URL_LIST_FILE, lines)
    return lines


def get_ip_list_text() -> str:
    return IP_LIST_FILE.read_text(encoding="utf-8") if IP_LIST_FILE.exists() else ""


def get_url_list_text() -> str:
    return URL_LIST_FILE.read_text(encoding="utf-8") if URL_LIST_FILE.exists() else ""
