import unittest
import threading
import time
import socket
from pynetdicom import AE
# Verification SOP Class UID
VerificationSOPClass = '1.2.840.10008.1.1'
from network.scp import DicomSCP

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class TestSCPIntegration(unittest.TestCase):
    def setUp(self):
        self.port = find_free_port()
        self.delay = 1.0
        self.config = {
            'ae_title': 'TEST_SCP',
            'fuzz_strategy': 'delay',
            'delay': self.delay
        }
        self.scp = DicomSCP(self.port, self.config)
        self.scp_thread = threading.Thread(target=self.scp.start, kwargs={'blocking': True})
        self.scp_thread.start()
        # Give it a moment to start
        time.sleep(0.5)

    def tearDown(self):
        self.scp.stop()
        self.scp_thread.join(timeout=2)

    def test_delay_strategy(self):
        ae = AE()
        ae.add_requested_context(VerificationSOPClass)
        
        start_time = time.time()
        assoc = ae.associate('127.0.0.1', self.port)
        if assoc.is_established:
            status = assoc.send_c_echo()
            assoc.release()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Check if duration includes the delay
            # Note: Association overhead + delay. 
            self.assertGreaterEqual(duration, self.delay, "Response time should be at least the configured delay")
            # Loose upper bound to avoid flakiness
            self.assertLess(duration, self.delay + 2.0, "Response time shouldn't be too long")
            self.assertEqual(status.Status, 0x0000)
        else:
            self.fail("Failed to associate with SCP")

if __name__ == '__main__':
    unittest.main()
