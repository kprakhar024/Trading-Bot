"""
Launcher script for the Binance Futures Trading Bot Web UI
"""

import os
import sys
import webbrowser
from threading import Timer

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')


def main():
    """Main function to run the web UI"""
    
    print("\n" + "=" * 70)
    print("🤖  BINANCE FUTURES TRADING BOT - WEB UI")
    print("=" * 70)
    
    # Check if .env file exists
    env_file = os.path.join(current_dir, '.env')
    if not os.path.exists(env_file):
        print("\n❌ ERROR: .env file not found!")
        print("\nPlease create a .env file with your API credentials:")
        print("   BINANCE_API_KEY=your_api_key_here")
        print("   BINANCE_API_SECRET=your_api_secret_here")
        print("   TESTNET=True")
        print("\n" + "=" * 70)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Check if required directories exist
    ui_dir = os.path.join(current_dir, 'ui')
    if not os.path.exists(ui_dir):
        print("\n❌ ERROR: 'ui' directory not found!")
        print("\nPlease ensure the following structure exists:")
        print("   ui/")
        print("   ├── app.py")
        print("   ├── templates/")
        print("   │   ├── layout.html")
        print("   │   └── index.html")
        print("   └── static/")
        print("       ├── css/style.css")
        print("       └── js/main.js")
        print("\n" + "=" * 70)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        # Import Flask app
        from ui.app import app, socketio
        
        print("\n✓ Trading bot initialized successfully")
        print("\n📡 Server Configuration:")
        print(f"   • Host: 0.0.0.0")
        print(f"   • Port: 5000")
        print(f"   • Mode: Development (Debug ON)")
        print(f"\n🌐 Access the dashboard at:")
        print(f"   → http://localhost:5000")
        print(f"   → http://127.0.0.1:5000")
        print(f"\n⚠️  TESTNET MODE - No real money involved")
        print("\n💡 Tips:")
        print("   • The browser will open automatically")
        print("   • Press CTRL+C to stop the server")
        print("   • Check logs/ directory for detailed logs")
        print("\n" + "=" * 70)
        print("\nStarting server...\n")
        
        # Open browser after 2 seconds
        Timer(2, open_browser).start()
        
        # Run the Flask app with SocketIO
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            log_output=True
        )
        
    except ImportError as e:
        print(f"\n❌ ERROR: Failed to import required modules")
        print(f"   {str(e)}")
        print("\n💡 Solution: Install required packages")
        print("   pip install -r requirements.txt")
        print("\n" + "=" * 70)
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to start server")
        print(f"   {str(e)}")
        print("\n💡 Check your configuration and try again")
        print("\n" + "=" * 70)
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("👋 Server stopped by user")
        print("=" * 70)
        sys.exit(0)