"""
=====================================================
BLISSFINITY SIGNAL
Monthly Report
=====================================================
"""

from reports.performance import get_performance_summary
from telegram.sender import send_monthly_report


async def generate_monthly_report():
    """
    Generate and send the monthly report.
    """

    report = get_performance_summary()

    await send_monthly_report(report)