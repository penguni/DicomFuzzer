from pynetdicom import AE
# Verification SOP Class UID
VerificationSOPClass = '1.2.840.10008.1.1'
import sys

def test_client(target_ip, target_port):
    ae = AE()
    ae.add_requested_context(VerificationSOPClass)
    
    print(f"Connecting to {target_ip}:{target_port}...")
    assoc = ae.associate(target_ip, target_port)
    
    if assoc.is_established:
        print("Association established.")
        status = assoc.send_c_echo()
        print(f"Received Echo Status: 0x{status.Status:04X}")
        assoc.release()
    else:
        print("Failed to associate")

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 11112
    test_client(ip, port)
