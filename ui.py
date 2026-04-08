import customtkinter as ctk
import threading
import sys
import ctypes

from scanner import scan_for_games
from scraper import get_latest_versions, download_file
from updater import inject_dll
from registry_mgr import set_dlss_indicator, schedule_removal_task, remove_scheduled_task

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DLSS Patcher")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        # Data storage
        self.games = []
        self.versions = {"DLSS": [], "Ray Reconstruction": [], "Frame Generation": []}

        self.setup_ui()
        self.start_background_fetches()



    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Indicator Controls
        frame_indicator = ctk.CTkFrame(self)
        frame_indicator.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.indicator_var = ctk.BooleanVar(value=False)
        indicator_switch = ctk.CTkSwitch(frame_indicator, text="Enable DLSS On-Screen Indicator", 
                                         variable=self.indicator_var, command=self.on_indicator_toggle)
        indicator_switch.pack(side="left", padx=20, pady=10)
        
        self.task_var = ctk.BooleanVar(value=False)
        self.task_check = ctk.CTkCheckBox(frame_indicator, text="Remove DLSS Overlay in 4 hours", 
                                          variable=self.task_var, state="disabled")
        self.task_check.pack(side="left", padx=20, pady=10)

        # 2. Game Selection
        frame_game = ctk.CTkFrame(self)
        frame_game.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame_game, text="1. Select Game:", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.btn_scan = ctk.CTkButton(frame_game, text="Scan Local Drives", command=self.start_scan)
        self.btn_scan.pack(pady=10, padx=10, fill="x")
        
        self.combo_game = ctk.CTkComboBox(frame_game, values=["Scan to find games..."])
        self.combo_game.pack(pady=10, padx=10, fill="x")

        # 3. Version Selection
        frame_version = ctk.CTkFrame(self)
        frame_version.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame_version, text="2. Select Updates:", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.combo_dlss = ctk.CTkComboBox(frame_version, values=["Fetching..."])
        self.combo_dlss.pack(pady=10, padx=10, fill="x")
        
        self.combo_rr = ctk.CTkComboBox(frame_version, values=["Fetching..."])
        self.combo_rr.pack(pady=10, padx=10, fill="x")
        
        self.combo_fg = ctk.CTkComboBox(frame_version, values=["Fetching..."])
        self.combo_fg.pack(pady=10, padx=10, fill="x")

        # 4. Action Area
        frame_action = ctk.CTkFrame(self)
        frame_action.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.btn_update = ctk.CTkButton(frame_action, text="Download & Inject", command=self.start_update, height=40, font=("Arial", 14, "bold"))
        self.btn_update.pack(pady=10, padx=20, fill="x")
        
        self.progress = ctk.CTkProgressBar(frame_action)
        self.progress.pack(pady=5, padx=20, fill="x")
        self.progress.set(0)

        # 5. Logs
        self.log_box = ctk.CTkTextbox(self, height=150)
        self.log_box.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.log("Application started.")

    def log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def on_indicator_toggle(self):
        if self.indicator_var.get():
            self.task_check.configure(state="normal")
            success, err = set_dlss_indicator(True)
            if success:
                self.log("DLSS Indicator Enabled in Registry.")
            else:
                self.log(f"Failed to enable DLSS Indicator: {err}")
        else:
            self.task_check.deselect()
            self.task_check.configure(state="disabled")
            success, err = set_dlss_indicator(False)
            if success:
                self.log("DLSS Indicator Disabled in Registry.")
            else:
                self.log(f"Failed to disable DLSS Indicator: {err}")
            remove_scheduled_task()

    # --------------- BACKGROUND TASKS ---------------

    def start_background_fetches(self):
        threading.Thread(target=self.fetch_versions_thread, daemon=True).start()

    def fetch_versions_thread(self):
        self.log("Fetching latest versions from TechPowerUp...")
        for dtype in ["DLSS", "Ray Reconstruction", "Frame Generation"]:
            try:
                self.after(0, self.log, f"Scraping category: {dtype}...")
                versions = get_latest_versions(dtype, 5)
                self.versions[dtype] = versions
                
                # Update UI safely
                self.after(0, self.update_version_combo, dtype, versions)
            except Exception as e:
                self.after(0, self.log, f"Error fetching {dtype}: {e}")
                
        self.log("Finished fetching versions.")

    def update_version_combo(self, dtype, versions):
        labels = ["None"] + [v['version'] for v in versions] if versions else ["None available"]
        if dtype == "DLSS":
            self.combo_dlss.configure(values=labels)
            if labels: self.combo_dlss.set(labels[1] if len(labels) > 1 else labels[0])
        elif dtype == "Ray Reconstruction":
            self.combo_rr.configure(values=labels)
            if labels: self.combo_rr.set(labels[0]) # Default to None to be safe, except DLSS usually requested
        elif dtype == "Frame Generation":
            self.combo_fg.configure(values=labels)
            if labels: self.combo_fg.set(labels[0])

    def start_scan(self):
        self.btn_scan.configure(state="disabled")
        threading.Thread(target=self.scan_thread, daemon=True).start()

    def scan_thread(self):
        self.log("Starting local drive scan...")
        
        def p_cb(msg):
            self.after(0, self.log, msg)
            
        found = scan_for_games(progress_callback=p_cb)
        self.games = found
        
        self.after(0, self.update_games_combo, found)

    def update_games_combo(self, found_games):
        self.btn_scan.configure(state="normal")
        if not found_games:
            self.combo_game.configure(values=["No games found."])
            self.combo_game.set("No games found.")
            return
            
        labels = [f"{g['name']} ({g['path']})" for g in found_games]
        self.combo_game.configure(values=labels)
        self.combo_game.set(labels[0])

    # --------------- UPDATE LOGIC ---------------

    def start_update(self):
        idx = self.combo_game.cget("values").index(self.combo_game.get()) if self.combo_game.get() in self.combo_game.cget("values") else -1
        if idx < 0 or not self.games:
            self.log("Error: Please select a valid game.")
            return
            
        game = self.games[idx]
        
        # Schedule the task if requested
        if self.indicator_var.get() and self.task_var.get():
            success, err = schedule_removal_task()
            if success:
                self.log("Scheduled Task created: Overlay will be removed in 4 hours.")
            else:
                self.log(f"Warning: Failed to schedule removal task: {err}")
        elif not self.task_var.get():
            remove_scheduled_task()

        dlss_v = self.combo_dlss.get()
        rr_v = self.combo_rr.get()
        fg_v = self.combo_fg.get()
        
        tasks = []
        if dlss_v and dlss_v not in ("None", "None available", "Fetching..."):
            dlss_id = next((v['id'] for v in self.versions["DLSS"] if v['version'] == dlss_v), None)
            if dlss_id: tasks.append(("DLSS", dlss_id))
            
        if rr_v and rr_v not in ("None", "None available", "Fetching..."):
            rr_id = next((v['id'] for v in self.versions["Ray Reconstruction"] if v['version'] == rr_v), None)
            if rr_id: tasks.append(("Ray Reconstruction", rr_id))
            
        if fg_v and fg_v not in ("None", "None available", "Fetching..."):
            fg_id = next((v['id'] for v in self.versions["Frame Generation"] if v['version'] == fg_v), None)
            if fg_id: tasks.append(("Frame Generation", fg_id))

        if not tasks:
            self.log("Error: Please select at least one component (DLSS, Ray Recon, or Frame Gen) to update.")
            return
            
        self.btn_update.configure(state="disabled")
        self.progress.set(0)
        
        threading.Thread(target=self.update_thread, args=(game, tasks), daemon=True).start()
        
    def update_thread(self, game, tasks):
        target_dir = game['path']
        total_tasks = len(tasks)
        
        for idx, (dl_type, version_id) in enumerate(tasks):
            def p_cb(fraction):
                # We calculate current overall fraction out of all tasks
                overall = (idx + fraction) / total_tasks
                self.after(0, self.progress.set, overall)
                
            self.log(f"Downloading {dl_type} Payload for {game['name']}...")
            try:
                zip_path = download_file(dl_type, version_id, progress_callback=p_cb)
                
                self.log(f"Download complete. Injecting {dl_type} into {target_dir}...")
                # Inject
                success, msg = inject_dll(zip_path, target_dir)
                if success:
                    self.log(f"Success! {dl_type} update finished. {msg}")
                else:
                    self.log(f"Injection Failed for {dl_type}: {msg}")
                    
            except Exception as e:
                self.log(f"Update Thread Error on {dl_type}: {e}")
            
        self.after(0, lambda: self.btn_update.configure(state="normal"))
        self.after(0, lambda: self.progress.set(1.0))

