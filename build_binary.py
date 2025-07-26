#!/usr/bin/env python3
"""
Build script for creating binary distributions using PyInstaller.
"""

import sys
import os
import subprocess
from pathlib import Path


def build_binary():
    """Build binary executable using PyInstaller."""
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Define paths
    main_script = project_root / "main.py"
    app_dir = project_root / "app"
    prompts_dir = app_dir / "commands" / "prompts"
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create single executable
        "--name", "ai-coding-agent",    # Executable name
        "--console",                    # Console application
        "--noconfirm",                  # Overwrite existing
        "--clean",                      # Clean cache
        # Add data files
        f"--add-data={prompts_dir}{os.pathsep}app/commands/prompts",
        # Hidden imports (if needed)
        "--hidden-import=app",
        "--hidden-import=app.ui",
        "--hidden-import=app.commands",
        "--hidden-import=app.core",
        "--hidden-import=app.models",
        "--hidden-import=app.services",
        "--hidden-import=app.functions",
        "--hidden-import=app.utils",
        # Exclude unnecessary modules
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        # Optimize
        "--strip",
        "--optimize=2",
        str(main_script)
    ]
    
    print("🔨 Building binary executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=project_root)
        print("✅ Binary build completed successfully!")
        
        # Check if executable was created
        if sys.platform == "win32":
            exe_path = project_root / "dist" / "ai-coding-agent.exe"
        else:
            exe_path = project_root / "dist" / "ai-coding-agent"
            
        if exe_path.exists():
            print(f"📦 Executable created: {exe_path}")
            print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("⚠️  Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


def clean_build():
    """Clean build artifacts."""
    project_root = Path(__file__).parent
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    print("🧹 Cleaning build artifacts...")
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")
    
    import glob
    for pattern in files_to_clean:
        for file_path in glob.glob(str(project_root / pattern)):
            os.remove(file_path)
            print(f"   Removed: {file_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build AI Coding Agent binary")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--build", action="store_true", default=True, help="Build binary")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.build and not args.clean:
        success = build_binary()
        if not success:
            sys.exit(1)