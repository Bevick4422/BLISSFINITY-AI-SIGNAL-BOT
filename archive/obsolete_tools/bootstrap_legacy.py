from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("BLISSFINITY AI SIGNAL BOT")
print("PROJECT SCANNER")
print("=" * 60)

analysis = ROOT / "analysis"
tests = ROOT / "tests"
templates = ROOT / "tools" / "templates"

analysis_files = list(analysis.rglob("*.py"))
test_files = list(tests.rglob("*.py"))

print(f"\nAnalysis files : {len(analysis_files)}")
print(f"Test files     : {len(test_files)}")

print("\nChecking for empty files...\n")

repair_count = 0

TEMPLATE_MAP = {

    analysis / "wave" / "wave_engine.py":
        templates / "wave.py",

    analysis / "risk" / "risk_engine.py":
        templates / "risk.py",

    analysis / "confluence" / "confluence_engine.py":
        templates / "confluence.py",

    analysis / "regime" / "market_regime.py":
        templates / "regime.py",

    tests / "test_wave_engine.py":
        templates / "tests" / "test_wave.py",

    tests / "test_risk_engine.py":
        templates / "tests" / "test_risk.py",

    tests / "test_confluence_engine.py":
        templates / "tests" / "test_confluence.py",
}

for target, template in TEMPLATE_MAP.items():

    repair = False

    if not target.exists():
        repair = True

    elif target.stat().st_size == 0:
        repair = True

    if repair:

        target.parent.mkdir(parents=True, exist_ok=True)

        if template.exists():

            shutil.copy(template, target)

            print(f"[RESTORED] {target.relative_to(ROOT)}")

        else:

            target.write_text("# Template Missing\n")

            print(f"[EMPTY] {target.relative_to(ROOT)}")

        repair_count += 1

print(f"\nRepaired {repair_count} file(s).")
print("\nScan complete.")
