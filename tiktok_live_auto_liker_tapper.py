import customtkinter as ctk
import pygetwindow as gw
import win32gui, win32api, win32con
import threading
import time

# UI Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TikTokAutoLiker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TikTok Live Auto Liker / Tapper")
        self.geometry("450x400")
        self.is_running = False

        # --- Header ---
        self.label = ctk.CTkLabel(self, text="TikTok Live Auto Liker", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(20, 10))

        # --- Window Selection ---
        self.select_label = ctk.CTkLabel(self, text="Select Target Window:", font=("Roboto", 12))
        self.select_label.pack(pady=5)
        
        self.window_list = ctk.CTkComboBox(self, width=350, values=[])
        self.window_list.pack(pady=5)
        
        self.refresh_btn = ctk.CTkButton(self, text="Refresh List", command=self.refresh_windows, 
                                        fg_color="#333333", hover_color="#444444")
        self.refresh_btn.pack(pady=10)

        # --- Status Indicator ---
        self.status_box = ctk.CTkLabel(self, text="● System Ready", text_color="gray", font=("Roboto", 12))
        self.status_box.pack(pady=10)

        # --- Control Button ---
        self.start_btn = ctk.CTkButton(self, text="START TAPPING", font=("Roboto", 14, "bold"),
                                       fg_color="#00C853", hover_color="#00E676",
                                       height=50, command=self.toggle_action)
        self.start_btn.pack(pady=20, padx=20, fill="x")

        self.refresh_windows()

    def refresh_windows(self):
        # Define what we want to ignore
        # self.title is the title of your program ("TikTok Live Auto Liker / Tapper")
        excluded_keywords = ["notepad", "cmd.exe", "command prompt", self.title().lower()]
        
        # Filter: Must contain "TikTok" AND NOT contain any excluded keywords
        titles = [
            w.title for w in gw.getAllWindows() 
            if "tiktok" in w.title.lower() 
            and not any(excl in w.title.lower() for excl in excluded_keywords)
            and w.title != ""
        ]
        
        unique_titles = sorted(list(set(titles)))
        
        if unique_titles:
            self.window_list.configure(values=unique_titles)
            self.window_list.set(unique_titles[0])
            self.status_box.configure(text=f"● Found {len(unique_titles)} TikTok window(s)", text_color="gray")
        else:
            self.window_list.configure(values=[])
            self.window_list.set("No valid TikTok windows found")
            self.status_box.configure(text="● Waiting for TikTok window...", text_color="#D32F2F")

    def toggle_action(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.configure(text="STOP TAPPING", fg_color="#D32F2F", hover_color="#F44336")
            self.status_box.configure(text="● ACTIVE: Tapping 'L'", text_color="#00C853")
            threading.Thread(target=self.run_tapper, daemon=True).start()
        else:
            self.is_running = False
            self.start_btn.configure(text="START TAPPING", fg_color="#00C853", hover_color="#00E676")
            self.status_box.configure(text="● Stopped", text_color="gray")

    def run_tapper(self):
        target_title = self.window_list.get()
        hwnd = win32gui.FindWindow(None, target_title)
        
        if not hwnd:
            self.is_running = False
            return

        L_KEY = 0x4C

        while self.is_running:
            # Force background focus signal
            win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
            
            # Send the key press
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, L_KEY, 0)
            win32api.PostMessage(hwnd, win32con.WM_CHAR, L_KEY, 0)
            
            time.sleep(0.1) # Frequency of likes

if __name__ == "__main__":
    app = TikTokAutoLiker()
    app.mainloop()