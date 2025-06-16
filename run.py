import os
import sys
import argparse
from dotenv import load_dotenv

def main():
    """Main function to run the bot."""
    parser = argparse.ArgumentParser(description='Telegram File Bot')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--web-only', action='store_true', help='Run only the web admin panel')
    parser.add_argument('--bot-only', action='store_true', help='Run only the bot')
    
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        import init_db
        return
    
    # Run web admin panel only
    if args.web_only:
        print("Running web admin panel...")
        from app.web.app import run_web_server
        run_web_server()
        return
    
    # Run bot only
    if args.bot_only:
        print("Running bot...")
        import asyncio
        from app.bot import main as bot_main
        asyncio.run(bot_main())
        return
    
    # Run both bot and web admin panel
    print("Running bot and web admin panel...")
    import main

if __name__ == "__main__":
    main()