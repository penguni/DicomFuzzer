from pynetdicom import AE, evt, debug_logger
from pydicom.uid import CTImageStorage
# Verification SOP Class UID
VerificationSOPClass = '1.2.840.10008.1.1'
import logging
import time
import random

class DicomSCP:
    def __init__(self, port, config=None):
        self.port = port
        self.config = config or {}
        self.ae = AE()
        
        # Determine AE Title
        self.ae_title = self.config.get('ae_title', 'FUZZER_SCP')
        self.ae.ae_title = self.ae_title
        
        # Support common contexts
        self.ae.add_supported_context(VerificationSOPClass)
        self.ae.add_supported_context(CTImageStorage)
        
        self.server = None
        self.logger = logging.getLogger("fuzzer")

    def start(self, blocking=True):
        self.logger.info(f"Starting Malicious SCP on port {self.port}")
        
        # Handlers
        handlers = [
            (evt.EVT_C_ECHO, self.handle_echo),
            (evt.EVT_C_STORE, self.handle_store),
            (evt.EVT_CONN_OPEN, self.handle_open)
        ]
        
        self.server = self.ae.start_server(('', self.port), evt_handlers=handlers, block=blocking)

    def handle_open(self, event):
        self.logger.info(f"Connection from {event.assoc.requestor.address}:{event.assoc.requestor.port}")
        # Basic Fuzzing: Delay connection acceptance?
        # Note: This event is after AC, so delays here affect data transfer start.

    def handle_echo(self, event):
        self.logger.info("Received C-ECHO request")
        
        # Fuzzing Strategy: Random status code or Delay
        strategy = self.config.get('fuzz_strategy', 'none')
        
        if strategy == 'delay':
            delay = self.config.get('delay', 1.0)
            self.logger.info(f"Fuzzing: Delaying response by {delay}s")
            time.sleep(delay)
            return 0x0000
            
        elif strategy == 'random_status':
            # Return a non-standard status code
            status = random.choice([0xA700, 0x0110, 0xFE00]) # Refused, Processing, etc.
            self.logger.info(f"Fuzzing: Returning random status 0x{status:04X}")
            return status

        return 0x0000

    def handle_store(self, event):
        self.logger.info("Received C-STORE request")
        # Logic similar to echo
        return 0x0000

    def stop(self):
        if self.server:
            self.server.shutdown()
