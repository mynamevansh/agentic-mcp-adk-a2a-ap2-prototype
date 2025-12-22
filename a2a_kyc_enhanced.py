"""
Enhanced A2A KYC Verification with Verification State View
===========================================================

NEW CONCEPT: Verification State View
- Agents observe verification STATE (not raw identity data)
- Only KycAgent owns and updates verification state
- CompanyAgents request state via A2A (never see identity data)
- Clear BEFORE vs AFTER state visibility per agent

Demonstrates:
- One-time KYC verification
- State-based authorization
- Privacy-preserving verification
- Reusable credentials across companies
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum


# ============================================================================
# VERIFICATION STATE SYSTEM
# ============================================================================

class KycStatus(Enum):
    """KYC verification status"""
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Permission(Enum):
    """Permissions granted based on verification state"""
    NONE = "none"
    INVEST = "invest"
    TRADE = "trade"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    BORROW = "borrow"


@dataclass
class VerificationState:
    """
    Verification state object - OWNED BY KycAgent ONLY
    
    This is what other agents see (NOT raw identity data)
    """
    investor_id: str
    kyc_status: KycStatus
    verification_id: Optional[str] = None
    verified_at: Optional[str] = None
    permissions: List[Permission] = field(default_factory=list)
    risk_level: str = "medium"  # low, medium, high
    compliance_flags: List[str] = field(default_factory=list)  # e.g., ["accredited_investor", "institutional"]
    
    def to_dict(self):
        return {
            'investor_id': self.investor_id,
            'kyc_status': self.kyc_status.value,
            'verification_id': self.verification_id,
            'verified_at': self.verified_at,
            'permissions': [p.value for p in self.permissions],
            'risk_level': self.risk_level,
            'compliance_flags': self.compliance_flags
        }
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if investor has specific permission"""
        return permission in self.permissions


# ============================================================================
# A2A MESSAGE PROTOCOL
# ============================================================================

class MessageType(Enum):
    """A2A message types for agent communication"""
    KYC_SUBMISSION = "kyc_submission"
    KYC_VERIFICATION_RESPONSE = "kyc_verification_response"
    VERIFICATION_STATE_REQUEST = "verification_state_request"
    VERIFICATION_STATE_RESPONSE = "verification_state_response"
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
# TRANSACTION STATE
# ============================================================================

class TransactionStatus(Enum):
    """Investment transaction status"""
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    COMPLETED = "completed"
    FAILED = "failed"


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
# INVESTOR STATE
# ============================================================================

@dataclass
class InvestorState:
    """Investor state tracking"""
    investor_id: str
    name: str
    kyc_status: KycStatus
    verification_id: Optional[str] = None


# ============================================================================
# AGENT 1: INVESTOR AGENT
# ============================================================================

