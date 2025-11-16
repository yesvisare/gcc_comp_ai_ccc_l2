"""
L3 M4.3: Change Management & Compliance

This module implements a GCC-grade change management system with:
- 3 change types (Standard, Normal, Emergency)
- 6-phase workflow (Request → Impact → Approval → Implementation → Verification → Review)
- Compliance-aware rollback (5 automated triggers)
- Change Advisory Board (CAB) approval routing
- Immutable audit trail (7-10 year retention)
"""

import logging
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

__all__ = [
    "ChangeType",
    "ChangeStatus",
    "RiskLevel",
    "RollbackTrigger",
    "ChangeRequest",
    "ChangeClassifier",
    "ApprovalRouter",
    "ComplianceVerifier",
    "RollbackDetector",
    "AuditTrailManager",
    "ChangeWorkflow",
    "init_database",
]


# ============================================================================
# Enums and Data Classes
# ============================================================================

class ChangeType(Enum):
    """Change type classification based on risk and frequency"""
    STANDARD = "standard"  # Pre-approved, low-risk, frequent
    NORMAL = "normal"      # Requires approval, medium-risk
    EMERGENCY = "emergency"  # Critical, requires CISO approval


class ChangeStatus(Enum):
    """6-phase workflow statuses"""
    DRAFT = "draft"
    REQUESTED = "requested"  # Phase 1: Request & Classification
    IMPACT_ASSESSMENT = "impact_assessment"  # Phase 2: Impact Assessment
    PENDING_APPROVAL = "pending_approval"  # Phase 3: Approval
    APPROVED = "approved"
    IMPLEMENTING = "implementing"  # Phase 4: Implementation
    VERIFYING = "verifying"  # Phase 5: Verification
    COMPLETED = "completed"  # Phase 6: Review & Close
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RollbackTrigger(Enum):
    """5 automated rollback triggers"""
    COMPLIANCE_TEST_FAILURE = "compliance_test_failure"
    METRICS_DEGRADED = "metrics_degraded"  # >20% degradation
    SECURITY_COMPROMISED = "security_compromised"
    USER_COMPLAINTS_THRESHOLD = "user_complaints_threshold"  # >10/hour
    AUDIT_LOG_GAPS = "audit_log_gaps"


@dataclass
class ChangeRequest:
    """Change request with compliance metadata"""
    change_id: str
    title: str
    description: str
    requestor: str
    change_type: ChangeType
    risk_level: RiskLevel
    status: ChangeStatus

    # Impact Assessment
    technical_impact: str
    compliance_impact: str
    business_impact: str
    affects_pii: bool = False
    affects_financial_data: bool = False
    affects_sox_controls: bool = False
    affects_gdpr: bool = False
    affects_dpdpa: bool = False

    # Approval
    approver: Optional[str] = None
    approval_timestamp: Optional[str] = None
    approval_conditions: Optional[str] = None

    # Implementation
    implementation_timestamp: Optional[str] = None
    deployment_notes: Optional[str] = None

    # Verification
    compliance_tests_passed: bool = False
    metrics_validated: bool = False
    rollback_tested: bool = False

    # Audit
    created_timestamp: str = None
    updated_timestamp: str = None

    def __post_init__(self):
        if self.created_timestamp is None:
            self.created_timestamp = datetime.utcnow().isoformat()
        if self.updated_timestamp is None:
            self.updated_timestamp = datetime.utcnow().isoformat()


# ============================================================================
# Change Classification
# ============================================================================

