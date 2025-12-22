"""Quick test to verify a2a_kyc_demo.py runs correctly"""
import sys
import subprocess

print("Running A2A KYC Demo...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "a2a_kyc_demo.py"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nExit Code: {result.returncode}")

if result.returncode == 0:
    print("\n[SUCCESS] Demo executed successfully!")
else:
    print("\n[ERROR] Demo failed!")
