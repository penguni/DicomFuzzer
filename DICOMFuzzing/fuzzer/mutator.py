import random
from pydicom.dataset import Dataset

class Mutator:
    def __init__(self, config):
        self.strategies = config.get('strategies', ['bit_flip'])
        self.seed = config.get('seed', 12345)
        random.seed(self.seed)

    def mutate(self, dataset: Dataset) -> Dataset:
        """Apply a random mutation strategy to the dataset."""
        strategy = random.choice(self.strategies)
        
        # Clone dataset to avoid modifying original? 
        # pydicom datasets are mutable. Deepcopy might be needed if we reuse the base.
        import copy
        mutated_ds = copy.deepcopy(dataset)
        
        if strategy == 'bit_flip':
            self._bit_flip(mutated_ds)
        elif strategy == 'byte_flip':
            self._byte_flip(mutated_ds)
        elif strategy == 'int_overflow':
            self._int_overflow(mutated_ds)
            
        return mutated_ds

    def _bit_flip(self, ds):
        # Simplistic implementation: Modify a string field
        if 'PatientName' in ds:
            val = str(ds.PatientName)
            if val:
                idx = random.randint(0, len(val)-1)
                # Flip a bit in the character? Or just replace with random char?
                # For string, replacing char is easier to demonstrate
                new_char = chr(ord(val[idx]) ^ 0xFF)
                ds.PatientName = val[:idx] + new_char + val[idx+1:]

    def _byte_flip(self, ds):
        # Placeholder
        pass

    def _int_overflow(self, ds):
        # Placeholder
        pass
