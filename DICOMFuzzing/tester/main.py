import tkinter as tk
import sys
import os
import argparse
import time

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tester.backend import TesterComponents

def run_cli_scu(args):
    print("[CLI] Starting Tester in SCU Mode...")
    components = TesterComponents(lambda msg: print(msg))
    components.run_scu_echo(args.target_ip, args.target_port, args.ae_title, args.target_ae)
    print("[CLI] SCU Action Completed.")

def run_cli_scp(args):
    print(f"[CLI] Starting Tester in SCP Mode on port {args.listen_port}...")
    components = TesterComponents(lambda msg: print(msg))
    if components.start_scp_server(args.ae_title, args.listen_port):
        print(f"[CLI] Server running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[CLI] Stopping Server...")
            components.stop_scp_server()

def main():
    parser = argparse.ArgumentParser(description="DICOM Fuzzer Tester")
    parser.add_argument("--mode", choices=["GUI", "SCU", "SCP"], default="GUI", help="Operation mode")
    parser.add_argument("--target-ip", default="127.0.0.1", help="Target IP for SCU")
    parser.add_argument("--target-port", type=int, default=11112, help="Target Port for SCU")
    parser.add_argument("--listen-port", type=int, default=10104, help="Listen Port for SCP")
    parser.add_argument("--ae-title", default="TESTER", help="My AE Title")
    parser.add_argument("--target-ae", default="FW_TARGET", help="Target AE Title")
    
    args = parser.parse_args()

    if args.mode == "GUI":
        from tester.gui import TesterApp
        root = tk.Tk()
        app = TesterApp(root)
        root.mainloop()
    elif args.mode == "SCU":
        run_cli_scu(args)
    elif args.mode == "SCP":
        run_cli_scp(args)

if __name__ == "__main__":
    main()
