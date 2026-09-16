from datetime import datetime
import pytz

UTC = pytz.utc


def get_market_session():

    now = datetime.now(UTC)

    hour = now.hour

    if 0 <= hour < 7:
        return "ASIAN"

    elif 7 <= hour < 12:
        return "LONDON"

    elif 12 <= hour < 16:
        return "LONDON_NEWYORK"

    elif 16 <= hour < 21:
        return "NEW_YORK"

    else:
        return "CLOSED"


def session_strength(session):

    strengths = {
        "ASIAN": 40,
        "LONDON": 80,
        "LONDON_NEWYORK": 100,
        "NEW_YORK": 90,
        "CLOSED": 10,
    }

    return strengths.get(session, 0)


def session_bias():

    session = get_market_session()

    return {
        "session": session,
        "strength": session_strength(session)
    }
