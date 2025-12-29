# DICOM Fuzzer Tester - User Guide

This guide explains how to use the **DICOM Fuzzer Tester** to verify the functionality and robustness of the **DICOM Fuzzing Tool**.

## 1. Overview
The **Tester** is a separate application that acts as a Reference DICOM Node. It can behave as:
- **SCU (Client)**: To send standard DICOM requests to the Fuzzer (when Fuzzer is in Server mode).
- **SCP (Server)**: To receive DICOM requests from the Fuzzer (when Fuzzer is in Client mode).

## 2. Launching the Tester
Run the following command in your terminal:
```bash
python c:\SWJ\Antigravity\DICOMFuzzing\tester\main.py
```

## 3. Testing Scenarios

### Scenario A: Testing the Fuzzer's Client (SCU) Fuzzing
In this scenario, the Fuzzer acts as a Client sending malformed data, and the Tester acts as a Server (SCP) to receive it.

1. **Configure Tester (Server Role)**
   - Select **SCP Mode**.
   - **Listen Port**: Set to `10104` (or any free port).
   - Click **Start Server**.
   - *Status*: Tester is now listening for connections.

2. **Configure Fuzzer (Client Role)**
   - Launch the Fuzzer App.
   - Select **Server Fuzzer (I am SCU)**.
   - **Target IP**: `127.0.0.1`
   - **Target Port**: `10104` (Must match Tester's listen port).
   - Select a Fuzzing Strategy (e.g., `bit_flip`, `int_overflow`).
   - Click **Start**.

3. **Verify**
   - Watch the **Tester's Log**. You should see incoming connections and data.
   - If the Fuzzer sends invalid data, the Tester Log might show errors or rejected associations.
   - **Goal**: The Tester should not crash even if it receives garbage. The Log should reflect the anomalies.

### Scenario B: Testing the Fuzzer's Server (SCP) Fuzzing
In this scenario, the Fuzzer acts as a Server (potentially with delays or random statuses), and the Tester acts as a Client (SCU).

1. **Configure Fuzzer (Server Role)**
   - Launch the Fuzzer App.
   - Select **Client Fuzzer (I am SCP)**.
   - **Listen Port**: `11112`.
   - Select a Strategy (e.g., `random_status`, `delay`).
   - Click **Start**.

2. **Configure Tester (Client Role)**
   - Select **SCU Mode**.
   - **Target IP**: `127.0.0.1`
   - **Target Port**: `11112` (Must match Fuzzer's port).
   - Click **Send C-ECHO**.

3. **Verify**
   - Watch the **Tester's Log**.
   - If Fuzzer is delaying, you'll see a pause before the response.
   - If Fuzzer sends random statuses, you'll see different Status codes in the log (not just Success `0x0000`).

## 4. Troubleshooting
- **Address in Use**: If you can't start the server, check if the port is already taken.
- **Connection Refused**: Ensure the Target IP/Port matches exactly.
