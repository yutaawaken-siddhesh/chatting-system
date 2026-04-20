import tkinter as tk
from tkinter import messagebox, simpledialog, font as tkfont
import threading
import time

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color="white", *args, **kwargs):
        super().__init__(container, bg=bg_color, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg_color)
        
        # Hide scrollbar for a much cleaner web-like appearance
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        # Basic wheel binding
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.pack(side="left", fill="both", expand=True)

class ChatApp:
    def __init__(self, root, db_backend):
        self.root = root
        self.db = db_backend
        self.current_user = None
        self.current_chat_id = None
        
        self.root.title("Modern Chat Interface")
        self.root.geometry("1100x750")
        
        # Palettes exactly mimicking the reference graphic aesthetic
        self.bg_root = "#efe4fa"  # Outer edge background (light purple from image)
        self.bg_white = "#ffffff" # Panels background
        self.accent_orange = "#6a13d2" # Now it's the specific Purple color!
        self.text_dark = "#1f1f1f"
        self.text_dim = "#7a7a7a"
        self.msg_grey = "#f0f0f4" # Light grey for received message backgrounds
        self.root.configure(bg=self.bg_root)
        
        self.font_title = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.font_bold = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.font_normal = tkfont.Font(family="Helvetica", size=10)
        self.font_small = tkfont.Font(family="Helvetica", size=8)
        
        self.show_login_screen()

    def show_login_screen(self):
        self._clear_screen()
        
        # Put it in a clean floating card
        container = tk.Frame(self.root, bg=self.bg_root)
        container.pack(expand=True, fill=tk.BOTH)
        
        card = tk.Frame(container, bg=self.bg_white, padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Welcome Back", font=self.font_title, bg=self.bg_white, fg=self.text_dark).pack(pady=(0,20))
        
        tk.Label(card, text="Username", font=self.font_bold, bg=self.bg_white, fg=self.text_dark).pack(anchor="w")
        self.entry_username = tk.Entry(card, font=self.font_normal, width=30, bg="#f8fafc", relief="flat", highlightbackground="#e2e8f0", highlightcolor=self.accent_orange, highlightthickness=1)
        self.entry_username.pack(pady=(5, 15), ipady=5)
        
        tk.Label(card, text="Password", font=self.font_bold, bg=self.bg_white, fg=self.text_dark).pack(anchor="w")
        self.entry_password = tk.Entry(card, show="*", font=self.font_normal, width=30, bg="#f8fafc", relief="flat", highlightbackground="#e2e8f0", highlightcolor=self.accent_orange, highlightthickness=1)
        self.entry_password.pack(pady=(5, 20), ipady=5)
        
        btn_frame = tk.Frame(card, bg=self.bg_white)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Login", command=self.process_login, bg=self.accent_orange, fg="white", font=self.font_bold, relief="flat", cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5), ipady=5)
        tk.Button(btn_frame, text="Register", command=self.process_register, bg="#10b981", fg="white", font=self.font_bold, relief="flat", cursor="hand2").pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5,0), ipady=5)

    def _clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def process_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        user = self.db.login_user(username, password)
        if user:
            self.current_user = user
            self.show_main_interface()
        else:
            messagebox.showerror("Auth Error", "Invalid Username or Password")

    def process_register(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        if not username or not password: return
        success, msg = self.db.register_user(username, f"{username}@testapp.com", password)
        if success:
            messagebox.showinfo("Success", "Registered! You can now log in.")
        else:
            messagebox.showerror("Error", msg)

    def show_main_interface(self):
        self._clear_screen()
        
        # Layout: Main wrapper with padding to simulate the grey border around the web-app mockup panels
        self.wrapper = tk.Frame(self.root, bg=self.bg_root, padx=20, pady=20)
        self.wrapper.pack(expand=True, fill=tk.BOTH)
        
        # Layout: Left Sidebar (White Card)
        self.sidebar_card = tk.Frame(self.wrapper, bg=self.bg_white, width=320)
        self.sidebar_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        self.sidebar_card.pack_propagate(False) # Keep fixed width
        
        # Sidebar: Header
        header_f = tk.Frame(self.sidebar_card, bg=self.bg_white, pady=20, padx=20)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text="Messages", font=self.font_title, bg=self.bg_white, fg=self.text_dark).pack(side=tk.LEFT)
        tk.Label(header_f, text="🔍", font=self.font_normal, bg=self.bg_white, fg=self.text_dim).pack(side=tk.RIGHT)
        
        # Sidebar: Tabs Mockup
        tabs_f = tk.Frame(self.sidebar_card, bg=self.bg_white, padx=20)
        tabs_f.pack(fill=tk.X)
        tk.Label(tabs_f, text="All messages", font=self.font_bold, bg=self.bg_white, fg=self.accent_orange).pack(side=tk.LEFT, padx=(0,10))
        tk.Label(tabs_f, text="Unread", font=self.font_normal, bg=self.bg_white, fg=self.text_dim).pack(side=tk.LEFT, padx=10)
        tk.Label(tabs_f, text="Favorites", font=self.font_normal, bg=self.bg_white, fg=self.text_dim).pack(side=tk.LEFT, padx=10)
        tk.Label(tabs_f, text="Work", font=self.font_normal, bg=self.bg_white, fg=self.text_dim).pack(side=tk.LEFT, padx=10)
        
        # Sidebar: Orange accent underline
        tk.Frame(self.sidebar_card, bg=self.accent_orange, height=2, width=80).pack(anchor="w", padx=20, pady=(5,15))
        
        # Sidebar: The Sunday AI orange button equivalent (Updated to Purple style)
        btn_f = tk.Frame(self.sidebar_card, bg=self.bg_white, padx=20)
        btn_f.pack(fill=tk.X, pady=(0,10))
        btn = tk.Button(btn_f, text="✨ New Chat", command=self.new_chat, bg=self.accent_orange, fg="white", font=self.font_bold, relief="flat", cursor="hand2")
        btn.pack(fill=tk.X, ipady=10)
        
        # Sidebar: Chat List Area (Scrollable)
        self.chats_frame = ScrollableFrame(self.sidebar_card, bg_color=self.bg_white)
        self.chats_frame.pack(expand=True, fill=tk.BOTH)
        
        # Layout: Right Main Panel (White Card)
        self.main_card = tk.Frame(self.wrapper, bg=self.bg_white)
        self.main_card.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # Determine views for Main Panel
        self.build_empty_state()
        self.build_active_chat_state()

        # By default, show empty state
        self.active_chat_wrapper.pack_forget()
        self.empty_state_wrapper.pack(expand=True, fill=tk.BOTH)

        # Threading for live polling
        self.is_running = True
        threading.Thread(target=self.background_refresh, daemon=True).start()

    def build_empty_state(self):
        self.empty_state_wrapper = tk.Frame(self.main_card, bg=self.bg_white)
        
        # Center elements using a nested frame
        inner = tk.Frame(self.empty_state_wrapper, bg=self.bg_white)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        
        # Mimic overlapping bubbles graphic simple version
        tk.Label(inner, text="💬", font=("Helvetica", 60), bg=self.bg_white, fg=self.accent_orange).pack(pady=(0,10))
        tk.Label(inner, text="No conversation selected", font=self.font_title, bg=self.bg_white, fg=self.text_dark).pack(pady=5)
        tk.Label(inner, text="You can view your conversation in the side bar", font=self.font_normal, bg=self.bg_white, fg=self.text_dim).pack()

    def build_active_chat_state(self):
        self.active_chat_wrapper = tk.Frame(self.main_card, bg=self.bg_white)
        
        # Top Header of active chat
        self.chat_header_f = tk.Frame(self.active_chat_wrapper, bg=self.bg_white, pady=15, padx=25)
        self.chat_header_f.pack(fill=tk.X)
        self.chat_header_label = tk.Label(self.chat_header_f, text="Select a chat...", font=self.font_title, bg=self.bg_white, fg=self.text_dark)
        self.chat_header_label.pack(side=tk.LEFT)
        tk.Frame(self.active_chat_wrapper, bg="#e2e8f0", height=1).pack(fill=tk.X) # Soft Divider
        
        # Chat History Body
        self.chat_display = tk.Text(self.active_chat_wrapper, state='disabled', wrap=tk.WORD, font=self.font_normal, bg=self.bg_white, bd=0, highlightthickness=0)
        self.chat_display.pack(expand=True, fill=tk.BOTH, padx=25, pady=20)
        
        # Input Box Footer
        input_f = tk.Frame(self.active_chat_wrapper, bg=self.bg_white, padx=25, pady=20)
        input_f.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Frame(self.active_chat_wrapper, bg="#f1f5f9", height=1).pack(fill=tk.X, side=tk.BOTTOM) # Divider
        
        self.message_input = tk.Entry(input_f, font=self.font_normal, bg="#f8fafc", relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        self.message_input.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=12, padx=(0, 15))
        self.message_input.bind("<Return>", lambda event: self.send_message())
        
        tk.Button(input_f, text="Send", command=self.send_message, bg=self.accent_orange, fg="white", font=self.font_bold, relief="flat", cursor="hand2").pack(side=tk.RIGHT, ipady=8, ipadx=20)

    def background_refresh(self):
        while self.is_running:
            self.refresh_sidebar()
            if self.current_chat_id:
                self.refresh_chat_history(self.current_chat_id)
            time.sleep(2)
            
    def refresh_sidebar(self):
        recent_chats = self.db.get_recent_chats(self.current_user['id'])
        all_chats = self.db.get_user_chats(self.current_user['id'])
        
        chat_dict = {c['id']: {'name': f"User Account #{c['id']}", 'snippet': "Tap to start conversation..."} for c in all_chats}
        
        for rc in recent_chats:
            if rc['chat_id'] in chat_dict:
                chat_dict[rc['chat_id']]['snippet'] = rc['content']
                chat_dict[rc['chat_id']]['sender'] = rc['sender_name']
                
        self.root.after(0, self._update_sidebar_gui, chat_dict)

    def _update_sidebar_gui(self, chat_dict):
        target_container = self.chats_frame.scrollable_frame
        for widget in target_container.winfo_children():
            widget.destroy()
            
        for chat_id, data in chat_dict.items():
            f = tk.Frame(target_container, bg=self.bg_white, pady=12, padx=20, cursor="hand2")
            f.pack(fill=tk.X)
            display_name = data.get('sender', data['name'])
            
            # Simulated Circle Avatar Image Area
            c = tk.Canvas(f, width=44, height=44, bg=self.bg_white, highlightthickness=0)
            c.pack(side=tk.LEFT, padx=(0, 15))
            c.create_oval(2, 2, 42, 42, fill="#f1f5f9", outline="")
            
            # Add Avatar Initial Initial Letter
            initial = display_name[0].upper() if display_name else "?"
            c.create_text(22, 22, text=initial, font=self.font_bold, fill="#64748b")
            
            # Name and Snippet Layout Configuration
            txt_f = tk.Frame(f, bg=self.bg_white)
            txt_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            top_line = tk.Frame(txt_f, bg=self.bg_white)
            top_line.pack(fill=tk.X)
            
            tk.Label(top_line, text=display_name, font=self.font_bold, bg=self.bg_white, fg=self.text_dark).pack(side=tk.LEFT)
            tk.Label(top_line, text="Active", font=self.font_small, bg=self.bg_white, fg=self.text_dim).pack(side=tk.RIGHT)
            
            snippet = data['snippet']
            if len(snippet) > 35: snippet = snippet[:32] + "..."
            tk.Label(txt_f, text=snippet, font=self.font_normal, bg=self.bg_white, fg=self.text_dim, anchor="w").pack(fill=tk.X, pady=(2,0))
            
            # Bind hovering clicks to native Tkinter rows
            for w in [f, c, txt_f, top_line] + txt_f.winfo_children() + top_line.winfo_children():
                w.bind("<Button-1>", lambda e, cid=chat_id, dname=display_name: self.on_chat_select(cid, dname))

    def on_chat_select(self, chat_id, display_name):
        self.current_chat_id = chat_id
        
        # Mount the Active text chat Window visually
        self.empty_state_wrapper.pack_forget()
        self.active_chat_wrapper.pack(expand=True, fill=tk.BOTH)
        
        self.chat_header_label.config(text=f"{display_name}")
        self.refresh_chat_history(self.current_chat_id)

    def refresh_chat_history(self, chat_id):
        history = self.db.get_chat_history(chat_id)
        self.root.after(0, self._update_chat_gui, history)

    def _update_chat_gui(self, history):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        
        for msg in history:
            sender = msg['sender_name']
            text = msg['content']
            
            if msg['sender_id'] == self.current_user['id']:
                self.chat_display.insert(tk.END, f" You \n", "right_header")
                self.chat_display.insert(tk.END, f" {text} \n\n", "right")
            else:
                self.chat_display.insert(tk.END, f" {sender} \n", "left_header")
                self.chat_display.insert(tk.END, f" {text} \n\n", "left")
                
        # Update tagging to mimic Bot/User bubble UI from the image concept
        self.chat_display.tag_configure("right_header", justify='right', foreground=self.text_dim, font=self.font_small)
        self.chat_display.tag_configure("right", justify='right', foreground=self.accent_orange, font=self.font_normal)
        
        self.chat_display.tag_configure("left_header", justify='left', foreground=self.text_dim, font=self.font_small)
        self.chat_display.tag_configure("left", justify='left', foreground=self.text_dark, font=self.font_normal)
        
        self.chat_display.config(state='disabled')
        if history: self.chat_display.yview(tk.END) 

    def send_message(self):
        text = self.message_input.get().strip()
        if text and self.current_chat_id:
            self.message_input.delete(0, tk.END)
            success = self.db.send_message(self.current_chat_id, self.current_user['id'], text)
            if success:
                self.refresh_chat_history(self.current_chat_id)
            else:
                messagebox.showerror("Error", "Message Failed to Send.")
                
    def new_chat(self):
        other_name = simpledialog.askstring("New Conversation", "Enter Username to connect with:", parent=self.root)
        if other_name:
            other_name = other_name.strip()
            if other_name.lower() == self.current_user['username'].lower():
                messagebox.showerror("Constraint Alert", "Users cannot link to themselves.")
                return
            
            success, result_or_msg = self.db.setup_new_chat(self.current_user['id'], other_name)
            if success:
                self.on_chat_select(result_or_msg, other_name)
                self.refresh_sidebar()
            else:
                messagebox.showerror("Chat Request Failed", result_or_msg)

    def on_closing(self):
        self.is_running = False
        self.root.destroy()
