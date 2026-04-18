#!/usr/bin/env python3
"""
Build script for Kivy Bugfixes Test App.

This script applies Python 3+ compatibility fixes and then runs buildozer
with the corrected configuration.

By default, performs a full clean rebuild (force + clean) to ensure all
fixes are applied. Use flags for incremental builds.

Usage:
    python build.py [--incremental] [--no-clean] [--no-force] [--debug]

Options:
    --incremental   Skip cleaning and forcing (incremental build)
    --no-clean      Force rebuild but skip cleaning (keep downloaded packages)
    --no-force      Clean but don't force rebuild (reuse existing dist if possible)
    --debug         Enable verbose debug output

Default behavior (no flags): --force --clean (full clean rebuild)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a shell command and print output in real-time."""
    print(f"Running: {cmd}")
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
    process.wait()
    return process.returncode

def main():
    parser = argparse.ArgumentParser(description="Build Kivy Bugfixes Test App")
    parser.add_argument("--incremental", action="store_true", help="Skip cleaning and forcing (incremental build)")
    parser.add_argument("--no-clean", action="store_true", help="Force rebuild but skip cleaning")
    parser.add_argument("--no-force", action="store_true", help="Clean but don't force rebuild")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug output")
    args = parser.parse_args()
    
    # Determine clean and force flags based on arguments
    if args.incremental:
        do_clean = False
        do_force = False
    elif args.no_clean:
        do_clean = False
        do_force = True
    elif args.no_force:
        do_clean = True
        do_force = False
    else:
        # Default: full clean rebuild
        do_clean = True
        do_force = True
    
    script_dir = Path(__file__).parent.absolute()
    
    # Step 1: Apply compatibility fixes via hook script
    print("=" * 60)
    print("Step 1: Applying Python 3+ / Cython 3.x compatibility fixes")
    print("=" * 60)
    
    fix_script = script_dir / "build_fixes.py"
    if fix_script.exists():
        import subprocess
        result = subprocess.run([sys.executable, str(fix_script)], cwd=script_dir)
        if result.returncode != 0:
            print("WARNING: Fix script returned non-zero exit code. Continuing anyway.")
    else:
        print("ERROR: build_fixes.py not found!")
        return 1
    
    # Step 2: Clean if requested
    if do_clean:
        print("=" * 60)
        print("Step 2: Cleaning build directories")
        print("=" * 60)
        run_command("buildozer android clean", cwd=script_dir)
    
    # Step 3: Run buildozer
    print("=" * 60)
    print("Step 3: Building APK with buildozer")
    print("=" * 60)
    
    buildozer_cmd = "buildozer android debug"
    if do_force:
        buildozer_cmd += " --force-build"
    if args.debug:
        buildozer_cmd += " --verbose"
    
    retcode = run_command(buildozer_cmd, cwd=script_dir)
    
    if retcode == 0:
        print("=" * 60)
        print("BUILD SUCCESSFUL!")
        apk_path = script_dir / "bin" / "kivybugfixes-0.1.0-arm64-v8a-debug.apk"
        if apk_path.exists():
            print(f"APK created at: {apk_path}")
            print(f"Size: {apk_path.stat().st_size / 1024 / 1024:.2f} MB")
        else:
            print("WARNING: APK not found in expected location.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("BUILD FAILED!")
        print("Check the logs above for errors.")
        print("=" * 60)
    
    return retcode

if __name__ == "__main__":
    sys.exit(main())