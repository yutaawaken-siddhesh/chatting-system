import os
import tkinter as tk
from backend import ChatDatabase
from frontend import ChatApp
from dotenv import load_dotenv

def main():
    """
    Main application entry point. Links all structural system parameters with Tkinter Frontend UI displays.
    """
    print("Initialize application runtime environment...")
    
    # Secure parameters loaded transparently to keep secrets clear of Git source logic tree
    load_dotenv()
    
    # Phase 2: Start Python <-> MYSQL Network Backbone Interface
    print("Connecting to MYSQL Backbone...")
    db_interface = ChatDatabase(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_NAME", "chat_app_db")
    )
    
    if not db_interface.pool:
        print("\n[!] FATAL DIAGNOSTIC: Application Failed to Establish Connection to Database.")
        print("[!] STEPS TO FIX:")
        print("  1. Ensure MySQL Server or Workspace Application is presently RUNNING.")
        print("  2. Apply the local schema definitions into Workbench -> 'mysql < sql/schema.sql'")
        print("  3. Double click/inspect valid keys placed inside the base-level '.env' file parameters.\n")
        
        # Fallback debug window alert
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Initialization Failed", "Could not connect to Chat Database Backend.\nSee console log for manual SQL schema fix operations.")
        return

    # Phase 3: Initiate Render Activity Sequence Flow. 
    root = tk.Tk()
    
    # Push interface variable straight into the ChatApp layout initialization state (Constructor method)
    app = ChatApp(root, db_interface)
    
    # Properly tie Tkinter manual exit X button hook callback to cleanly disconnect server polling thread.
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start persistent application Loop processing (Never blocks thanks to separate threads previously handled inside class layout)
    root.mainloop()

if __name__ == "__main__":
    main()
