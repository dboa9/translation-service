import sys
from pathlib import Path

# Set project root and add it to sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("\nInitial sys.path:")
for p in sys.path:
    print(f"  - {p}")

print(f"\nProject root: {project_root}")

print("\nUpdated sys.path:")
for p in sys.path:
    print(f"  - {p}")

print("\nAttempting import...")
try:
    from tests.path_impact_analyzer import ImpactAnalyzer
    print("Successfully imported ImpactAnalyzer")
    
    analyzer = ImpactAnalyzer(project_root)
    report = analyzer.generate_report()
    analyzer.save_report(report, "project_report.json")
    print("Report generated and saved to project_report.json")
except ImportError as e:
    print(f"Import error: {e}")
    print("\nListing contents of the 'tests' directory:")
    tests_dir = project_root / 'tests'
    if tests_dir.is_dir():
        for item in tests_dir.iterdir():
            print(f"  - {item.name}")
    else:
        print("  'tests' directory not found")
except Exception as e:
    print(f"An error occurred: {e}")
