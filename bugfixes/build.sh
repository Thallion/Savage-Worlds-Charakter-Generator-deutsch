#!/bin/bash
# Build script for Kivy Bugfixes Test App (shell version)
# Default: full clean rebuild (force + clean)
# Options: --incremental, --no-clean, --no-force, --debug

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
INCREMENTAL=""
NO_CLEAN=""
NO_FORCE=""
DEBUG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --incremental)
            INCREMENTAL="yes"
            shift
            ;;
        --no-clean)
            NO_CLEAN="yes"
            shift
            ;;
        --no-force)
            NO_FORCE="yes"
            shift
            ;;
        --debug)
            DEBUG="--verbose"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--incremental] [--no-clean] [--no-force] [--debug]"
            echo "  --incremental   Skip cleaning and forcing (incremental build)"
            echo "  --no-clean      Force rebuild but skip cleaning"
            echo "  --no-force      Clean but don't force rebuild"
            echo "  --debug         Enable verbose debug output"
            echo ""
            echo "Default (no flags): full clean rebuild (force + clean)"
            exit 1
            ;;
    esac
done

# Determine clean and force flags
if [ "$INCREMENTAL" = "yes" ]; then
    DO_CLEAN="no"
    DO_FORCE="no"
    MODE="incremental"
elif [ "$NO_CLEAN" = "yes" ]; then
    DO_CLEAN="no"
    DO_FORCE="yes"
    MODE="force (no clean)"
elif [ "$NO_FORCE" = "yes" ]; then
    DO_CLEAN="yes"
    DO_FORCE="no"
    MODE="clean (no force)"
else
    DO_CLEAN="yes"
    DO_FORCE="yes"
    MODE="full clean rebuild"
fi

echo "============================================================"
echo "Build mode: $MODE"
echo "============================================================"

echo "============================================================"
echo "Step 1: Applying Python 3+ / Cython 3.x compatibility fixes"
echo "============================================================"

if [ -f "build_fixes.py" ]; then
    python3 build_fixes.py
else
    echo "ERROR: build_fixes.py not found!"
    exit 1
fi

# Step 2: Clean if requested
if [ "$DO_CLEAN" = "yes" ]; then
    echo "============================================================"
    echo "Step 2: Cleaning build directories"
    echo "============================================================"
    echo "Cleaning build directories..."
    buildozer android clean
fi

# Step 3: Run buildozer
echo "============================================================"
echo "Step 3: Building APK with buildozer"
echo "============================================================"

BUILDOZER_CMD="buildozer android debug"
if [ "$DO_FORCE" = "yes" ]; then
    BUILDOZER_CMD="$BUILDOZER_CMD --force-build"
fi
if [ -n "$DEBUG" ]; then
    BUILDOZER_CMD="$BUILDOZER_CMD $DEBUG"
fi

echo "Starting build: $BUILDOZER_CMD"
$BUILDOZER_CMD

APK_PATH="bin/kivybugfixes-0.1.0-arm64-v8a-debug.apk"
if [ -f "$APK_PATH" ]; then
    echo "============================================================"
    echo "BUILD SUCCESSFUL!"
    echo "APK created at: $APK_PATH"
    echo "Size: $(du -h "$APK_PATH" | cut -f1)"
    echo "============================================================"
else
    echo "============================================================"
    echo "BUILD COMPLETED BUT APK NOT FOUND!"
    echo "Check logs for errors."
    echo "============================================================"
    exit 1
fi