class InvestorAgent:
    """
    Represents the investor
    - Submits identity data ONE TIME only
    - Sees own KYC status
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
        CompanyAgent will check verification state via KycAgent
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
                "verification_id": self.state.verification_id
            }
        )
        
        # Send via A2A communication
        response = company_agent.receive_message(message)
        
        return response


# ============================================================================
# AGENT 2: KYC AGENT (Trusted Authority)
# ============================================================================

class KycAgent:
    """
    Trusted identity verification agent
    - Performs and stores KYC verification
    - Owns and updates VerificationState
    - Exposes ONLY verification state (not identity data)
    """
    
    def __init__(self):
        self.agent_id = "KycAgent-TrustedAuthority"
        # Private storage - never exposed directly
        self._identity_store: Dict[str, Dict[str, Any]] = {}  # investor_id -> identity_data (hashed)
        # Public verification states - this is what other agents see
        self._verification_states: Dict[str, VerificationState] = {}  # investor_id -> VerificationState
        
        print(f"\n[{self.agent_id}] Initialized")
        print("  Role: Trusted Identity Verification Authority")
        print("  Manages: Verification States (NOT raw identity data)")
    
    def receive_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming A2A messages"""
        print(f"\n[{self.agent_id}] Received message: {message.message_type.value}")
        
        if message.message_type == MessageType.KYC_SUBMISSION:
            return self._handle_kyc_submission(message)
        elif message.message_type == MessageType.VERIFICATION_STATE_REQUEST:
            return self._handle_verification_state_request(message)
        else:
            raise ValueError(f"Unknown message type: {message.message_type}")
    
    def _handle_kyc_submission(self, message: A2AMessage) -> A2AMessage:
        """
        Process KYC submission from investor
        Creates/updates VerificationState
        """
        investor_id = message.payload["investor_id"]
        identity_data = message.payload["identity_data"]
        
        print(f"\n[{self.agent_id}] Processing KYC verification...")
        print(f"  Investor ID: {investor_id}")
        
        # Mock KYC verification logic
        is_valid = self._verify_identity(identity_data)
        
        if is_valid:
            # Generate unique verification ID
            verification_id = f"KYC-{hashlib.sha256(investor_id.encode()).hexdigest()[:12].upper()}"
            verified_at = datetime.now().isoformat()
            
            # Store identity data privately (hashed)
            self._identity_store[investor_id] = {
                "identity_hash": hashlib.sha256(json.dumps(identity_data).encode()).hexdigest(),
                "verified_at": verified_at
            }
            
            # Create VerificationState (this is what other agents see)
            self._verification_states[investor_id] = VerificationState(
                investor_id=investor_id,
                kyc_status=KycStatus.VERIFIED,
                verification_id=verification_id,
                verified_at=verified_at,
                permissions=[Permission.INVEST, Permission.TRADE, Permission.WITHDRAW, Permission.TRANSFER],  # Grant permissions
                risk_level="low",  # Based on verification
                compliance_flags=["accredited_investor", "aml_cleared"]
            )
            
            print(f"\n[{self.agent_id}] [SUCCESS] Identity Verified!")
            print(f"  Verification ID: {verification_id}")
            print(f"\n[{self.agent_id}] VerificationState Created:")
            print(f"  KYC Status: {KycStatus.VERIFIED.value}")
            print(f"  Permissions: {[p.value for p in self._verification_states[investor_id].permissions]}")
            print(f"  Risk Level: {self._verification_states[investor_id].risk_level}")
            print(f"  Compliance Flags: {self._verification_states[investor_id].compliance_flags}")
            print(f"  [PRIVACY] Identity data stored securely (hashed)")
            
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
                    "verified_at": verified_at
                }
            )
        else:
            # Create NOT_VERIFIED state
            self._verification_states[investor_id] = VerificationState(
                investor_id=investor_id,
                kyc_status=KycStatus.REJECTED,
                permissions=[]
            )
            
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
    
    def _handle_verification_state_request(self, message: A2AMessage) -> A2AMessage:
        """
        Handle verification state request from CompanyAgent
        Returns VerificationState (NOT identity data)
        """
        investor_id = message.payload.get("investor_id")
        
        print(f"\n[{self.agent_id}] Verification state request from {message.sender_agent}")
        print(f"  Investor ID: {investor_id}")
        
        # Get verification state (or create NOT_VERIFIED state if doesn't exist)
        if investor_id in self._verification_states:
            state = self._verification_states[investor_id]
        else:
            # Create default NOT_VERIFIED state
            state = VerificationState(
                investor_id=investor_id,
                kyc_status=KycStatus.NOT_VERIFIED,
                permissions=[]
            )
        
        print(f"\n[{self.agent_id}] Returning VerificationState:")
        print(f"  KYC Status: {state.kyc_status.value}")
        print(f"  Verification ID: {state.verification_id or 'NONE'}")
        print(f"  Permissions: {[p.value for p in state.permissions]}")
        print(f"  [PRIVACY] Identity data NOT included in response")
        
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION_STATE_RESPONSE,
            sender_agent=self.agent_id,
            recipient_agent=message.sender_agent,
            timestamp=datetime.now().isoformat(),
            payload={
                "verification_state": state.to_dict()
            }
        )
    
    def _verify_identity(self, identity_data: Dict[str, str]) -> bool:
        """Mock identity verification logic"""
        required_fields = ["name", "date_of_birth", "national_id", "address"]
        return all(field in identity_data for field in required_fields)


# ============================================================================
# AGENT 3: COMPANY AGENT
# ============================================================================

