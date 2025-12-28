import unittest
from pydicom.dataset import Dataset
from fuzzer.mutator import Mutator

class TestMutator(unittest.TestCase):
    def setUp(self):
        self.config = {'strategies': ['bit_flip'], 'seed': 12345}
        self.mutator = Mutator(self.config)
        
        self.ds = Dataset()
        self.ds.PatientName = "TESTNAME"
        self.ds.PatientID = "11111"

    def test_bit_flip_changes_content(self):
        mutated = self.mutator.mutate(self.ds)
        # Check that it's different
        # Note: With a fixed seed and known strategy, we expect a change.
        self.assertNotEqual(str(mutated.PatientName), "TESTNAME")
        
    def test_mutation_does_not_affect_original(self):
        mutated = self.mutator.mutate(self.ds)
        self.assertEqual(str(self.ds.PatientName), "TESTNAME")

if __name__ == '__main__':
    unittest.main()
