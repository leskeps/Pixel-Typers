import subprocess
import sys
import os

def install(package):
    """Install a Python package using pip."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} installed successfully!\n")
    except Exception as e:
        print(f"Failed to install {package}: {e}")

def main():
    print("Opening command prompt and installing required libraries...\n")

    required_packages = ["pygame", "imageio", "numpy", "pillow"]

    for pkg in required_packages:
        install(pkg)

    print("All required packages installed.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
