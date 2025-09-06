#!/bin/bash
# Build script with automatic compatibility fixes

echo "Starting buildozer build with automatic fixes..."

# Start the buildozer build
buildozer android debug

# Check if build failed and fixes might be needed
BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "Build failed, attempting compatibility fixes..."
    
    # Run Kivy fixes
    if [ -f "fix_kivy.py" ]; then
        echo "Running Kivy Python 3+ compatibility fixes..."
        python3 fix_kivy.py
    fi
    
    # Run pyjnius fixes
    if [ -f "fix_pyjnius.py" ]; then
        echo "Running pyjnius Python 3+ compatibility fixes..."
        python3 fix_pyjnius.py
    fi
    
    # Try building again
    echo "Retrying build after fixes..."
    buildozer android debug
    BUILD_EXIT_CODE=$?
fi

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "Build completed successfully!"
else
    echo "Build failed even after fixes. Check the logs above for details."
fi

exit $BUILD_EXIT_CODE