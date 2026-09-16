"""
=========================================================
BLISSFINITY AI SIGNAL BOT
Setup Manager
=========================================================

Responsible for:

- Saving Daily rejection setups
- Loading saved setups
- Updating setups
- Removing setups
- Persisting setups safely as JSON

Important:
Pandas Timestamp objects are converted to ISO strings
before JSON persistence.
=========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# ==========================================================
# STORAGE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SETUP_FILE = DATA_DIR / "setups.json"


# ==========================================================
# JSON SERIALIZATION
# ==========================================================

def _json_safe(value: Any) -> Any:
    """
    Convert common non-JSON Python/Pandas objects
    into JSON-safe values.
    """

    if value is None:
        return None

    # Pandas Timestamp / datetime-like objects
    if hasattr(value, "isoformat"):
        return value.isoformat()

    # NumPy scalar values
    if hasattr(value, "item"):

        try:
            return value.item()

        except Exception:
            pass

    # Dictionaries
    if isinstance(value, dict):

        return {
            str(key): _json_safe(val)
            for key, val in value.items()
        }

    # Lists / tuples
    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):

        return [
            _json_safe(item)
            for item in value
        ]

    # Primitive JSON values
    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):

        return value

    # Final fallback
    return str(value)


# ==========================================================
# LOAD
# ==========================================================

def load_setups() -> List[Dict[str, Any]]:
    """
    Load all saved setups.

    If the file does not exist or is invalid,
    return an empty list.
    """

    if not SETUP_FILE.exists():
        return []

    try:

        with SETUP_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            list,
        ):

            return []

        return data

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


# ==========================================================
# SAVE
# ==========================================================

def save_setups(
    setups: List[Dict[str, Any]],
) -> bool:
    """
    Save setups safely to JSON.
    """

    try:

        safe_setups = _json_safe(
            setups
        )

        with SETUP_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                safe_setups,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return True

    except OSError as exc:

        print(
            f"SETUP MANAGER | "
            f"Save failed: {exc}"
        )

        return False


# ==========================================================
# GET SETUP
# ==========================================================

def get_setup(
    symbol: str,
) -> Optional[Dict[str, Any]]:
    """
    Return the saved setup for a symbol.
    """

    setups = load_setups()

    for setup in setups:

        if setup.get(
            "symbol"
        ) == symbol:

            return setup

    return None


# ==========================================================
# ADD SETUP
# ==========================================================

def add_setup(
    setup: Dict[str, Any],
) -> bool:
    """
    Add or replace a setup for a symbol.

    Only one active setup per symbol
    is maintained.
    """

    if not isinstance(
        setup,
        dict,
    ):

        return False

    symbol = setup.get(
        "symbol"
    )

    if not symbol:
        return False

    setups = load_setups()

    # Remove previous setup
    setups = [
        existing
        for existing in setups
        if existing.get(
            "symbol"
        ) != symbol
    ]

    # Add new setup
    setups.append(
        _json_safe(
            setup
        )
    )

    return save_setups(
        setups
    )


# ==========================================================
# UPDATE SETUP
# ==========================================================

def update_setup(
    symbol: str,
    updates: Dict[str, Any],
) -> bool:
    """
    Update an existing setup.
    """

    if not isinstance(
        updates,
        dict,
    ):

        return False

    setups = load_setups()

    found = False

    for setup in setups:

        if setup.get(
            "symbol"
        ) == symbol:

            setup.update(
                _json_safe(
                    updates
                )
            )

            found = True

            break

    if not found:
        return False

    return save_setups(
        setups
    )


# ==========================================================
# REMOVE SETUP
# ==========================================================

def remove_setup(
    symbol: str,
) -> bool:
    """
    Remove a saved setup for a symbol.
    """

    setups = load_setups()

    new_setups = [
        setup
        for setup in setups
        if setup.get(
            "symbol"
        ) != symbol
    ]

    if len(new_setups) == len(
        setups
    ):

        return False

    return save_setups(
        new_setups
    )


# ==========================================================
# CLEAR ALL
# ==========================================================

def clear_setups() -> bool:
    """
    Remove all saved setups.
    """

    return save_setups(
        []
    )


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "load_setups",
    "save_setups",
    "get_setup",
    "add_setup",
    "update_setup",
    "remove_setup",
    "clear_setups",
]