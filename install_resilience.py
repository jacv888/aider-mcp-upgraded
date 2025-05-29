#!/usr/bin/env python3
"""
Installation script for enhancing aider_mcp.py with resilience features.

Features:
1. Backup original aider_mcp.py
2. Install required dependencies (psutil, etc.)
3. Add resilience features to the existing server
4. Create configuration files
5. Test the enhanced server
6. Provide rollback functionality
7. Simple CLI interface for configuration

Usage:
    python install_resilience.py [--install | --rollback | --test]

Run with --install to perform installation.
Run with --rollback to restore original aider_mcp.py from backup.
Run with --test to run a basic test of the enhanced server.
"""

import os
import sys
import shutil
import subprocess
import argparse

BACKUP_FILE = "aider_mcp.py.bak"
TARGET_FILE = "aider_mcp.py"
CONFIG_FILE = "resilience_config.ini"

REQUIRED_PACKAGES = [
    "psutil"
]

RESILIENCE_CODE_SNIPPET = '''
# --- Resilience features added by install_resilience.py ---
import psutil
import threading
import time
import sys

def monitor_memory(threshold_mb=500):
    def monitor():
        process = psutil.Process()
        while True:
            mem = process.memory_info().rss / (1024 * 1024)  # MB
            if mem > threshold_mb:
                print(f"[Resilience] Memory usage exceeded {threshold_mb} MB: {mem:.2f} MB. Restarting server.")
                # Restart logic: exit process to let external supervisor restart it
                sys.exit(1)
            time.sleep(5)
    t = threading.Thread(target=monitor, daemon=True)
    t.start()

# Start monitoring with threshold from config or default
import configparser
config = configparser.ConfigParser()
config.read("''' + CONFIG_FILE + '''")
threshold = 500
try:
    threshold = int(config.get("Resilience", "memory_threshold_mb"))
except Exception:
    pass

monitor_memory(threshold)
# --- End resilience features ---
'''

def backup_original():
    if os.path.exists(BACKUP_FILE):
        print(f"Backup file {BACKUP_FILE} already exists. Skipping backup.")
        return
    if not os.path.exists(TARGET_FILE):
        print(f"Error: {TARGET_FILE} does not exist. Cannot backup.")
        sys.exit(1)
    shutil.copy2(TARGET_FILE, BACKUP_FILE)
    print(f"Backup created: {BACKUP_FILE}")

def install_dependencies():
    print("Installing required dependencies...")
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("All dependencies installed.")

def add_resilience_features():
    if not os.path.exists(TARGET_FILE):
        print(f"Error: {TARGET_FILE} does not exist. Cannot add resilience features.")
        sys.exit(1)

    with open(TARGET_FILE, "r") as f:
        content = f.read()

    if "# --- Resilience features added by install_resilience.py ---" in content:
        print("Resilience features already added. Skipping modification.")
        return

    # Insert resilience code snippet after imports (after first import block)
    lines = content.splitlines()
    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "" or line.startswith("#"):
            continue
        if line.startswith("import") or line.startswith("from"):
            insert_index = i + 1
        else:
            break

    new_content = (
        "\n".join(lines[:insert_index]) + "\n" +
        RESILIENCE_CODE_SNIPPET + "\n" +
        "\n".join(lines[insert_index:]) + "\n"
    )

    with open(TARGET_FILE, "w") as f:
        f.write(new_content)

    print(f"Resilience features added to {TARGET_FILE}.")

def create_config():
    if os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} already exists. Skipping creation.")
        return

    config_content = """[Resilience]
# Memory usage threshold in MB to trigger restart
memory_threshold_mb = 500
"""
    with open(CONFIG_FILE, "w") as f:
        f.write(config_content)
    print(f"Configuration file {CONFIG_FILE} created.")

def test_server():
    print("Testing enhanced server by running it for 10 seconds...")
    try:
        proc = subprocess.Popen([sys.executable, TARGET_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.terminate()
            print("Server ran successfully for 10 seconds and was terminated.")
            return
        stdout, stderr = proc.communicate()
        print("Server output:")
        print(stdout.decode())
        if stderr:
            print("Server errors:")
            print(stderr.decode())
    except Exception as e:
        print(f"Error running server: {e}")

def rollback():
    if not os.path.exists(BACKUP_FILE):
        print(f"No backup file {BACKUP_FILE} found. Cannot rollback.")
        sys.exit(1)
    shutil.copy2(BACKUP_FILE, TARGET_FILE)
    print(f"Rollback complete. {TARGET_FILE} restored from {BACKUP_FILE}.")

def main():
    parser = argparse.ArgumentParser(description="Install resilience features for aider_mcp.py")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="Perform installation")
    group.add_argument("--rollback", action="store_true", help="Rollback to original aider_mcp.py")
    group.add_argument("--test", action="store_true", help="Test the enhanced server")

    args = parser.parse_args()

    if args.install:
        print("Starting installation...")
        backup_original()
        install_dependencies()
        add_resilience_features()
        create_config()
        test_server()
        print("Installation complete.")
    elif args.rollback:
        print("Starting rollback...")
        rollback()
        print("Rollback complete.")
    elif args.test:
        test_server()

if __name__ == "__main__":
    main()
