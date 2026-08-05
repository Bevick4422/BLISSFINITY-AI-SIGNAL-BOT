import asyncio

from reports.weekly import generate_weekly_report

async def main():
    await generate_weekly_report()

if __name__ == "__main__":
    asyncio.run(main())