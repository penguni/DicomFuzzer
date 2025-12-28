# DICOM Fuzzing Tool

A Python-based fuzzing tool for testing the security of DICOM medical devices.

## Features
- **DICOM Networking**: Acts as an SCU (Service Class User) to send datasets to target SCPs (Service Class Providers).
- **Fuzzing Engine**: Mutation-based fuzzing to generate malformed DICOM packets.
- **Strategies**: Bit-flipping, integer overflow, format string injection, and more.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python main.py --target <IP> --port <PORT> --mode <MODE>
```

Example:
```bash
python main.py --target 127.0.0.1 --port 11112 --mode fuzz
```
