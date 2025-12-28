from pynetdicom import AE, debug_logger
from pydicom.uid import CTImageStorage
# Verification SOP Class UID
VerificationSOPClass = '1.2.840.10008.1.1'
from pydicom.dataset import Dataset

class DicomSCU:
    def __init__(self, target_ip, target_port, config=None):
        self.target_ip = target_ip
        self.target_port = target_port
        self.config = config or {}
        self.ae = AE()
        
        # Determine calling and called AE titles
        ae_params = self.config.get('ae_title_params', {})
        self.calling_ae = ae_params.get('calling_ae', 'FUZZER_SCU')
        self.called_ae = ae_params.get('called_ae', 'TARGET_SCP')
        
        self.ae.ae_title = self.calling_ae
        
        # Add requested presentation contexts
        self.ae.add_requested_context(VerificationSOPClass)
        self.ae.add_requested_context(CTImageStorage)
        # We can add more contexts here as needed or make it configurable

    def echo(self):
        """Perform a C-ECHO to test connectivity."""
        assoc = self.ae.associate(self.target_ip, self.target_port, ae_title=self.called_ae)
        if assoc.is_established:
            status = assoc.send_c_echo()
            assoc.release()
            
            if status:
                return status.Status == 0x0000
        return False

    def send_dataset(self, dataset):
        """Send a DICOM dataset using C-STORE."""
        assoc = self.ae.associate(self.target_ip, self.target_port, ae_title=self.called_ae)
        if assoc.is_established:
            # We assume CT Image Storage for now, ideally this should match the dataset's SOP Class UID
            status = assoc.send_c_store(dataset)
            assoc.release()
            return status
        return None