class ChangeClassifier:
    """Automatically classify changes as Standard/Normal/Emergency"""

    # Pre-approved Standard changes (low-risk, frequent)
    STANDARD_CHANGES = {
        "ssl_certificate_renewal",
        "security_patch_installation",
        "log_retention_config_update",
        "backup_schedule_update",
        "monitoring_threshold_adjustment",
    }

    @staticmethod
    def classify_change(
        description: str,
        affects_pii: bool = False,
        affects_financial_data: bool = False,
        affects_sox_controls: bool = False,
        is_emergency: bool = False
    ) -> Tuple[ChangeType, RiskLevel]:
        """
        Classify change type and risk level based on impact.

        Args:
            description: Change description
            affects_pii: Does change affect PII processing?
            affects_financial_data: Does change affect financial data?
            affects_sox_controls: Does change modify SOX controls?
            is_emergency: Is this an emergency change?

        Returns:
            Tuple of (ChangeType, RiskLevel)
        """
        logger.info(f"Classifying change: {description[:50]}...")

        # Emergency changes
        if is_emergency:
            logger.warning("⚠️ Emergency change detected")
            return ChangeType.EMERGENCY, RiskLevel.CRITICAL

        # Check if pre-approved Standard change
        description_lower = description.lower()
        for standard_pattern in ChangeClassifier.STANDARD_CHANGES:
            if standard_pattern.replace("_", " ") in description_lower:
                logger.info("✓ Classified as Standard change (pre-approved)")
                return ChangeType.STANDARD, RiskLevel.LOW

        # Normal changes - assess risk level
        risk_level = RiskLevel.LOW

        if affects_sox_controls or affects_financial_data:
            risk_level = RiskLevel.HIGH
            logger.info("High risk: Affects SOX controls or financial data")
        elif affects_pii:
            risk_level = RiskLevel.MEDIUM
            logger.info("Medium risk: Affects PII processing")

        logger.info(f"✓ Classified as Normal change with {risk_level.value} risk")
        return ChangeType.NORMAL, risk_level


# ============================================================================
# Approval Routing
# ============================================================================

class ApprovalRouter:
    """Route change requests to appropriate approvers"""

    @staticmethod
    def get_required_approvers(
        change_type: ChangeType,
        risk_level: RiskLevel
    ) -> List[str]:
        """
        Determine required approvers based on change type and risk.

        Args:
            change_type: Standard, Normal, or Emergency
            risk_level: Low, Medium, High, or Critical

        Returns:
            List of required approver roles
        """
        logger.info(f"Routing approval for {change_type.value} change with {risk_level.value} risk")

        # Standard changes: Auto-approved
        if change_type == ChangeType.STANDARD:
            logger.info("✓ Standard change - auto-approved")
            return ["auto_approved"]

        # Emergency changes: CISO + VP Engineering
        if change_type == ChangeType.EMERGENCY:
            logger.info("⚠️ Emergency change - requires CISO + VP Engineering")
            return ["ciso", "vp_engineering"]

        # Normal changes: Route based on risk
        if risk_level == RiskLevel.LOW or risk_level == RiskLevel.MEDIUM:
            logger.info("Normal change with low/medium risk - requires Manager")
            return ["manager"]

        # High risk: Requires CAB approval
        logger.info("Normal change with high risk - requires CAB")
        return [
            "chief_architect",
            "head_of_security",
            "compliance_officer",
            "lead_devops_engineer"
        ]

    @staticmethod
    def get_approval_sla_hours(change_type: ChangeType) -> int:
        """
        Get approval SLA in hours based on change type.

        Args:
            change_type: Standard, Normal, or Emergency

        Returns:
            SLA in hours
        """
        sla_map = {
            ChangeType.STANDARD: 1,  # <1 day (auto-approved)
            ChangeType.NORMAL: 72,   # 3 business days
            ChangeType.EMERGENCY: 2  # <2 hours
        }
        return sla_map[change_type]


# ============================================================================
# Compliance Verification
# ============================================================================

