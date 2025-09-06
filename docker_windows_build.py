#!/usr/bin/env python3
"""
Docker-basierter Windows Build für Cross-Platform Entwicklung
Nutzt einen Windows Container um echte Windows EXE zu erstellen
"""

import subprocess
import sys
from pathlib import Path

def create_dockerfile():
    """Erstellt Dockerfile für Windows Build Container"""
    dockerfile_content = """
# Use Windows Server Core as base
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Chocolatey
RUN powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

# Install Python and Git
RUN choco install -y python git

# Set working directory
WORKDIR C:\\app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pyinstaller

# Copy application files
COPY . .

# Build Windows EXE
CMD ["python", "build_windows.py"]
"""
    
    dockerfile_path = Path("Dockerfile.windows")
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content.strip())
    
    print(f"📄 Dockerfile erstellt: {dockerfile_path}")
    return dockerfile_path

def build_docker_image():
    """Baut das Docker Windows Image"""
    print("🐳 Baue Windows Build Container...")
    
    cmd = [
        "docker", "build", 
        "-f", "Dockerfile.windows",
        "-t", "savage-worlds-windows-builder",
        "."
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Docker Image erfolgreich gebaut")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker Build fehlgeschlagen: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def run_windows_build():
    """Führt den Windows Build im Container aus"""
    print("🏗️  Starte Windows Build im Container...")
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{Path.cwd()}:/output",
        "savage-worlds-windows-builder"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Windows Build erfolgreich abgeschlossen")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows Build fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion für Docker Windows Build"""
    print("🪟 Docker-basierter Windows Build")
    print("Dieser Prozess erstellt eine echte Windows .exe mit Docker")
    print()
    
    # Prüfe Docker Installation
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker ist nicht installiert oder nicht verfügbar")
        print("Installiere Docker: https://docs.docker.com/get-docker/")
        return False
    
    # Erstelle Dockerfile
    dockerfile_path = create_dockerfile()
    
    # Baue Image
    if not build_docker_image():
        return False
    
    # Führe Build aus
    if not run_windows_build():
        return False
    
    print("\n🎉 Windows Build erfolgreich!")
    print("Die .exe Datei sollte im dist/ Verzeichnis sein")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)