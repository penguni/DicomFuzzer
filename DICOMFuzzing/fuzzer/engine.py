import time
import random
from pydicom.dataset import Dataset
from .mutator import Mutator
# from network.scu import DicomSCU # Circular import if not careful, better to inject SCU or import inside

class FuzzingEngine:
    def __init__(self, target_ip, target_port, config):
        self.target_ip = target_ip
        self.target_port = target_port
        self.config = config
        self.mutator = Mutator(config.get('fuzzer', {}))
        
        # Deferred import to avoid circular dependency if organized that way, 
        # but here we can just import at top if structure allows.
        from network.scu import DicomSCU
        self.scu = DicomSCU(target_ip, target_port, config.get('network', {}))
        
        self.delay = config.get('fuzzer', {}).get('delay', 0.1)
        self.max_iterations = config.get('fuzzer', {}).get('max_iterations', 100)

    def run(self):
        print(f"Starting fuzzing on {self.target_ip}:{self.target_port}")
        
        for i in range(self.max_iterations):
            print(f"Iteration {i+1}/{self.max_iterations}")
            
            # Create a base dataset (dummy)
            ds = self._create_base_dataset()
            
            # Mutate it
            mutated_ds = self.mutator.mutate(ds)
            
            # Send it
            try:
                status = self.scu.send_dataset(mutated_ds)
                if status:
                    print(f"  Response: {status.Status}")
                else:
                    print("  Failed to associate or send")
            except Exception as e:
                print(f"  Error sending: {e}")
                
            time.sleep(self.delay)

    def _create_base_dataset(self):
        """Creates a valid dummy DICOM dataset to start with."""
        ds = Dataset()
        ds.PatientName = "Test^Fuzz"
        ds.PatientID = "123456"
        # Add minimal required tags for a valid object (e.g. CT Image)
        # For real fuzzing, we might load a seed file from disk.
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2' # CT Image Storage
        ds.SOPInstanceUID = '1.2.3.4.5.6.7'
        return ds
