import sys
import os
import platform
import subprocess

print("\n=== Python Environment Diagnostics ===\n")

# 1. Check Python executable and version
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"CWD: {os.getcwd()}")

# 2. Check installed packages using import
print("\n--- Checking Critical Libraries ---")
libs = ['streamlit', 'pandas', 'duckduckgo_search', 'watchdog']
for lib in libs:
    try:
        module = __import__(lib)
        version = getattr(module, '__version__', 'unknown version')
        path = getattr(module, '__file__', 'unknown path')
        print(f"✅ {lib:<20} : {version} (installed at {os.path.dirname(path)})")
    except ImportError:
        print(f"❌ {lib:<20} : NOT FOUND")
    except Exception as e:
        print(f"⚠️ {lib:<20} : ERROR - {e}")

# 3. Check pip availability
print("\n--- Checking Pip ---")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Pip is available: {result.stdout.strip()}")
    else:
        print(f"❌ Pip check failed: {result.stderr.strip()}")
except Exception as e:
    print(f"❌ Pip check failed with exception: {e}")

print("\n=== End of Diagnostics ===\n")
