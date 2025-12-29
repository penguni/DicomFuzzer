import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from tester.backend import TesterComponents

class TesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Fuzzer Tester - Reference Node")
        self.root.geometry("700x550")
        
        self.backend = TesterComponents(self.log_message)
        
        # UI State Variables
        self.mode = tk.StringVar(value="SCP")
        self.target_ip = tk.StringVar(value="127.0.0.1")
        self.target_port = tk.IntVar(value=11112)
        self.listen_port = tk.IntVar(value=10104) # Default Tester Port
        self.my_ae = tk.StringVar(value="TESTER_SCU")
        self.target_ae = tk.StringVar(value="FUZZER_SCP")
        
        self.is_server_running = False

        self._build_ui()
    
    def log_message(self, msg):
        def _append():
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, msg + "\n")
            self.log_area.configure(state='disabled')
            self.log_area.see(tk.END)
        self.root.after(0, _append)

    def _build_ui(self):
        # Mode Selection
        mode_frame = ttk.LabelFrame(self.root, text="Tester Mode", padding=10)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Radiobutton(mode_frame, text="SCU Mode (Act as Client -> Test Fuzzer Server)", 
                        variable=self.mode, value="SCU", command=self._update_state).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="SCP Mode (Act as Server -> Test Fuzzer Client)", 
                        variable=self.mode, value="SCP", command=self._update_state).pack(anchor="w")

        # Configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for config
        ttk.Label(config_frame, text="Target IP:").grid(row=0, column=0, sticky="w")
        self.ent_ip = ttk.Entry(config_frame, textvariable=self.target_ip)
        self.ent_ip.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Target Port:").grid(row=0, column=2, sticky="w")
        self.ent_tport = ttk.Entry(config_frame, textvariable=self.target_port)
        self.ent_tport.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(config_frame, text="Listen Port:").grid(row=1, column=0, sticky="w")
        self.ent_lport = ttk.Entry(config_frame, textvariable=self.listen_port)
        self.ent_lport.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="My AE Title:").grid(row=2, column=0, sticky="w")
        ttk.Entry(config_frame, textvariable=self.my_ae).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(config_frame, text="Target AE Title:").grid(row=2, column=2, sticky="w")
        self.ent_tae = ttk.Entry(config_frame, textvariable=self.target_ae)
        self.ent_tae.grid(row=2, column=3, padx=5, pady=2)

        # Actions
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill="x", padx=10)
        
        self.btn_scu_action = ttk.Button(action_frame, text="Send C-ECHO", command=self._run_echo)
        self.btn_scu_action.pack(side="left", padx=5)
        
        self.btn_server_toggle = ttk.Button(action_frame, text="Start Server", command=self._toggle_server)
        self.btn_server_toggle.pack(side="left", padx=5)
        
        self.btn_clear = ttk.Button(action_frame, text="Clear Log", command=self._clear_log)
        self.btn_clear.pack(side="right", padx=5)

        # Logs
        log_frame = ttk.LabelFrame(self.root, text="Interaction Logs", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, state='disabled')
        self.log_area.pack(fill="both", expand=True)

        self._update_state()

    def _clear_log(self):
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')

    def _update_state(self):
        mode = self.mode.get()
        if mode == "SCU":
            self.ent_ip.config(state="normal")
            self.ent_tport.config(state="normal")
            self.ent_tae.config(state="normal")
            self.ent_lport.config(state="disabled")
            
            self.btn_scu_action.config(state="normal")
            self.btn_server_toggle.config(state="disabled")
            
            # Stop server if running when switching to SCU
            if self.is_server_running:
                self._toggle_server() 

        else: # SCP
            self.ent_ip.config(state="disabled")
            self.ent_tport.config(state="disabled") # We don't need target port if we are server
            self.ent_tae.config(state="disabled")
            self.ent_lport.config(state="normal")
            
            self.btn_scu_action.config(state="disabled")
            self.btn_server_toggle.config(state="normal")

    def _run_echo(self):
        # Runs in a thread to avoid freezing UI
        t = threading.Thread(target=self.backend.run_scu_echo, args=(
            self.target_ip.get(), 
            self.target_port.get(),
            self.my_ae.get(),
            self.target_ae.get()
        ))
        t.start()

    def _toggle_server(self):
        if not self.is_server_running:
            # Start
            port = self.listen_port.get()
            ae = self.my_ae.get()
            if self.backend.start_scp_server(ae, port):
                self.is_server_running = True
                self.btn_server_toggle.config(text="Stop Server")
        else:
            # Stop
            self.backend.stop_scp_server()
            self.is_server_running = False
            self.btn_server_toggle.config(text="Start Server")
