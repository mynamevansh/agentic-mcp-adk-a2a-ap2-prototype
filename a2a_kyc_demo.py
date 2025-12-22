"""
Agent-to-Agent (A2A) KYC Verification Prototype
================================================

Demonstrates:
- One-time KYC verification
- Reusable verification credentials
- Agent-mediated trust via A2A communication
- Transaction state changes BEFORE and AFTER verification

Architecture:
- InvestorAgent: Represents the investor
- KycAgent: Trusted identity verification service
- CompanyAgent: Investment platform requiring KYC
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# A2A MESSAGE PROTOCOL
# ============================================================================

class MessageType(Enum):
    """A2A message types for agent communication"""
    KYC_SUBMISSION = "kyc_submission"
    KYC_VERIFICATION_RESPONSE = "kyc_verification_response"
    VERIFICATION_REQUEST = "verification_request"
    VERIFICATION_RESPONSE = "verification_response"
    INVESTMENT_REQUEST = "investment_request"
    INVESTMENT_RESPONSE = "investment_response"


@dataclass
class A2AMessage:
    """Structured A2A message format"""
    message_id: str
    message_type: MessageType
    sender_agent: str
    recipient_agent: str
    timestamp: str
    payload: Dict[str, Any]
    
    def to_dict(self):
        return {
            **asdict(self),
            'message_type': self.message_type.value
        }


# ============================================================================
# STATE OBJECTS
# ============================================================================

class KycStatus(Enum):
    """KYC verification status"""
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class TransactionStatus(Enum):
    """Investment transaction status"""
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InvestorState:
    """Investor state tracking"""
    investor_id: str
    name: str
    kyc_status: KycStatus
    verification_id: Optional[str] = None


@dataclass
class TransactionState:
    """Transaction state tracking"""
    transaction_id: str
    investor_id: str
    company_id: str
    amount: float
    status: TransactionStatus
    reason: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


# ============================================================================
# AGENT 1: INVESTOR AGENT
# ============================================================================

class InvestorAgent:
    """
    Represents the investor
    - Holds investor consent
    - Initiates investments
    - Performs one-time KYC submission
    """
    
    def __init__(self, investor_id: str, name: str):
        self.agent_id = f"InvestorAgent-{investor_id}"
        self.state = InvestorState(
            investor_id=investor_id,
            name=name,
            kyc_status=KycStatus.NOT_VERIFIED
        )
        print(f"\n[{self.agent_id}] Initialized")
        print(f"  Investor: {name}")
        print(f"  KYC Status: {self.state.kyc_status.value}")
    
    def submit_kyc(self, kyc_agent: 'KycAgent', identity_data: Dict[str, str]) -> A2AMessage:
        """
        Submit KYC verification ONCE to KycAgent
        This is the ONLY time identity data is shared
        """
        print(f"\n[{self.agent_id}] Submitting KYC to KycAgent...")
        print(f"  Identity Data: {json.dumps(identity_data, indent=2)}")
        
        self.state.kyc_status = KycStatus.PENDING
        
        # Create A2A message for KYC submission
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.KYC_SUBMISSION,
            sender_agent=self.agent_id,
            recipient_agent=kyc_agent.agent_id,
            timestamp=datetime.now().isoformat(),
            payload={
                "investor_id": self.state.investor_id,
                "identity_data": identity_data
            }
        )
        
        # Send via A2A communication
        response = kyc_agent.receive_message(message)
        
        # Update state based on response
        if response.payload.get("verification_status") == "verified":
            self.state.kyc_status = KycStatus.VERIFIED
            self.state.verification_id = response.payload.get("verification_id")
            print(f"\n[{self.agent_id}] [SUCCESS] KYC Verified!")
            print(f"  Verification ID: {self.state.verification_id}")
        else:
            self.state.kyc_status = KycStatus.REJECTED
            print(f"\n[{self.agent_id}] [FAILED] KYC Rejected")
        
        return response
    
    def request_investment(self, company_agent: 'CompanyAgent', amount: float) -> A2AMessage:
        """
        Request investment in a company
        CompanyAgent will handle KYC verification check
        """
        print(f"\n[{self.agent_id}] Requesting investment...")
        print(f"  Company: {company_agent.company_name}")
        print(f"  Amount: ${amount:,.2f}")
        print(f"  Current KYC Status: {self.state.kyc_status.value}")
        
        # Create A2A investment request message
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.INVESTMENT_REQUEST,
            sender_agent=self.agent_id,
            recipient_agent=company_agent.agent_id,
            timestamp=datetime.now().isoformat(),
            payload={
                "investor_id": self.state.investor_id,
                "amount": amount,
                "verification_id": self.state.verification_id  # Share verification ID, not raw data
            }
        )
        
        # Send via A2A communication
        response = company_agent.receive_message(message)
        
        return response


# ============================================================================
# AGENT 2: KYC AGENT (Trusted Identity Agent)
# ============================================================================

class KycAgent:
    """
    Trusted identity verification agent
    - Performs and stores KYC verification
    - Issues reusable verification credentials
    - Responds to verification requests from companies
    """
    
    def __init__(self):
        self.agent_id = "KycAgent-TrustedIdentity"
        self.verification_store: Dict[str, Dict[str, Any]] = {}  # verification_id -> verification_data
        self.investor_verifications: Dict[str, str] = {}  # investor_id -> verification_id
        print(f"\n[{self.agent_id}] Initialized")
        print("  Role: Trusted Identity Verification Service")
    
    def receive_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming A2A messages"""
        print(f"\n[{self.agent_id}] Received message: {message.message_type.value}")
        
        if message.message_type == MessageType.KYC_SUBMISSION:
            return self._handle_kyc_submission(message)
        elif message.message_type == MessageType.VERIFICATION_REQUEST:
            return self._handle_verification_request(message)
        else:
            raise ValueError(f"Unknown message type: {message.message_type}")
    
    def _handle_kyc_submission(self, message: A2AMessage) -> A2AMessage:
        """
        Process KYC submission from investor
        This is where identity verification happens ONCE
        """
        investor_id = message.payload["investor_id"]
        identity_data = message.payload["identity_data"]
        
        print(f"\n[{self.agent_id}] Processing KYC verification...")
        print(f"  Investor ID: {investor_id}")
        
        # Mock KYC verification logic
        # In production: verify documents, check sanctions lists, etc.
        is_valid = self._verify_identity(identity_data)
        
        if is_valid:
            # Generate unique verification ID
            verification_id = f"KYC-{hashlib.sha256(investor_id.encode()).hexdigest()[:12].upper()}"
            
            # Store verification (hashed identity data, not raw)
            self.verification_store[verification_id] = {
                "investor_id": investor_id,
                "verified_at": datetime.now().isoformat(),
                "identity_hash": hashlib.sha256(json.dumps(identity_data).encode()).hexdigest(),
                "status": "verified"
            }
            
            self.investor_verifications[investor_id] = verification_id
            
            print(f"\n[{self.agent_id}] [SUCCESS] Identity Verified!")
            print(f"  Verification ID: {verification_id}")
            print(f"  Stored in secure verification registry")
            
            # Return verification response
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.KYC_VERIFICATION_RESPONSE,
                sender_agent=self.agent_id,
                recipient_agent=message.sender_agent,
                timestamp=datetime.now().isoformat(),
                payload={
                    "verification_status": "verified",
                    "verification_id": verification_id,
                    "verified_at": self.verification_store[verification_id]["verified_at"]
                }
            )
        else:
            print(f"\n[{self.agent_id}] [FAILED] Identity Verification Failed")
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.KYC_VERIFICATION_RESPONSE,
                sender_agent=self.agent_id,
                recipient_agent=message.sender_agent,
                timestamp=datetime.now().isoformat(),
                payload={
                    "verification_status": "rejected",
                    "reason": "Identity verification failed"
                }
            )
    
    def _handle_verification_request(self, message: A2AMessage) -> A2AMessage:
        """
        Handle verification request from CompanyAgent
        This is A2A communication - company asks KycAgent, not investor
        """
        verification_id = message.payload.get("verification_id")
        investor_id = message.payload.get("investor_id")
        
        print(f"\n[{self.agent_id}] Verification request from {message.sender_agent}")
        print(f"  Investor ID: {investor_id}")
        print(f"  Verification ID: {verification_id}")
        
        # Check if verification exists and is valid
        if verification_id and verification_id in self.verification_store:
            verification = self.verification_store[verification_id]
            
            if verification["investor_id"] == investor_id and verification["status"] == "verified":
                print(f"\n[{self.agent_id}] [SUCCESS] Verification Confirmed!")
                print(f"  Verified at: {verification['verified_at']}")
                
                return A2AMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=MessageType.VERIFICATION_RESPONSE,
                    sender_agent=self.agent_id,
                    recipient_agent=message.sender_agent,
                    timestamp=datetime.now().isoformat(),
                    payload={
                        "verification_status": "confirmed",
                        "investor_id": investor_id,
                        "verified_at": verification["verified_at"]
                    }
                )
        
        print(f"\n[{self.agent_id}] [FAILED] Verification Not Found or Invalid")
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION_RESPONSE,
            sender_agent=self.agent_id,
            recipient_agent=message.sender_agent,
            timestamp=datetime.now().isoformat(),
            payload={
                "verification_status": "not_verified",
                "investor_id": investor_id
            }
        )
    
    def _verify_identity(self, identity_data: Dict[str, str]) -> bool:
        """
        Mock identity verification logic
        In production: verify documents, check databases, etc.
        """
        required_fields = ["name", "date_of_birth", "national_id", "address"]
        return all(field in identity_data for field in required_fields)


