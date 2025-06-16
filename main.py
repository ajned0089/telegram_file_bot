import asyncio
import threading
from app.bot import main as bot_main
from app.web.app import run_web_server

def start_web_server():
    """Start web server in a separate thread."""
    run_web_server()

if __name__ == "__main__":
    # Start web server in a separate thread
    web_thread = threading.Thread(target=start_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Start bot
    asyncio.run(bot_main())