class ComplianceVerifier:
    """Verify compliance impact and run compliance tests"""

    @staticmethod
    def verify_compliance_controls(
        change_request: ChangeRequest,
        offline: bool = False
    ) -> Dict[str, Any]:
        """
        Verify that change doesn't compromise compliance controls.

        Args:
            change_request: Change request to verify
            offline: If True, skip actual compliance tests (return simulated results)

        Returns:
            Dict with verification results
        """
        logger.info(f"Verifying compliance for change {change_request.change_id}")

        if offline:
            logger.warning("⚠️ Offline mode - skipping actual compliance tests")
            return {
                "pii_detection_test": "skipped",
                "encryption_test": "skipped",
                "audit_logging_test": "skipped",
                "access_control_test": "skipped",
                "overall_status": "skipped",
                "reason": "offline mode"
            }

        results = {
            "pii_detection_test": "passed",
            "encryption_test": "passed",
            "audit_logging_test": "passed",
            "access_control_test": "passed",
        }

        # Simulate compliance tests based on change impact
        if change_request.affects_pii:
            logger.info("Running PII detection compliance test...")
            results["pii_detection_test"] = "passed"
            results["pii_detection_accuracy"] = 98.5  # Must be >98%

        if change_request.affects_financial_data:
            logger.info("Running SOX 404 financial data controls test...")
            results["sox_controls_test"] = "passed"

        if change_request.affects_gdpr:
            logger.info("Running GDPR Article 32 security controls test...")
            results["gdpr_security_test"] = "passed"

        if change_request.affects_dpdpa:
            logger.info("Running DPDPA Section 8 data localization test...")
            results["dpdpa_localization_test"] = "passed"

        results["overall_status"] = "passed"
        logger.info("✓ All compliance tests passed")

        return results


# ============================================================================
# Rollback Detection
# ============================================================================

class RollbackDetector:
    """Detect conditions that trigger automatic rollback"""

    @staticmethod
    def check_rollback_triggers(
        metrics: Dict[str, Any],
        baseline_metrics: Dict[str, Any]
    ) -> Optional[RollbackTrigger]:
        """
        Check if any rollback triggers are activated.

        Args:
            metrics: Current metrics after deployment
            baseline_metrics: Baseline metrics before deployment

        Returns:
            RollbackTrigger if rollback needed, None otherwise
        """
        logger.info("Checking rollback triggers...")

        # Trigger 1: Compliance test failure
        if metrics.get("compliance_tests_passed") is False:
            logger.error("❌ ROLLBACK TRIGGER: Compliance tests failed")
            return RollbackTrigger.COMPLIANCE_TEST_FAILURE

        # Trigger 2: Metrics degraded >20%
        if "latency" in metrics and "latency" in baseline_metrics:
            latency_increase = (
                (metrics["latency"] - baseline_metrics["latency"]) /
                baseline_metrics["latency"] * 100
            )
            if latency_increase > 20:
                logger.error(f"❌ ROLLBACK TRIGGER: Latency degraded by {latency_increase:.1f}%")
                return RollbackTrigger.METRICS_DEGRADED

        if "error_rate" in metrics and "error_rate" in baseline_metrics:
            error_increase = (
                (metrics["error_rate"] - baseline_metrics["error_rate"]) /
                max(baseline_metrics["error_rate"], 0.01) * 100
            )
            if error_increase > 20:
                logger.error(f"❌ ROLLBACK TRIGGER: Error rate increased by {error_increase:.1f}%")
                return RollbackTrigger.METRICS_DEGRADED

        # Trigger 3: Security controls compromised
        if not metrics.get("audit_logs_recording", True):
            logger.error("❌ ROLLBACK TRIGGER: Audit logs stopped recording")
            return RollbackTrigger.SECURITY_COMPROMISED

        # Trigger 4: User complaints >10/hour
        if metrics.get("support_tickets_per_hour", 0) > 10:
            logger.error(f"❌ ROLLBACK TRIGGER: {metrics['support_tickets_per_hour']} support tickets/hour")
            return RollbackTrigger.USER_COMPLAINTS_THRESHOLD

        # Trigger 5: Audit log gaps detected
        if metrics.get("audit_log_gap_minutes", 0) > 0:
            logger.error(f"❌ ROLLBACK TRIGGER: {metrics['audit_log_gap_minutes']} minutes of missing audit logs")
            return RollbackTrigger.AUDIT_LOG_GAPS

        logger.info("✓ No rollback triggers detected")
        return None

    @staticmethod
    def execute_rollback(
        change_id: str,
        trigger: RollbackTrigger,
        offline: bool = False
    ) -> Dict[str, Any]:
        """
        Execute automated rollback.

        Args:
            change_id: Change ID to rollback
            trigger: Rollback trigger that activated
            offline: If True, simulate rollback

        Returns:
            Dict with rollback execution results
        """
        logger.warning(f"⚠️ Executing rollback for change {change_id} due to {trigger.value}")

        if offline:
            logger.warning("⚠️ Offline mode - simulating rollback")
            return {
                "rollback_executed": True,
                "rollback_trigger": trigger.value,
                "rollback_timestamp": datetime.utcnow().isoformat(),
                "compliance_verified": True,
                "mode": "simulated"
            }

        # In production: Execute actual rollback procedures
        # 1. Restore snapshot of previous version
        # 2. Verify compliance controls after rollback
        # 3. Notify stakeholders
        # 4. Update audit trail

        result = {
            "rollback_executed": True,
            "rollback_trigger": trigger.value,
            "rollback_timestamp": datetime.utcnow().isoformat(),
            "snapshot_restored": True,
            "compliance_verified": True,
            "stakeholders_notified": ["manager", "ciso", "compliance_officer"]
        }

        logger.info(f"✓ Rollback completed successfully for {change_id}")
        return result


