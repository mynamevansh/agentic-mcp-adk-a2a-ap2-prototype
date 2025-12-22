"""
AP2 (Agentic Payment Protocol) Mock Implementation

This is a protocol-aligned mock of AP2 that simulates:
1. Payment Intent Creation
2. Authorization Flow
3. Payment Confirmation

In production, this would integrate with:
- Blockchain networks (Ethereum, Polygon, etc.)
- Traditional payment gateways (Stripe, PayPal)
- Banking APIs with proper security and compliance
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PaymentStatus(Enum):
    """Payment lifecycle states"""
    INTENT_CREATED = "intent_created"
    PENDING_AUTHORIZATION = "pending_authorization"
    AUTHORIZED = "authorized"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PaymentIntent:
    """Payment intent data model"""
    payment_id: str
    amount: float
    currency: str
    purpose: str
    status: PaymentStatus
    created_at: str
    metadata: Dict[str, Any]


@dataclass
class PaymentAuthorization:
    """Payment authorization data"""
    auth_id: str
    payment_id: str
    authorized_by: str
    authorized_at: str
    auth_method: str
    risk_score: float


@dataclass
class PaymentReceipt:
    """Payment completion receipt"""
    receipt_id: str
    payment_id: str
    transaction_id: str
    amount: float
    currency: str
    status: str
    completed_at: str
    confirmation_code: str


class AP2PaymentMock:
    """
    Mock implementation of AP2 (Agentic Payment Protocol)
    
    Simulates a secure payment flow for autonomous agents:
    1. Create payment intent
    2. Request authorization (simulated user/agent approval)
    3. Process payment
    4. Return receipt
    
    Production Implementation Notes:
    - Use secure key management (HSM, KMS)
    - Implement proper authentication and authorization
    - Add fraud detection and risk scoring
    - Support multiple payment methods and currencies
    - Implement idempotency for retry safety
    - Add comprehensive audit logging
    - Support webhooks for async notifications
    """
    
    def __init__(self):
        self.payment_intents: Dict[str, PaymentIntent] = {}
        self.authorizations: Dict[str, PaymentAuthorization] = {}
        self.receipts: Dict[str, PaymentReceipt] = {}
        print("[AP2 Mock] Payment protocol initialized")
    
    def create_payment_intent(
        self,
        amount: float,
        purpose: str,
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 1: Create a payment intent
        
        Args:
            amount: Payment amount
            purpose: Payment description/purpose
            currency: Currency code (default: USD)
            metadata: Additional payment context
            
        Returns:
            Payment intent details
        """
        payment_id = "PAY-" + str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        intent = PaymentIntent(
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            purpose=purpose,
            status=PaymentStatus.INTENT_CREATED,
            created_at=now,
            metadata=metadata or {}
        )
        
        self.payment_intents[payment_id] = intent
        
        print(f"[AP2 Mock] 💳 Payment intent created: {payment_id}")
        print(f"           Amount: ${amount:.2f} {currency}")
        print(f"           Purpose: {purpose}")
        
        return {
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "purpose": purpose,
            "status": PaymentStatus.INTENT_CREATED.value,
            "created_at": now,
            "next_step": "authorize_payment"
        }
    
    def authorize_payment(
        self,
        payment_id: str,
        authorized_by: str = "agent_nav",
        auth_method: str = "agent_signature"
    ) -> Dict[str, Any]:
        """
        Step 2: Authorize the payment
        
        In production, this would:
        - Verify agent credentials
        - Check spending limits
        - Perform risk assessment
        - Request user confirmation if needed
        - Validate against fraud rules
        
        Args:
            payment_id: Payment intent ID
            authorized_by: Entity authorizing the payment
            auth_method: Authorization method used
            
        Returns:
            Authorization result
        """
        if payment_id not in self.payment_intents:
            return {
                "success": False,
                "error": f"Payment intent not found: {payment_id}"
            }
        
        intent = self.payment_intents[payment_id]
        
        # Simulate risk scoring
        risk_score = self._calculate_risk_score(intent)
        
        if risk_score > 0.8:
            print(f"[AP2 Mock] ⚠️  High risk payment detected (score: {risk_score:.2f})")
            intent.status = PaymentStatus.FAILED
            return {
                "success": False,
                "payment_id": payment_id,
                "error": "Payment blocked due to high risk score",
                "risk_score": risk_score
            }
        
        auth_id = "AUTH-" + str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        authorization = PaymentAuthorization(
            auth_id=auth_id,
            payment_id=payment_id,
            authorized_by=authorized_by,
            authorized_at=now,
            auth_method=auth_method,
            risk_score=risk_score
        )
        
        self.authorizations[auth_id] = authorization
        intent.status = PaymentStatus.AUTHORIZED
        
        print(f"[AP2 Mock] ✓ Payment authorized: {payment_id}")
        print(f"           Auth ID: {auth_id}")
        print(f"           Risk Score: {risk_score:.2f}")
        print(f"           Authorized by: {authorized_by}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "auth_id": auth_id,
            "authorized_at": now,
            "risk_score": risk_score,
            "status": PaymentStatus.AUTHORIZED.value,
            "next_step": "confirm_payment"
        }
    
    def confirm_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Step 3: Confirm and complete the payment
        
        In production, this would:
        - Execute the actual payment transaction
        - Update ledgers/blockchain
        - Send confirmation to all parties
        - Trigger webhooks
        - Generate compliance records
        
        Args:
            payment_id: Payment intent ID
            
        Returns:
            Payment receipt
        """
        if payment_id not in self.payment_intents:
            return {
                "success": False,
                "error": f"Payment intent not found: {payment_id}"
            }
        
        intent = self.payment_intents[payment_id]
        
        if intent.status != PaymentStatus.AUTHORIZED:
            return {
                "success": False,
                "payment_id": payment_id,
                "error": f"Payment not authorized. Current status: {intent.status.value}"
            }
        
        # Simulate payment processing
        intent.status = PaymentStatus.PROCESSING
        print(f"[AP2 Mock] ⏳ Processing payment: {payment_id}")
        
        # Create receipt
        receipt_id = "RCP-" + str(uuid.uuid4())
        transaction_id = "TXN-" + str(uuid.uuid4())
        confirmation_code = str(uuid.uuid4())[:8].upper()
        now = datetime.utcnow().isoformat()
        
        receipt = PaymentReceipt(
            receipt_id=receipt_id,
            payment_id=payment_id,
            transaction_id=transaction_id,
            amount=intent.amount,
            currency=intent.currency,
            status="completed",
            completed_at=now,
            confirmation_code=confirmation_code
        )
        
        self.receipts[receipt_id] = receipt
        intent.status = PaymentStatus.COMPLETED
        
        print(f"[AP2 Mock] ✓ Payment completed: {payment_id}")
        print(f"           Transaction ID: {transaction_id}")
        print(f"           Confirmation: {confirmation_code}")
        print(f"           Amount: ${intent.amount:.2f} {intent.currency}")
        
        return {
            "success": True,
            "receipt_id": receipt_id,
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": "completed",
            "completed_at": now,
            "confirmation_code": confirmation_code,
            "purpose": intent.purpose
        }
    
    def _calculate_risk_score(self, intent: PaymentIntent) -> float:
        """
        Simulate risk scoring
        
        Production implementation would consider:
        - Transaction amount and velocity
        - Agent reputation score
        - Historical behavior patterns
        - Merchant/recipient verification
        - Geographic and temporal anomalies
        """
        # Simple mock: higher amounts = slightly higher risk
        base_risk = 0.1
        amount_risk = min(intent.amount / 1000.0, 0.3)
        return base_risk + amount_risk
    
    def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get current payment status"""
        if payment_id not in self.payment_intents:
            return None
        
        intent = self.payment_intents[payment_id]
        return {
            "payment_id": payment_id,
            "amount": intent.amount,
            "currency": intent.currency,
            "purpose": intent.purpose,
            "status": intent.status.value,
            "created_at": intent.created_at
        }


# Singleton instance
_ap2_instance = None

def get_ap2_instance() -> AP2PaymentMock:
    """Get or create AP2 instance"""
    global _ap2_instance
    if _ap2_instance is None:
        _ap2_instance = AP2PaymentMock()
    return _ap2_instance


if __name__ == "__main__":
    # Test AP2 payment flow
    ap2 = get_ap2_instance()
    
    print("\n=== AP2 Payment Flow Test ===\n")
    
    # Step 1: Create intent
    intent = ap2.create_payment_intent(
        amount=50.0,
        purpose="Premium workspace booking",
        metadata={"workspace_id": "WS-123", "duration_hours": 2}
    )
    print(f"\n1. Intent: {intent}\n")
    
    # Step 2: Authorize
    auth = ap2.authorize_payment(
        payment_id=intent["payment_id"],
        authorized_by="agent_nav"
    )
    print(f"\n2. Authorization: {auth}\n")
    
    # Step 3: Confirm
    receipt = ap2.confirm_payment(intent["payment_id"])
    print(f"\n3. Receipt: {receipt}\n")