# ============================================================================
# AGENT 3: COMPANY AGENT
# ============================================================================

class CompanyAgent:
    """
    Represents an investment platform
    - Requires KYC before processing investment
    - Requests verification from KycAgent (NOT from investor)
    """
    
    def __init__(self, company_id: str, company_name: str, kyc_agent: KycAgent):
        self.agent_id = f"CompanyAgent-{company_id}"
        self.company_id = company_id
        self.company_name = company_name
        self.kyc_agent = kyc_agent
        self.transactions: Dict[str, TransactionState] = {}
        print(f"\n[{self.agent_id}] Initialized")
        print(f"  Company: {company_name}")
        print(f"  KYC Requirement: MANDATORY")
    
    def receive_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming A2A messages"""
        print(f"\n[{self.agent_id}] Received message: {message.message_type.value}")
        
        if message.message_type == MessageType.INVESTMENT_REQUEST:
            return self._handle_investment_request(message)
        else:
            raise ValueError(f"Unknown message type: {message.message_type}")
    
    def _handle_investment_request(self, message: A2AMessage) -> A2AMessage:
        """
        Process investment request
        REQUIRES KYC verification via A2A communication with KycAgent
        """
        investor_id = message.payload["investor_id"]
        amount = message.payload["amount"]
        verification_id = message.payload.get("verification_id")
        
        # Create transaction
        transaction = TransactionState(
            transaction_id=str(uuid.uuid4()),
            investor_id=investor_id,
            company_id=self.company_id,
            amount=amount,
            status=TransactionStatus.PENDING_VERIFICATION
        )
        
        self.transactions[transaction.transaction_id] = transaction
        
        print(f"\n[{self.agent_id}] Processing investment request...")
        print(f"  Transaction ID: {transaction.transaction_id}")
        print(f"  Investor: {investor_id}")
        print(f"  Amount: ${amount:,.2f}")
        
        # Check if verification ID is provided
        if not verification_id:
            print(f"\n[{self.agent_id}] [BLOCKED] Transaction BLOCKED")
            print(f"  Reason: Investor not KYC verified")
            
            transaction.status = TransactionStatus.BLOCKED
            transaction.reason = "KYC verification required"
            
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.INVESTMENT_RESPONSE,
                sender_agent=self.agent_id,
                recipient_agent=message.sender_agent,
                timestamp=datetime.now().isoformat(),
                payload={
                    "transaction_id": transaction.transaction_id,
                    "status": transaction.status.value,
                    "reason": transaction.reason
                }
            )
        
        # Request verification from KycAgent via A2A
        print(f"\n[{self.agent_id}] Requesting verification from KycAgent...")
        
        verification_request = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION_REQUEST,
            sender_agent=self.agent_id,
            recipient_agent=self.kyc_agent.agent_id,
            timestamp=datetime.now().isoformat(),
            payload={
                "investor_id": investor_id,
                "verification_id": verification_id
            }
        )
        
        # A2A communication with KycAgent
        verification_response = self.kyc_agent.receive_message(verification_request)
        
        # Process verification response
        if verification_response.payload.get("verification_status") == "confirmed":
            print(f"\n[{self.agent_id}] [SUCCESS] Verification Confirmed by KycAgent")
            print(f"  Proceeding with transaction...")
            
            transaction.status = TransactionStatus.COMPLETED
            
            print(f"\n[{self.agent_id}] [APPROVED] Transaction APPROVED")
            print(f"  Transaction ID: {transaction.transaction_id}")
            print(f"  Amount: ${amount:,.2f}")
            
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.INVESTMENT_RESPONSE,
                sender_agent=self.agent_id,
                recipient_agent=message.sender_agent,
                timestamp=datetime.now().isoformat(),
                payload={
                    "transaction_id": transaction.transaction_id,
                    "status": transaction.status.value,
                    "amount": amount,
                    "verified_at": verification_response.payload.get("verified_at")
                }
            )
        else:
            print(f"\n[{self.agent_id}] [FAILED] Verification Failed")
            
            transaction.status = TransactionStatus.BLOCKED
            transaction.reason = "KYC verification not confirmed"
            
            return A2AMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.INVESTMENT_RESPONSE,
                sender_agent=self.agent_id,
                recipient_agent=message.sender_agent,
                timestamp=datetime.now().isoformat(),
                payload={
                    "transaction_id": transaction.transaction_id,
                    "status": transaction.status.value,
                    "reason": transaction.reason
                }
            )


# ============================================================================
# DEMONSTRATION FLOW
# ============================================================================

def main():
    """
    Demonstrate A2A KYC verification flow
    Shows transaction behavior BEFORE and AFTER KYC
    """
    
    print("=" * 80)
    print("AGENT-TO-AGENT (A2A) KYC VERIFICATION PROTOTYPE")
    print("=" * 80)
    print("\nScenario: Investor wants to invest in multiple companies")
    print("Requirement: KYC verification done ONCE, reused across transactions")
    print("=" * 80)
    
    # Initialize agents
    print("\n" + "=" * 80)
    print("PHASE 1: AGENT INITIALIZATION")
    print("=" * 80)
    
    kyc_agent = KycAgent()
    
    investor = InvestorAgent(
        investor_id="INV-001",
        name="Alice Johnson"
    )
    
    company_a = CompanyAgent(
        company_id="COMP-A",
        company_name="TechVentures Inc.",
        kyc_agent=kyc_agent
    )
    
    company_b = CompanyAgent(
        company_id="COMP-B",
        company_name="GreenEnergy Corp.",
        kyc_agent=kyc_agent
    )
    
    # BEFORE KYC: Try to invest (should be blocked)
    print("\n" + "=" * 80)
    print("PHASE 2: BEFORE KYC - Transaction Attempt")
    print("=" * 80)
    print("\n[WARNING] Investor has NOT completed KYC verification yet")
    
    response_before = investor.request_investment(company_a, 50000.00)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {response_before.payload['status']}")
    print(f"  Reason: {response_before.payload.get('reason', 'N/A')}")
    print("-" * 80)
    
    # KYC PROCESS: Submit KYC once
    print("\n" + "=" * 80)
    print("PHASE 3: KYC VERIFICATION PROCESS")
    print("=" * 80)
    print("\n[INFO] Investor submits identity data to KycAgent (ONE TIME ONLY)")
    
    identity_data = {
        "name": "Alice Johnson",
        "date_of_birth": "1990-05-15",
        "national_id": "US-123456789",
        "address": "123 Main St, San Francisco, CA 94102",
        "email": "alice.johnson@email.com"
    }
    
    kyc_response = investor.submit_kyc(kyc_agent, identity_data)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {kyc_response.payload['verification_status']}")
    print(f"  Verification ID: {kyc_response.payload.get('verification_id', 'N/A')}")
    print("-" * 80)
    
    # AFTER KYC: Try to invest again (should succeed)
    print("\n" + "=" * 80)
    print("PHASE 4: AFTER KYC - Transaction Attempt #1")
    print("=" * 80)
    print("\n[SUCCESS] Investor is now KYC verified")
    print("[INFO] Attempting investment in Company A...")
    
    response_after_a = investor.request_investment(company_a, 50000.00)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {response_after_a.payload['status']}")
    print(f"  Transaction ID: {response_after_a.payload.get('transaction_id', 'N/A')}")
    print(f"  Amount: ${response_after_a.payload.get('amount', 0):,.2f}")
    print("-" * 80)
    
    # REUSABLE VERIFICATION: Invest in another company
    print("\n" + "=" * 80)
    print("PHASE 5: REUSABLE VERIFICATION - Transaction Attempt #2")
    print("=" * 80)
    print("\n[INFO] Attempting investment in Company B...")
    print("[INFO] Using SAME verification ID (no re-verification needed)")
    
    response_after_b = investor.request_investment(company_b, 75000.00)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {response_after_b.payload['status']}")
    print(f"  Transaction ID: {response_after_b.payload.get('transaction_id', 'N/A')}")
    print(f"  Amount: ${response_after_b.payload.get('amount', 0):,.2f}")
    print("-" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION SUMMARY")
    print("=" * 80)
    print("\n[SUCCESS] Key Achievements:")
    print("  1. KYC verification performed ONCE")
    print("  2. Verification credential reused across multiple companies")
    print("  3. Agent-to-agent communication for verification requests")
    print("  4. Clear transaction state changes BEFORE and AFTER KYC")
    print("  5. No repeated identity document sharing")
    print("\n[INFO] Transaction Flow:")
    print("  BEFORE KYC: Transaction BLOCKED")
    print("  KYC PROCESS: Identity verified, credential issued")
    print("  AFTER KYC: Transactions APPROVED automatically")
    print("  REUSE: Same credential works for multiple companies")
    print("\n[SECURITY] Security Model:")
    print("  - Investor shares identity data ONLY with KycAgent")
    print("  - Companies request verification via A2A (not from investor)")
    print("  - KycAgent acts as trusted verification authority")
    print("  - Verification ID used instead of raw identity data")
    print("=" * 80)


if __name__ == "__main__":
    main()
