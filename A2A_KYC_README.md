# Agent-to-Agent (A2A) KYC Verification Prototype

## Overview

This prototype demonstrates **one-time KYC verification with reusable credentials** across multiple investment transactions using Agent-to-Agent (A2A) communication.

## Problem Statement

An investor wants to invest in multiple companies. Each company requires KYC verification, but the investor should **NOT** be asked to verify their identity repeatedly.

## Solution Architecture

### Three Autonomous Agents

1. **InvestorAgent**
   - Represents the investor
   - Holds investor consent
   - Initiates investments
   - Performs **one-time** KYC submission

2. **KycAgent** (Trusted Identity Agent)
   - Performs and stores KYC verification
   - Issues reusable verification credentials
   - Responds to verification requests from companies
   - Acts as trusted third-party verifier

3. **CompanyAgent**
   - Represents an investment platform
   - Requires KYC before processing investment
   - Requests verification from KycAgent (**NOT** from investor)

### A2A Communication Protocol

All agents communicate via structured A2A messages:

```python
@dataclass
class A2AMessage:
    message_id: str
    message_type: MessageType
    sender_agent: str
    recipient_agent: str
    timestamp: str
    payload: Dict[str, Any]
```

**Message Types:**
- `KYC_SUBMISSION` - Investor → KycAgent
- `KYC_VERIFICATION_RESPONSE` - KycAgent → Investor
- `VERIFICATION_REQUEST` - CompanyAgent → KycAgent
- `VERIFICATION_RESPONSE` - KycAgent → CompanyAgent
- `INVESTMENT_REQUEST` - Investor → CompanyAgent
- `INVESTMENT_RESPONSE` - CompanyAgent → Investor

## Execution Flow

### Phase 1: Agent Initialization
- Initialize KycAgent (trusted identity service)
- Initialize InvestorAgent (Alice Johnson)
- Initialize CompanyAgent A (TechVentures Inc.)
- Initialize CompanyAgent B (GreenEnergy Corp.)

### Phase 2: BEFORE KYC - Transaction Blocked

```
[InvestorAgent] 💰 Requesting investment...
  Company: TechVentures Inc.
  Amount: $50,000.00
  Current KYC Status: not_verified

[CompanyAgent] ❌ Transaction BLOCKED
  Reason: Investor not KYC verified

RESULT:
  Status: blocked
  Reason: KYC verification required
```

### Phase 3: KYC Verification Process (ONE TIME ONLY)

```
[InvestorAgent] 📤 Submitting KYC to KycAgent...
  Identity Data: {
    "name": "Alice Johnson",
    "date_of_birth": "1990-05-15",
    "national_id": "US-123456789",
    "address": "123 Main St, San Francisco, CA 94102",
    "email": "alice.johnson@email.com"
  }

[KycAgent] 🔍 Processing KYC verification...
  Investor ID: INV-001

[KycAgent] ✅ Identity Verified!
  Verification ID: KYC-A1B2C3D4E5F6
  Stored in secure verification registry

[InvestorAgent] ✅ KYC Verified!
  Verification ID: KYC-A1B2C3D4E5F6

RESULT:
  Status: verified
  Verification ID: KYC-A1B2C3D4E5F6
```

### Phase 4: AFTER KYC - Transaction Approved

```
[InvestorAgent] 💰 Requesting investment...
  Company: TechVentures Inc.
  Amount: $50,000.00
  Current KYC Status: verified

[CompanyAgent] 🔍 Requesting verification from KycAgent...

[KycAgent] 🔍 Verification request from CompanyAgent-COMP-A
  Investor ID: INV-001
  Verification ID: KYC-A1B2C3D4E5F6

[KycAgent] ✅ Verification Confirmed!

[CompanyAgent] ✅ Verification Confirmed by KycAgent
  Proceeding with transaction...

[CompanyAgent] ✅ Transaction APPROVED
  Transaction ID: txn-uuid-1234
  Amount: $50,000.00

RESULT:
  Status: completed
  Transaction ID: txn-uuid-1234
  Amount: $50,000.00
```

### Phase 5: Reusable Verification - Second Company

```
[InvestorAgent] 💰 Requesting investment...
  Company: GreenEnergy Corp.
  Amount: $75,000.00
  Current KYC Status: verified

[CompanyAgent] 🔍 Requesting verification from KycAgent...

[KycAgent] ✅ Verification Confirmed!
  (Using SAME verification ID - no re-verification needed)

[CompanyAgent] ✅ Transaction APPROVED
  Transaction ID: txn-uuid-5678
  Amount: $75,000.00

RESULT:
  Status: completed
  Transaction ID: txn-uuid-5678
  Amount: $75,000.00
```

