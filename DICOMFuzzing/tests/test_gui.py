import unittest
from unittest.mock import MagicMock, patch
import sys

# Define Fakes for Tkinter Variables
class FakeVar:
    def __init__(self, value=None):
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value

# Mock tkinter module
mock_tk = MagicMock()
mock_tk.StringVar = FakeVar
mock_tk.IntVar = FakeVar
mock_tk.Tk = MagicMock
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()

# Now import the app
from gui.app import FuzzerApp

class TestFuzzerApp(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        # Re-initialize app for each test
        self.app = FuzzerApp(self.root)

    def test_initial_state(self):
        # Check default values using our FakeVar
        self.assertEqual(self.app.target_ip.get(), "127.0.0.1")
        self.assertEqual(self.app.target_port.get(), 11112)
        self.assertFalse(self.app.running)

    @patch('gui.app.FuzzingEngine')
    @patch('gui.app.threading.Thread')
    def test_start_fuzzing(self, mock_thread, mock_engine):
        # Configure mocks for UI elements that are created in __init__
        self.app.start_btn = MagicMock()
        self.app.stop_btn = MagicMock()
        self.app.log_text = MagicMock()
        
        # Action
        self.app.start_fuzzing()
        
        # Assertions
        self.assertTrue(self.app.running)
        mock_thread.assert_called_once()
        self.app.start_btn.config.assert_called_with(state="disabled")
        self.app.stop_btn.config.assert_called_with(state="normal")

    def test_stop_fuzzing(self):
        self.app.running = True
        self.app.start_btn = MagicMock()
        self.app.stop_btn = MagicMock()
        
        self.app.stop_fuzzing()
        
        self.assertFalse(self.app.running)
        self.app.start_btn.config.assert_called_with(state="normal")
        self.app.stop_btn.config.assert_called_with(state="disabled")

if __name__ == '__main__':
    unittest.main()
