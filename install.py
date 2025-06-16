import os
import sys
import subprocess
import shutil

def main():
    """Main function to install the bot."""
    print("Installing Telegram File Bot...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create necessary directories
    print("Creating necessary directories...")
    os.makedirs("app/database", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("app/web/templates", exist_ok=True)
    os.makedirs("app/web/static", exist_ok=True)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Creating .env file...")
        shutil.copy(".env.example" if os.path.exists(".env.example") else ".env", ".env")
        print("Please edit the .env file with your settings.")
    
    # Initialize database
    print("Initializing database...")
    subprocess.run([sys.executable, "init_db.py"])
    
    print("Installation completed successfully!")
    print("You can now run the bot with: python run.py")

if __name__ == "__main__":
    main()