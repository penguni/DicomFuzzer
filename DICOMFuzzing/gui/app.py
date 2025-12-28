import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import logging
from fuzzer.engine import FuzzingEngine
from network.scp import DicomSCP

class TextHandler(logging.Handler):
    """Custom logging handler to redirect logs to a Tkinter Text widget."""
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)

class FuzzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Fuzzing Tool")
        self.root.geometry("600x600")

        # Config Variables
        self.mode = tk.StringVar(value="SCU") # SCU (Server Fuzzer) or SCP (Client Fuzzer)
        self.target_ip = tk.StringVar(value="127.0.0.1")
        self.target_port = tk.IntVar(value=11112)
        self.seed = tk.IntVar(value=12345)
        self.strategy = tk.StringVar(value="bit_flip")
        self.running = False
        self.active_thread = None
        self.scp_server = None

        self._create_widgets()

    def _create_widgets(self):
        # Mode Selection
        mode_frame = ttk.LabelFrame(self.root, text="Fuzzing Mode", padding="10")
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Server Fuzzer (I am Client/SCU)", variable=self.mode, value="SCU", command=self._update_ui_state).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="Client Fuzzer (I am Server/SCP)", variable=self.mode, value="SCP", command=self._update_ui_state).pack(side="left", padx=10)

        # Settings Frame
        self.settings_frame = ttk.LabelFrame(self.root, text="Configuration", padding="10")
        self.settings_frame.pack(fill="x", padx=10, pady=5)

        # Labels will update based on mode
        self.lbl_ip = ttk.Label(self.settings_frame, text="Target IP:")
        self.lbl_ip.grid(row=0, column=0, sticky="w")
        self.entry_ip = ttk.Entry(self.settings_frame, textvariable=self.target_ip)
        self.entry_ip.grid(row=0, column=1, padx=5, pady=2)

        self.lbl_port = ttk.Label(self.settings_frame, text="Target Port:")
        self.lbl_port.grid(row=0, column=2, sticky="w")
        ttk.Entry(self.settings_frame, textvariable=self.target_port).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(self.settings_frame, text="Seed:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.settings_frame, textvariable=self.seed).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self.settings_frame, text="Strategy:").grid(row=1, column=2, sticky="w")
        self.strategy_cb = ttk.Combobox(self.settings_frame, textvariable=self.strategy, values=["bit_flip", "byte_flip", "int_overflow", "delay", "random_status"])
        self.strategy_cb.grid(row=1, column=3, padx=5, pady=2)

        # Control Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_fuzzing)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_fuzzing, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Log Area
        log_frame = ttk.LabelFrame(self.root, text="Logs", padding="5")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=15)
        self.log_text.pack(fill="both", expand=True)

        # Setup Logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        text_handler = TextHandler(self.log_text)
        self.logger.addHandler(text_handler)
        
        self._update_ui_state()

    def _update_ui_state(self):
        if self.mode.get() == "SCU":
            self.lbl_ip.config(text="Target IP:")
            self.lbl_port.config(text="Target Port:")
            self.entry_ip.config(state="normal")
            self.strategy_cb['values'] = ["bit_flip", "byte_flip", "int_overflow"]
        else:
            self.lbl_ip.config(text="Bind IP (ignored):")
            self.lbl_port.config(text="Listen Port:")
            self.entry_ip.config(state="disabled") # SCP usually listens on 0.0.0.0
            self.strategy_cb['values'] = ["delay", "random_status"]

    def start_fuzzing(self):
        if self.running:
            return
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        mode = self.mode.get()
        
        if mode == "SCU":
            config = {
                'fuzzer': {
                    'seed': self.seed.get(),
                    'strategies': [self.strategy.get()],
                    'delay': 0.1,
                    'max_iterations': 100
                },
                'network': {
                    'ae_title_params': {'calling_ae': 'GUI_SCU', 'called_ae': 'TARGET_SCP'}
                }
            }
            self.active_thread = threading.Thread(target=self._run_scu_thread, args=(config,))
            self.active_thread.start()
            
        elif mode == "SCP":
            config = {
                'fuzz_strategy': self.strategy.get(),
                'delay': 2.0, # Example delay amount
                'ae_title': 'FUZZER_SCP'
            }
            self.active_thread = threading.Thread(target=self._run_scp_thread, args=(config,))
            self.active_thread.start()

    def stop_fuzzing(self):
        if self.mode.get() == "SCP" and self.scp_server:
             self.logger.info("Stopping SCP Server...")
             self.scp_server.stop()
             self.scp_server = None
        
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.logger.info("Stop requested...")

    def _run_scu_thread(self, config):
        try:
            self.logger.info("Initializing SCU Fuzzer Engine...")
            engine = FuzzingEngine(self.target_ip.get(), self.target_port.get(), config)
            engine.run()
            self.logger.info("SCU Fuzzing complete.")
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            self.root.after(0, self._reset_ui)

    def _run_scp_thread(self, config):
        try:
            port = self.target_port.get()
            self.logger.info(f"Starting SCP Server on port {port}...")
            self.scp_server = DicomSCP(port, config)
            self.scp_server.start(blocking=True) # Blocking call, runs until stopped
            self.logger.info("SCP Server stopped.")
        except Exception as e:
            self.logger.error(f"Error in SCP: {e}")
        finally:
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

def main():
    root = tk.Tk()
    app = FuzzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
