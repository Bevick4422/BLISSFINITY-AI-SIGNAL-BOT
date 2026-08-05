"""
=====================================================
BLISSFINITY SIGNAL
Report Scheduler
=====================================================
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from reports.weekly import generate_weekly_report
from reports.monthly import generate_monthly_report

# Prevent duplicate reports
last_week_sent = None
last_month_sent = None


async def run_report_scheduler():
    """
    Background scheduler for weekly and monthly reports.
    """

    global last_week_sent
    global last_month_sent

    print("✅ Report Scheduler Started")

    while True:

        try:

            now = datetime.utcnow()

            current_week = now.isocalendar().week
            current_month = now.month

            # =====================================================
            # WEEKLY REPORT
            # Every Sunday between 23:00 and 23:59 UTC
            # =====================================================

            if (
                now.weekday() == 6
                and now.hour == 23
                and last_week_sent != current_week
            ):

                print("📈 Sending Weekly Report...")

                await generate_weekly_report()

                last_week_sent = current_week

                print("✅ Weekly Report Sent")

            # =====================================================
            # MONTHLY REPORT
            # First day of month between 23:00 and 23:59 UTC
            # =====================================================

            if (
                now.day == 1
                and now.hour == 23
                and last_month_sent != current_month
            ):

                print("🏆 Sending Monthly Report...")

                await generate_monthly_report()

                last_month_sent = current_month

                print("✅ Monthly Report Sent")

        except Exception as e:

            print(f"❌ Report Scheduler Error: {e}")

        await asyncio.sleep(60)