class CompanyAgent:
    """
    Represents an investment platform
    - Requires KYC before processing investment
    - Requests VerificationState from KycAgent (NOT identity data)
    - Makes decisions based on state
    """
    
    def __init__(self, company_id: str, company_name: str, kyc_agent: KycAgent):
        self.agent_id = f"CompanyAgent-{company_id}"
        self.company_id = company_id
        self.company_name = company_name
        self.kyc_agent = kyc_agent
        self.transactions: Dict[str, TransactionState] = {}
        print(f"\n[{self.agent_id}] Initialized")
        print(f"  Company: {company_name}")
        print(f"  KYC Requirement: MANDATORY (state-based)")
    
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
        REQUIRES verification state check via A2A with KycAgent
        """
        investor_id = message.payload["investor_id"]
        amount = message.payload["amount"]
        
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
        
        # Request VerificationState from KycAgent via A2A
        print(f"\n[{self.agent_id}] Requesting verification state from KycAgent...")
        
        state_request = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.VERIFICATION_STATE_REQUEST,
            sender_agent=self.agent_id,
            recipient_agent=self.kyc_agent.agent_id,
            timestamp=datetime.now().isoformat(),
            payload={
                "investor_id": investor_id
            }
        )
        
        # A2A communication with KycAgent
        state_response = self.kyc_agent.receive_message(state_request)
        verification_state_dict = state_response.payload.get("verification_state")
        
        # Display verification state view
        print(f"\n{'='*60}")
        print(f"[{self.agent_id}] Investor Verification State:")
        print(f"{'='*60}")
        print(f"  KYC Status: {verification_state_dict['kyc_status'].upper()}")
        print(f"  Verification ID: {verification_state_dict['verification_id'] or 'NONE'}")
        print(f"  Permissions: {', '.join(verification_state_dict['permissions']) if verification_state_dict['permissions'] else 'NONE'}")
        print(f"  Risk Level: {verification_state_dict.get('risk_level', 'N/A').upper()}")
        print(f"  Compliance: {', '.join(verification_state_dict.get('compliance_flags', [])) if verification_state_dict.get('compliance_flags') else 'NONE'}")
        
        # Make decision based on state
        kyc_status = verification_state_dict['kyc_status']
        permissions = verification_state_dict['permissions']
        
        if kyc_status == KycStatus.VERIFIED.value and 'invest' in permissions:
            print(f"  Allowed Action: [APPROVED] Transaction allowed")
            print(f"{'='*60}")
            
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
                    "amount": amount
                }
            )
        else:
            print(f"  Allowed Action: [BLOCKED] Transaction blocked")
            print(f"{'='*60}")
            
            transaction.status = TransactionStatus.BLOCKED
            transaction.reason = "KYC verification required or insufficient permissions"
            
            print(f"\n[{self.agent_id}] [BLOCKED] Transaction BLOCKED")
            print(f"  Reason: {transaction.reason}")
            
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
    Demonstrate A2A KYC with Verification State View
    Shows clear BEFORE vs AFTER state visibility per agent
    """
    
    print("=" * 80)
    print("ENHANCED A2A KYC WITH VERIFICATION STATE VIEW")
    print("=" * 80)
    print("\nNEW CONCEPT: Verification State View")
    print("- Agents observe verification STATE (not raw identity data)")
    print("- Only KycAgent owns and updates verification state")
    print("- CompanyAgents request state via A2A")
    print("=" * 80)
    
    # Initialize agents
    print("\n" + "=" * 80)
    print("PHASE 1: AGENT INITIALIZATION")
    print("=" * 80)
    
    kyc_agent = KycAgent()
    
    investor = InvestorAgent(
        investor_id="INV-001",
        name="Vansh Ranawat"
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
    
    # BEFORE KYC: Try to invest (should be blocked with state view)
    print("\n" + "=" * 80)
    print("PHASE 2: BEFORE KYC - Verification State View")
    print("=" * 80)
    print("\n[WARNING] Investor has NOT completed KYC verification yet")
    print("[INFO] CompanyAgent will request verification state from KycAgent")
    
    response_before = investor.request_investment(company_a, 50000.00)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {response_before.payload['status']}")
    print(f"  Reason: {response_before.payload.get('reason', 'N/A')}")
    print("-" * 80)
    
    # KYC PROCESS: Submit KYC once
    print("\n" + "=" * 80)
    print("PHASE 3: KYC VERIFICATION PROCESS (ONE TIME)")
    print("=" * 80)
    print("\n[INFO] Investor submits identity data to KycAgent (ONE TIME ONLY)")
    print("[INFO] KycAgent will create VerificationState")
    
    identity_data = {
        "name": "Vansh Ranawat",
        "date_of_birth": "1990-05-15",
        "national_id": "US-123456789",
        "address": "123 Main St, San Francisco, CA 94102",
        "email": "vansh.ranawat@email.com"
    }
    
    kyc_response = investor.submit_kyc(kyc_agent, identity_data)
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print(f"  Status: {kyc_response.payload['verification_status']}")
    print(f"  Verification ID: {kyc_response.payload.get('verification_id', 'N/A')}")
    print("-" * 80)
    
    # AFTER KYC: Try to invest again (should succeed with state view)
    print("\n" + "=" * 80)
    print("PHASE 4: AFTER KYC - Verification State View")
    print("=" * 80)
    print("\n[SUCCESS] Investor is now KYC verified")
    print("[INFO] CompanyAgent will request updated verification state")
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
    print("PHASE 5: REUSABLE VERIFICATION STATE")
    print("=" * 80)
    print("\n[INFO] Attempting investment in Company B...")
    print("[INFO] Company B will request SAME verification state")
    print("[INFO] No re-verification needed")
    
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
    print("  1. Verification State View implemented")
    print("  2. CompanyAgents see STATE, not identity data")
    print("  3. Clear BEFORE vs AFTER state visibility")
    print("  4. State-based authorization (permissions)")
    print("  5. Reusable verification state across companies")
    print("\n[INFO] State Transition Flow:")
    print("  BEFORE KYC: State = NOT_VERIFIED, Permissions = NONE")
    print("  KYC PROCESS: State updated to VERIFIED, Permissions granted")
    print("  AFTER KYC: State = VERIFIED, Permissions = [INVEST, TRADE]")
    print("  REUSE: Same state accessible to all companies")
    print("\n[PRIVACY] Privacy Model:")
    print("  - Identity data stored ONLY in KycAgent (hashed)")
    print("  - CompanyAgents receive ONLY verification state")
    print("  - No identity fields in CompanyAgent logs")
    print("  - State-based authorization (not document-based)")
    print("=" * 80)


if __name__ == "__main__":
    main()
