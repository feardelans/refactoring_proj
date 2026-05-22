#!/usr/bin/env python3
"""Знімає UF_HIDDEN з .pth у venv (macOS, Python 3.12+ ігнорує приховані .pth)."""
from __future__ import annotations

import glob
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if sys.platform != "darwin":
        print("Не macOS — нічого не потрібно.")
        return 0

    import site

    sp = Path(site.getsitepackages()[0])
    files = sorted(sp.glob("*.pth"))
    if not files:
        print(f"Немає .pth у {sp}")
        return 0

    for pth in files:
        subprocess.run(["chflags", "nohidden", str(pth)], check=False)
    print(f"Оновлено {len(files)} файл(ів) у {sp}")
    try:
        import sport_training  # noqa: F401
    except ModuleNotFoundError:
        print("Увага: import sport_training досі не працює — перевірте pip install -e .")
        return 1
    print("import sport_training — OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
