from .signal_builder import build_signal, validate_signal, format_signal


def generate_signal(symbol: str):
    """
    Legacy compatibility interface.

    The production signal engine requires a validated trade setup.
    This function does not generate a live signal from a symbol alone.
    """
    return {
        "symbol": symbol,
        "signal": None,
        "status": "NO_SIGNAL",
        "message": "A complete validated setup is required.",
    }


__all__ = [
    "build_signal",
    "validate_signal",
    "format_signal",
    "generate_signal",
]