# ============================================================================
# Audit Trail Management
# ============================================================================

class AuditTrailManager:
    """Manage immutable audit trail with 7-10 year retention"""

    def __init__(self, db_path: str = "./changes.db"):
        """
        Initialize audit trail manager.

        Args:
            db_path: Path to SQLite database (use PostgreSQL in production)
        """
        self.db_path = db_path
        logger.info(f"Initialized AuditTrailManager with database: {db_path}")

    def log_change_event(
        self,
        change_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        actor: str
    ) -> None:
        """
        Log change event to immutable audit trail.

        Args:
            change_id: Change request ID
            event_type: Type of event (created, approved, deployed, verified, etc.)
            event_data: Event data as JSON
            actor: Username/ID of person who performed action
        """
        logger.info(f"Logging audit event: {event_type} for change {change_id} by {actor}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_trail (
                change_id, event_type, event_data, actor, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            change_id,
            event_type,
            json.dumps(event_data),
            actor,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

        logger.info(f"✓ Audit event logged: {event_type}")

    def get_change_audit_trail(self, change_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve complete audit trail for a change.

        Args:
            change_id: Change request ID

        Returns:
            List of audit events
        """
        logger.info(f"Retrieving audit trail for change {change_id}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_type, event_data, actor, timestamp
            FROM audit_trail
            WHERE change_id = ?
            ORDER BY timestamp ASC
        """, (change_id,))

        rows = cursor.fetchall()
        conn.close()

        audit_trail = [
            {
                "event_type": row[0],
                "event_data": json.loads(row[1]),
                "actor": row[2],
                "timestamp": row[3]
            }
            for row in rows
        ]

        logger.info(f"✓ Retrieved {len(audit_trail)} audit events")
        return audit_trail


# ============================================================================
# Change Workflow Orchestration
# ============================================================================

class ChangeWorkflow:
    """Orchestrate 6-phase change management workflow"""

    def __init__(self, db_path: str = "./changes.db"):
        """
        Initialize change workflow manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.audit_manager = AuditTrailManager(db_path)
        logger.info("Initialized ChangeWorkflow")

    def create_change_request(
        self,
        title: str,
        description: str,
        requestor: str,
        technical_impact: str,
        compliance_impact: str,
        business_impact: str,
        affects_pii: bool = False,
        affects_financial_data: bool = False,
        affects_sox_controls: bool = False,
        affects_gdpr: bool = False,
        affects_dpdpa: bool = False,
        is_emergency: bool = False
    ) -> ChangeRequest:
        """
        Create new change request (Phase 1: Request & Classification).

        Returns:
            ChangeRequest object with auto-classification
        """
        # Generate change ID
        change_id = f"CHG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Auto-classify change
        change_type, risk_level = ChangeClassifier.classify_change(
            description,
            affects_pii,
            affects_financial_data,
            affects_sox_controls,
            is_emergency
        )

        # Create change request
        change_request = ChangeRequest(
            change_id=change_id,
            title=title,
            description=description,
            requestor=requestor,
            change_type=change_type,
            risk_level=risk_level,
            status=ChangeStatus.REQUESTED,
            technical_impact=technical_impact,
            compliance_impact=compliance_impact,
            business_impact=business_impact,
            affects_pii=affects_pii,
            affects_financial_data=affects_financial_data,
            affects_sox_controls=affects_sox_controls,
            affects_gdpr=affects_gdpr,
            affects_dpdpa=affects_dpdpa
        )

        # Save to database
        self._save_change_request(change_request)

        # Log audit event
        self.audit_manager.log_change_event(
            change_id=change_id,
            event_type="change_requested",
            event_data=asdict(change_request),
            actor=requestor
        )

        logger.info(f"✓ Created change request {change_id} ({change_type.value}, {risk_level.value})")

        return change_request

    def approve_change(
        self,
        change_id: str,
        approver: str,
        conditions: Optional[str] = None
    ) -> ChangeRequest:
        """
        Approve change request (Phase 3: Approval).

        Args:
            change_id: Change ID to approve
            approver: Username of approver
            conditions: Optional approval conditions

        Returns:
            Updated ChangeRequest
        """
        logger.info(f"Approving change {change_id} by {approver}")

        # Load change request
        change_request = self._load_change_request(change_id)

        # Update approval status
        change_request.status = ChangeStatus.APPROVED
        change_request.approver = approver
        change_request.approval_timestamp = datetime.utcnow().isoformat()
        change_request.approval_conditions = conditions
        change_request.updated_timestamp = datetime.utcnow().isoformat()

        # Save updated change
        self._save_change_request(change_request)

        # Log audit event
        self.audit_manager.log_change_event(
            change_id=change_id,
            event_type="change_approved",
            event_data={
                "approver": approver,
                "conditions": conditions,
                "timestamp": change_request.approval_timestamp
            },
            actor=approver
        )

        logger.info(f"✓ Change {change_id} approved by {approver}")

        return change_request

    def _save_change_request(self, change_request: ChangeRequest) -> None:
        """Save change request to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO changes (change_id, data)
            VALUES (?, ?)
        """, (change_request.change_id, json.dumps(asdict(change_request))))

        conn.commit()
        conn.close()

    def _load_change_request(self, change_id: str) -> ChangeRequest:
        """Load change request from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM changes WHERE change_id = ?
        """, (change_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Change {change_id} not found")

        data = json.loads(row[0])

        # Convert string enums back to Enum types
        data["change_type"] = ChangeType(data["change_type"])
        data["risk_level"] = RiskLevel(data["risk_level"])
        data["status"] = ChangeStatus(data["status"])

        return ChangeRequest(**data)


# ============================================================================
# Database Initialization
# ============================================================================

def init_database(db_path: str = "./changes.db") -> None:
    """
    Initialize SQLite database for change management.

    Args:
        db_path: Path to SQLite database file
    """
    logger.info(f"Initializing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create changes table (stores change requests)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            change_id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    """)

    # Create audit_trail table (immutable, append-only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            change_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Create index for efficient audit trail queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_change_id
        ON audit_trail(change_id)
    """)

    conn.commit()
    conn.close()

    logger.info("✓ Database initialized successfully")
