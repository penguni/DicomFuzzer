
import sys
import os
import time
# Add parent dir
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from network.scp import DicomSCP

def main():
    print("[Fuzzer-Headless] Starting SCP on port 11112...")
    config = {
        'fuzz_strategy': 'random_status', 
        'delay': 0,
        'ae_title': 'FUZZER_SCP'
    }
    scp = DicomSCP(11112, config)
    # Start blocking
    scp.start(blocking=True)

if __name__ == "__main__":
    main()