## Key Features

### ✅ One-Time KYC
- Identity data submitted **ONCE** to KycAgent
- Verification credential issued
- No repeated identity document sharing

### ✅ Reusable Verification
- Same verification ID works across multiple companies
- Companies verify via A2A communication with KycAgent
- Investor doesn't need to re-submit documents

### ✅ Agent-Mediated Trust
- KycAgent acts as trusted third party
- Companies trust KycAgent's verification
- Investor's raw identity data never shared with companies

### ✅ Clear State Tracking

**Investor State:**
```python
{
  investor_id: "INV-001",
  kyc_status: "verified",
  verification_id: "KYC-A1B2C3D4E5F6"
}
```

**Transaction State:**
```python
{
  transaction_id: "txn-uuid-1234",
  status: "completed",  # BLOCKED → VERIFIED → COMPLETED
  investor_id: "INV-001",
  company_id: "COMP-A",
  amount: 50000.00
}
```

## Security Model

1. **Privacy**: Investor shares identity data ONLY with KycAgent
2. **Verification**: Companies request verification via A2A (not from investor)
3. **Trust**: KycAgent acts as trusted verification authority
4. **Credentials**: Verification ID used instead of raw identity data
5. **Hashing**: Identity data hashed and stored securely

## Running the Prototype

```bash
# Navigate to project directory
cd "c:\Users\vansh\OneDrive\Desktop\hush prototype"

# Run the demonstration
python a2a_kyc_demo.py
```

## Expected Output Summary

The prototype demonstrates:

1. **BEFORE KYC**: Transaction attempt → **BLOCKED**
2. **KYC PROCESS**: Identity verification → **VERIFIED** (credential issued)
3. **AFTER KYC**: Transaction attempt → **APPROVED** (automatic)
4. **REUSE**: Second company → **APPROVED** (same credential)

## Technical Implementation

### State Objects
- `InvestorState`: Tracks KYC status and verification ID
- `TransactionState`: Tracks transaction lifecycle
- `KycStatus`: Enum for verification states
- `TransactionStatus`: Enum for transaction states

### A2A Message Flow

```
BEFORE KYC:
Investor → Company: INVESTMENT_REQUEST (no verification_id)
Company → Investor: INVESTMENT_RESPONSE (status: blocked)

KYC PROCESS:
Investor → KycAgent: KYC_SUBMISSION (identity_data)
KycAgent → Investor: KYC_VERIFICATION_RESPONSE (verification_id)

AFTER KYC:
Investor → Company: INVESTMENT_REQUEST (with verification_id)
Company → KycAgent: VERIFICATION_REQUEST (verification_id)
KycAgent → Company: VERIFICATION_RESPONSE (status: confirmed)
Company → Investor: INVESTMENT_RESPONSE (status: completed)
```

## Use Case Applicability

This pattern applies to:
- **Financial Services**: Investment platforms, banking, lending
- **Healthcare**: Patient identity verification across providers
- **Government**: Citizen identity for multiple services
- **Enterprise**: Employee verification across departments
- **E-commerce**: Buyer verification across marketplaces

## Advantages

1. **User Experience**: Verify once, use everywhere
2. **Privacy**: Minimal data sharing
3. **Security**: Centralized verification authority
4. **Efficiency**: No repeated verification processes
5. **Scalability**: Add new companies without re-verification
6. **Compliance**: Audit trail via A2A messages

## Architecture Principles

- **Separation of Concerns**: Each agent has clear responsibility
- **Message-Based Communication**: No direct function calls
- **State Management**: Clear state tracking and transitions
- **Trust Model**: Explicit trust relationships
- **Reusability**: Verification credentials are portable

## Future Enhancements

1. **Zero-Knowledge Proofs**: Verify attributes without revealing data
2. **Blockchain Integration**: Immutable verification records
3. **Expiration**: Time-limited verification credentials
4. **Revocation**: Ability to revoke compromised credentials
5. **Multi-Factor**: Additional verification layers
6. **Selective Disclosure**: Share only required attributes

---

**Author**: AI Systems Engineer  
**Purpose**: Demonstrate A2A communication for reusable KYC verification  
**Status**: Prototype / Educational
