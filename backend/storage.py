from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


SUBMISSIONS_DIR = Path(__file__).parent / "submissions"


def save_submission(data: Dict[str, Any]) -> str:
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"submission_{timestamp}.json"
    path = SUBMISSIONS_DIR / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename
