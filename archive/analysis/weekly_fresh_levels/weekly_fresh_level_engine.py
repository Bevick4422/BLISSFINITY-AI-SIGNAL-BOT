"""
BLISSFINITY AI SIGNAL BOT
WEEKLY FRESH LEVEL ENGINE
"""


def detect_fresh_weekly_levels(df, levels):
    """
    Detect unmitigated weekly institutional levels.
    """

    fresh_a = []
    fresh_v = []

    current = len(df) - 1

    # -------------------------
    # V LEVELS
    # -------------------------

    for level in levels["all_v"]:

        mitigated = False

        for i in range(level["index"] + 1, current):

            if df.iloc[i]["low"] <= level["price"]:

                mitigated = True
                break

        if not mitigated:

            fresh_v.append(level)

    # -------------------------
    # A LEVELS
    # -------------------------

    for level in levels["all_a"]:

        mitigated = False

        for i in range(level["index"] + 1, current):

            if df.iloc[i]["high"] >= level["price"]:

                mitigated = True
                break

        if not mitigated:

            fresh_a.append(level)

    return {

        "fresh_v": fresh_v,

        "fresh_a": fresh_a

    }