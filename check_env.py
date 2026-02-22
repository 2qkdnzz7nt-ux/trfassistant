import sys
import os

print("STDOUT: Starting check...", flush=True)
sys.stderr.write("STDERR: Starting check...\n")

try:
    import streamlit
    print(f"STDOUT: Streamlit version: {streamlit.__version__}", flush=True)
except ImportError:
    print("STDOUT: Streamlit not found", flush=True)
except Exception as e:
    print(f"STDOUT: Error: {e}", flush=True)

print("STDOUT: Done.", flush=True)
