import asyncio

from reports.weekly import generate_weekly_report


async def main():
    print("Generating Weekly Report...")
    await generate_weekly_report()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())