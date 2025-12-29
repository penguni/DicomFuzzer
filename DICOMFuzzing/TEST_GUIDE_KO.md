# DICOM Fuzzer Tester - 사용자 가이드

이 가이드는 **DICOM Fuzzer Tester**를 사용하여 **DICOM Fuzzing Tool**의 기능과 안정성을 검증하는 방법을 설명합니다.

## 1. 개요 (Overview)
**Tester**는 표준 Reference DICOM Node 역할을 하는 별도의 애플리케이션입니다. 다음과 같이 동작할 수 있습니다:
- **SCU (Client)**: Fuzzer에게 표준 DICOM 요청을 전송 (Fuzzer가 Server 모드일 때).
- **SCP (Server)**: Fuzzer로부터 DICOM 요청을 수신 (Fuzzer가 Client 모드일 때).

## 2. Tester 실행 방법
터미널에서 다음 명령어를 실행하세요:
```bash
python c:\SWJ\Antigravity\DICOMFuzzing\tester\main.py
```

## 3. 테스트 시나리오

### 시나리오 A: Fuzzer의 Client (SCU) Fuzzing 테스트
이 시나리오에서는 Fuzzer가 Client로서 비정상적인 데이터를 보내고, Tester가 Server (SCP)로서 이를 받습니다.

1. **Tester 설정 (Server 역할)**
   - **SCP Mode**를 선택합니다.
   - **Listen Port**: `10104` (또는 사용 가능한 포트)로 설정합니다.
   - **Start Server** 클릭.
   - *상태*: Tester가 연결을 대기 중입니다.

2. **Fuzzer 설정 (Client 역할)**
   - Fuzzer 앱을 실행합니다.
   - **Server Fuzzer (I am SCU)** 선택.
   - **Target IP**: `127.0.0.1`
   - **Target Port**: `10104` (Tester의 Listen Port와 일치해야 함).
   - Fuzzing Strategy 선택 (예: `bit_flip`, `int_overflow`).
   - **Start** 클릭.

3. **검증 (Verify)**
   - **Tester의 Log**를 확인합니다. 들어오는 연결과 데이터가 표시되어야 합니다.
   - Fuzzer가 유효하지 않은 데이터를 보내면 Tester 로그에 오류나 연결 거부(Rejected)가 표시될 수 있습니다.
   - **목표**: Tester는 쓰레기 값(garbage)을 받더라도 충돌(Crash)하지 않아야 합니다. 로그에 이상 징후가 기록되는지 확인하세요.

### 시나리오 B: Fuzzer의 Server (SCP) Fuzzing 테스트
이 시나리오에서는 Fuzzer가 Server로서 동작(지연 응답이나 무작위 상태 코드 반환 등)하고, Tester가 Client (SCU)로서 요청을 보냅니다.

1. **Fuzzer 설정 (Server 역할)**
   - Fuzzer 앱을 실행합니다.
   - **Client Fuzzer (I am SCP)** 선택.
   - **Listen Port**: `11112`.
   - Strategy 선택 (예: `random_status`, `delay`).
   - **Start** 클릭.

2. **Tester 설정 (Client 역할)**
   - **SCU Mode** 선택.
   - **Target IP**: `127.0.0.1`
   - **Target Port**: `11112` (Fuzzer의 포트와 일치해야 함).
   - **Send C-ECHO** 클릭.

3. **검증 (Verify)**
   - **Tester의 Log**를 확인합니다.
   - Fuzzer가 지연(delay) 전략을 사용 중이라면 응답 전 일시 중지가 보일 것입니다.
   - Fuzzer가 무작위 상태(random status) 전략을 사용 중이라면 로그에 성공(`0x0000`) 외의 다른 Status 코드가 찍힐 것입니다.

## 4. 문제 해결 (Troubleshooting)
- **Address in Use**: 서버를 시작할 수 없다면 해당 포트가 이미 사용 중인지 확인하세요.
- **Connection Refused**: Target IP/Port가 정확히 일치하는지 확인하세요.
