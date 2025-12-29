import subprocess
import time
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXE = sys.executable
TESTER_MAIN = os.path.join(BASE_DIR, "tester", "main.py")

# We need to simulate the Fuzzer App running in SCP Mode.
# Since the Fuzzer App is GUI-heavy, we will write a temporary script that imports 
# the underlying SCP logic from 'network/scp.py' and runs it headless.
FUZZER_HEADLESS_SCRIPT = os.path.join(BASE_DIR, "tests", "run_fuzzer_scp_headless.py")

def create_fuzzer_headless_script():
    content = """
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
"""
    with open(FUZZER_HEADLESS_SCRIPT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Setup] Created headless fuzzer script: {FUZZER_HEADLESS_SCRIPT}")

def run_integration_test():
    create_fuzzer_headless_script()
    
    log_file_path = os.path.join(BASE_DIR, "integration_log.txt")
    print(f"[Test] Logs will be saved to: {log_file_path}")

    with open(log_file_path, "w", encoding="utf-8") as log_file:
        # 1. Start Fuzzer (Server)
        print("[Test] Launching Fuzzer (SCP Role)...")
        fuzzer_proc = subprocess.Popen(
            [PYTHON_EXE, FUZZER_HEADLESS_SCRIPT],
            stdout=log_file,
            stderr=log_file,
            cwd=BASE_DIR
        )
        time.sleep(2) # Wait for server startup

        # 2. Start Tester (Client) via CLI
        print("[Test] Launching Tester (SCU Role)...")
        tester_env = os.environ.copy()
        tester_proc = subprocess.Popen(
            [PYTHON_EXE, TESTER_MAIN, "--mode", "SCU", "--target-port", "11112", "--target-ae", "FUZZER_SCP"],
            stdout=log_file,
            stderr=log_file,
            cwd=BASE_DIR,
            env=tester_env
        )

        tester_proc.wait()
        print("[Test] Tester finished.")
        
        # 3. Stop Fuzzer
        fuzzer_proc.terminate()
        try:
            fuzzer_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            fuzzer_proc.kill()
        print("[Test] Fuzzer terminated.")

    # 4. Analyze Log
    analyze_logs(log_file_path)

def analyze_logs(log_path):
    print("\n[Analysis] Analyzing logs...")
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    report = []
    report.append("=== 통합 테스트 결과 보고서 (Integration Test Report) ===")
    
    if "Starting SCP on port 11112" in content:
        report.append("[PASS] Fuzzer SCP 서버 시작됨.")
    else:
        report.append("[FAIL] Fuzzer SCP 서버 시작 실패.")

    if "C-ECHO Response" in content or "Association Accepted" in content:
        report.append("[PASS] Tester SCU가 서버에 성공적으로 연결하고 응답을 받음.")
    else:
        report.append("[FAIL] Tester SCU가 응답을 받지 못함 (타임아웃 또는 연결 거부).")
        
    print("\n".join(report))
    
    # Save Korean Report
    report_path = os.path.join(BASE_DIR, "INTEGRATION_REPORT_KO.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n\n=== Raw Logs ===\n" + content)
    print(f"[Test] Korean report saved to: {report_path}")

if __name__ == "__main__":
    run_integration_test()
