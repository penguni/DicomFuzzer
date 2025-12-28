# DICOM Fuzzing Tool - GUI Guide

## 1. Starting the GUI
Run the tool with the `gui` mode argument:
```bash
python c:/SWJ/Antigravity/DICOMFuzzing/main.py --mode gui
```

## 2. Fuzzing Modes

### A. Server Fuzzer (Default)
In this mode, the tool acts as a **DICOM Client (SCU)** and attacks a target DICOM Server (SCP).
1. Select **Server Fuzzer (I am Client/SCU)**.
2. **Target IP/Port**: Enter the address of the victim server.
3. **Strategy**: Choose mutation strategies (e.g., `bit_flip`, `int_overflow`).
4. **Action**: Sends malformed DICOM datasets to the server.

### B. Client Fuzzer (New)
In this mode, the tool acts as a malicious **DICOM Server (SCP)** and attacks incoming Client (SCU) connections.
1. Select **Client Fuzzer (I am Server/SCP)**.
2. **Listen Port**: Enter the port to bind to (e.g., `11112`). IP is ignored (binds to all interfaces).
3. **Strategy**: Choose response strategies:
   - `delay`: Delays the C-ECHO/C-STORE response to cause timeouts.
   - `random_status`: Returns invalid/random status codes.
4. **Action**: Waits for a client to connect and then behaves maliciously.

## 3. Detailed Parameters

### Seed
The **Seed** is an integer value used to initialize the random number generator.
- **Purpose**: Ensures reproducibility. If you run the fuzzer twice with the same seed, it will generate the exact same sequence of mutations.
- **Usage**: Change this value to generate a new set of random test cases.

### Strategies
The strategy determines how the data is manipulated (mutated) or how the protocol is disrupted.

#### Server Fuzzer (Client/SCU) Strategies:
These apply when you are attacking a DICOM Server.
- **`bit_flip`**: Randomly flips single bits in the DICOM dataset values (e.g., changing characters in a patient name). Good for finding parsing errors.
- **`byte_flip`**: Randomly flips entire bytes (0x00 <-> 0xFF). More aggressive than bit flipping.
- **`int_overflow`**: Replaces numerical values with boundary values (e.g., MAX_INT, -1) to test for integer overflow or underflow vulnerabilities.

#### Client Fuzzer (Server/SCP) Strategies:
These apply when you are attacking a DICOM Client.
- **`delay`**: Delays the response (Association Accept or C-ECHO/C-STORE response).
  - *Effect*: Tests how the client handles network latencies and timeout conditions.
- **`random_status`**: Returns a random, often invalid, DICOM Status Code (e.g., 0xA700, 0xFE00).
  - *Effect*: Tests if the client properly handles unexpected or reserved error codes without crashing.

## 4. Running a Test

### Testing Server Fuzzer
1. Start your `storescp` (or use the dummy server).
2. Configure IP/Port in GUI.
3. Click **Start**.

### Testing Client Fuzzer
1. Select **Client Fuzzer** mode in GUI.
2. Set Port to `11112`.
3. Select `delay` strategy.
4. Click **Start**. The Logs will say "Starting SCP Server...".
5. Run the dummy client in a terminal:
   ```bash
   python c:/SWJ/Antigravity/DICOMFuzzing/tests/dummy_client.py 127.0.0.1 11112
   ```
6. Observe that the client hangs for a few seconds before getting a response (due to delay).

## 5. Verification
- **Logs**: Check the GUI log window for "Connection from..." and "Fuzzing: ..." messages.
