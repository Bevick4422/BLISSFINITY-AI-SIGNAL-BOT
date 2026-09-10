"""
=====================================================
BLISSFINITY SIGNAL
Weekly Report
=====================================================
"""

from reports.performance import (
    get_weekly_performance_summary,
)

from telegram.sender import send_weekly_report


async def generate_weekly_report():
    """
    Generate and send the current week's report.
    """

    report = get_weekly_performance_summary()

    await send_weekly_report(report)