import logging
from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import Verification, CTImageStorage, MRImageStorage, SecondaryCaptureImageStorage

class TesterComponents:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.scp = None
        self.logger = logging.getLogger("TesterBackend")
        # Ensure we don't have double handlers if this is re-instantiated
        if not self.logger.handlers:
             # Create a custom handler that routes to the callback
            class CallbackHandler(logging.Handler):
                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback
                
                def emit(self, record):
                    msg = self.format(record)
                    self.callback(f"[LOG] {msg}")

            handler = CallbackHandler(log_callback)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def start_scp_server(self, title, port):
        """Starts a DICOM SCP Server."""
        try:
            self.ae = AE(ae_title=title)
            # Support Verification (C-ECHO)
            self.ae.add_supported_context(Verification)
            # Support common Storage classes
            for sop in [CTImageStorage, MRImageStorage, SecondaryCaptureImageStorage]:
                self.ae.add_supported_context(sop)

            handlers = [
                (evt.EVT_C_STORE, self._handle_store),
                (evt.EVT_C_ECHO, self._handle_echo),
                (evt.EVT_CONN_OPEN, self._handle_open),
                (evt.EVT_CONN_CLOSE, self._handle_close),
                (evt.EVT_ACCEPTED_ASSO, self._handle_accepted),
                (evt.EVT_REJECTED_ASSO, self._handle_rejected),
                (evt.EVT_ABORTED, self._handle_aborted),
            ]

            self.log(f"Starting SCP Server regarding AE Title '{title}' on port {port}...")
            # non-blocking start
            self.scp = self.ae.start_server(('', port), block=False, evt_handlers=handlers)
            self.log(f"SCP Server actively listening on port {port}.")
            return True
        except Exception as e:
            self.log(f"Failed to start SCP Server: {e}")
            return False

    def stop_scp_server(self):
        if self.scp:
            self.scp.shutdown()
            self.scp = None
            self.log("SCP Server stopped.")

    def run_scu_echo(self, target_ip, target_port, calling_ae, called_ae):
        """Runs a C-ECHO request to target."""
        try:
            ae = AE(ae_title=calling_ae)
            ae.add_requested_context(Verification)

            self.log(f"Sending C-ECHO to {target_ip}:{target_port} (Called AE: {called_ae})...")
            assoc = ae.associate(target_ip, target_port, ae_title=called_ae)

            if assoc.is_established:
                status = assoc.send_c_echo()
                if status:
                    self.log(f"C-ECHO Response: {status.Status}")
                else:
                     self.log("C-ECHO Failed: Timed out or no response.")
                assoc.release()
            else:
                self.log(f"Association Rejected or Failed to Connect.")
        except Exception as e:
            self.log(f"SCU Error: {e}")

    # --- Handlers ---
    def _handle_open(self, event):
        self.log(f"Connection opened from {event.assoc.requestor.address}")

    def _handle_close(self, event):
        self.log("Connection closed.")

    def _handle_accepted(self, event):
        self.log(f"Association Accepted. Requestor AE: {event.assoc.requestor.ae_title}")

    def _handle_rejected(self, event):
        self.log("Association Rejected.")

    def _handle_aborted(self, event):
        self.log("Association Aborted.")

    def _handle_echo(self, event):
        self.log("Received C-ECHO Request.")
        return 0x0000 # Success

    def _handle_store(self, event):
        try:
            ds = event.dataset
            ds.file_meta = event.file_meta
            self.log(f"Received C-STORE Request. SOP Class: {ds.SOPClassUID}")
            # We don't save file for now, just acknowledge receipt
            return 0x0000 # Success
        except Exception as e:
            self.log(f"Error handling C-STORE: {e}")
            return 0xC000 # Error
