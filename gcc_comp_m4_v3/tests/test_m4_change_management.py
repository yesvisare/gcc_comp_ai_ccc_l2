"""
Tests for L3 M4.3: Change Management & Compliance

Tests all major functions:
- Change classification (Standard/Normal/Emergency)
- Approval routing (Auto/Manager/CAB/CISO)
- Compliance verification
- Rollback trigger detection
- Audit trail generation
- End-to-end change workflow
"""

import pytest
import os
import tempfile
from datetime import datetime

from src.l3_m4_change_management import (
    ChangeType,
    ChangeStatus,
    RiskLevel,
    RollbackTrigger,
    ChangeRequest,
    ChangeClassifier,
    ApprovalRouter,
    ComplianceVerifier,
    RollbackDetector,
    AuditTrailManager,
    ChangeWorkflow,
    init_database,
)

# Force offline mode for tests
os.environ["OFFLINE"] = "true"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_database(path)
    yield path
    os.unlink(path)


@pytest.fixture
def workflow(temp_db):
    """Create ChangeWorkflow instance with temp database"""
    return ChangeWorkflow(temp_db)


@pytest.fixture
def audit_manager(temp_db):
    """Create AuditTrailManager instance with temp database"""
    return AuditTrailManager(temp_db)


# ============================================================================
# Test Change Classification
# ============================================================================

def test_classify_standard_change():
    """Test classification of Standard change (pre-approved, low-risk)"""
    change_type, risk_level = ChangeClassifier.classify_change(
        description="SSL certificate renewal for production API",
        affects_pii=False,
        affects_financial_data=False,
        affects_sox_controls=False,
        is_emergency=False
    )

    assert change_type == ChangeType.STANDARD
    assert risk_level == RiskLevel.LOW


def test_classify_normal_change_medium_risk():
    """Test classification of Normal change with medium risk (affects PII)"""
    change_type, risk_level = ChangeClassifier.classify_change(
        description="Upgrade embedding model from ada-002 to ada-003",
        affects_pii=True,
        affects_financial_data=False,
        affects_sox_controls=False,
        is_emergency=False
    )

    assert change_type == ChangeType.NORMAL
    assert risk_level == RiskLevel.MEDIUM


def test_classify_normal_change_high_risk():
    """Test classification of Normal change with high risk (affects SOX controls)"""
    change_type, risk_level = ChangeClassifier.classify_change(
        description="Modify financial data processing pipeline",
        affects_pii=False,
        affects_financial_data=True,
        affects_sox_controls=True,
        is_emergency=False
    )

    assert change_type == ChangeType.NORMAL
    assert risk_level == RiskLevel.HIGH


def test_classify_emergency_change():
    """Test classification of Emergency change"""
    change_type, risk_level = ChangeClassifier.classify_change(
        description="Patch zero-day vulnerability in LangChain",
        affects_pii=False,
        affects_financial_data=False,
        affects_sox_controls=False,
        is_emergency=True
    )

    assert change_type == ChangeType.EMERGENCY
    assert risk_level == RiskLevel.CRITICAL


# ============================================================================
# Test Approval Routing
# ============================================================================

def test_approval_routing_standard_change():
    """Test approval routing for Standard change (auto-approved)"""
    approvers = ApprovalRouter.get_required_approvers(
        ChangeType.STANDARD,
        RiskLevel.LOW
    )

    assert approvers == ["auto_approved"]


def test_approval_routing_normal_low_risk():
    """Test approval routing for Normal change with low risk (Manager)"""
    approvers = ApprovalRouter.get_required_approvers(
        ChangeType.NORMAL,
        RiskLevel.LOW
    )

    assert approvers == ["manager"]


def test_approval_routing_normal_high_risk():
    """Test approval routing for Normal change with high risk (CAB)"""
    approvers = ApprovalRouter.get_required_approvers(
        ChangeType.NORMAL,
        RiskLevel.HIGH
    )

    assert "chief_architect" in approvers
    assert "head_of_security" in approvers
    assert "compliance_officer" in approvers
    assert "lead_devops_engineer" in approvers


def test_approval_routing_emergency():
    """Test approval routing for Emergency change (CISO + VP Engineering)"""
    approvers = ApprovalRouter.get_required_approvers(
        ChangeType.EMERGENCY,
        RiskLevel.CRITICAL
    )

    assert "ciso" in approvers
    assert "vp_engineering" in approvers


def test_approval_sla():
    """Test approval SLA for different change types"""
    assert ApprovalRouter.get_approval_sla_hours(ChangeType.STANDARD) == 1
    assert ApprovalRouter.get_approval_sla_hours(ChangeType.NORMAL) == 72
    assert ApprovalRouter.get_approval_sla_hours(ChangeType.EMERGENCY) == 2


# ============================================================================
# Test Compliance Verification
# ============================================================================

def test_compliance_verification_offline():
    """Test compliance verification in offline mode"""
    change_request = ChangeRequest(
        change_id="CHG-TEST-001",
        title="Test change",
        description="Test",
        requestor="test_user",
        change_type=ChangeType.NORMAL,
        risk_level=RiskLevel.MEDIUM,
        status=ChangeStatus.REQUESTED,
        technical_impact="Test",
        compliance_impact="Test",
        business_impact="Test",
        affects_pii=True,
        affects_financial_data=False,
        affects_sox_controls=False
    )

    results = ComplianceVerifier.verify_compliance_controls(
        change_request,
        offline=True
    )

    assert results["overall_status"] == "skipped"
    assert results["reason"] == "offline mode"


# ============================================================================
# Test Rollback Detection
# ============================================================================

def test_rollback_trigger_compliance_failure():
    """Test rollback trigger on compliance test failure"""
    metrics = {
        "compliance_tests_passed": False
    }
    baseline_metrics = {
        "compliance_tests_passed": True
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger == RollbackTrigger.COMPLIANCE_TEST_FAILURE


def test_rollback_trigger_latency_degraded():
    """Test rollback trigger on latency degradation >20%"""
    metrics = {
        "latency": 3.8,  # 81% increase from baseline
        "compliance_tests_passed": True
    }
    baseline_metrics = {
        "latency": 2.1
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger == RollbackTrigger.METRICS_DEGRADED


def test_rollback_trigger_audit_logs_stopped():
    """Test rollback trigger on audit logs stopped recording"""
    metrics = {
        "audit_logs_recording": False,
        "compliance_tests_passed": True
    }
    baseline_metrics = {
        "audit_logs_recording": True
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger == RollbackTrigger.SECURITY_COMPROMISED


def test_rollback_trigger_user_complaints():
    """Test rollback trigger on excessive user complaints"""
    metrics = {
        "support_tickets_per_hour": 15,
        "compliance_tests_passed": True,
        "audit_logs_recording": True
    }
    baseline_metrics = {
        "support_tickets_per_hour": 2
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger == RollbackTrigger.USER_COMPLAINTS_THRESHOLD


def test_rollback_trigger_audit_log_gaps():
    """Test rollback trigger on audit log gaps detected"""
    metrics = {
        "audit_log_gap_minutes": 37,
        "compliance_tests_passed": True,
        "audit_logs_recording": True
    }
    baseline_metrics = {
        "audit_log_gap_minutes": 0
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger == RollbackTrigger.AUDIT_LOG_GAPS


def test_no_rollback_triggers():
    """Test no rollback triggers when metrics are healthy"""
    metrics = {
        "latency": 2.2,  # Only 4.8% increase
        "error_rate": 0.8,
        "compliance_tests_passed": True,
        "audit_logs_recording": True,
        "support_tickets_per_hour": 3,
        "audit_log_gap_minutes": 0
    }
    baseline_metrics = {
        "latency": 2.1,
        "error_rate": 0.7
    }

    trigger = RollbackDetector.check_rollback_triggers(metrics, baseline_metrics)

    assert trigger is None


def test_execute_rollback_offline():
    """Test rollback execution in offline mode"""
    result = RollbackDetector.execute_rollback(
        change_id="CHG-TEST-001",
        trigger=RollbackTrigger.COMPLIANCE_TEST_FAILURE,
        offline=True
    )

    assert result["rollback_executed"] is True
    assert result["rollback_trigger"] == "compliance_test_failure"
    assert result["compliance_verified"] is True
    assert result["mode"] == "simulated"


# ============================================================================
# Test Audit Trail
# ============================================================================

def test_audit_trail_logging(audit_manager):
    """Test logging events to audit trail"""
    change_id = "CHG-TEST-001"

    # Log change created event
    audit_manager.log_change_event(
        change_id=change_id,
        event_type="change_created",
        event_data={"title": "Test change"},
        actor="test_user"
    )

    # Log approval event
    audit_manager.log_change_event(
        change_id=change_id,
        event_type="change_approved",
        event_data={"approver": "manager"},
        actor="manager"
    )

    # Retrieve audit trail
    audit_trail = audit_manager.get_change_audit_trail(change_id)

    assert len(audit_trail) == 2
    assert audit_trail[0]["event_type"] == "change_created"
    assert audit_trail[0]["actor"] == "test_user"
    assert audit_trail[1]["event_type"] == "change_approved"
    assert audit_trail[1]["actor"] == "manager"


# ============================================================================
# Test Change Workflow (End-to-End)
# ============================================================================

def test_create_change_request(workflow):
    """Test creating change request (Phase 1)"""
    change_request = workflow.create_change_request(
        title="Upgrade embedding model",
        description="Upgrade from ada-002 to ada-003",
        requestor="engineer@company.com",
        technical_impact="Re-embed all documents (4 hours downtime)",
        compliance_impact="Affects PII processing, requires compliance review",
        business_impact="Improved accuracy from 78% to 84%",
        affects_pii=True,
        affects_financial_data=True,
        affects_sox_controls=True,
        is_emergency=False
    )

    assert change_request.change_id.startswith("CHG-")
    assert change_request.change_type == ChangeType.NORMAL
    assert change_request.risk_level == RiskLevel.HIGH
    assert change_request.status == ChangeStatus.REQUESTED
    assert change_request.requestor == "engineer@company.com"


def test_approve_change(workflow):
    """Test approving change request (Phase 3)"""
    # Create change request
    change_request = workflow.create_change_request(
        title="Test change",
        description="Test",
        requestor="engineer@company.com",
        technical_impact="Test",
        compliance_impact="Test",
        business_impact="Test",
        affects_pii=False,
        affects_financial_data=False,
        is_emergency=False
    )

    # Approve change
    approved_change = workflow.approve_change(
        change_id=change_request.change_id,
        approver="manager@company.com",
        conditions="Deploy to 10% canary first"
    )

    assert approved_change.status == ChangeStatus.APPROVED
    assert approved_change.approver == "manager@company.com"
    assert approved_change.approval_conditions == "Deploy to 10% canary first"
    assert approved_change.approval_timestamp is not None


def test_approve_nonexistent_change(workflow):
    """Test approving non-existent change raises ValueError"""
    with pytest.raises(ValueError, match="not found"):
        workflow.approve_change(
            change_id="CHG-NONEXISTENT",
            approver="manager@company.com"
        )


def test_end_to_end_workflow(workflow):
    """Test complete change workflow from request to approval"""
    # Phase 1: Create change request
    change_request = workflow.create_change_request(
        title="Security patch installation",
        description="Install critical security patch for production API",
        requestor="devops@company.com",
        technical_impact="10-minute downtime during deployment",
        compliance_impact="Improves security controls (positive impact)",
        business_impact="Minimal - deployment during maintenance window",
        affects_pii=False,
        affects_financial_data=False,
        is_emergency=False
    )

    # Verify auto-classification
    assert change_request.change_type == ChangeType.STANDARD
    assert change_request.risk_level == RiskLevel.LOW

    # Phase 3: Approve (auto-approved for Standard changes)
    approved_change = workflow.approve_change(
        change_id=change_request.change_id,
        approver="auto_approved"
    )

    assert approved_change.status == ChangeStatus.APPROVED

    # Verify audit trail
    audit_trail = workflow.audit_manager.get_change_audit_trail(
        change_request.change_id
    )

    assert len(audit_trail) == 2  # Created + Approved
    assert audit_trail[0]["event_type"] == "change_requested"
    assert audit_trail[1]["event_type"] == "change_approved"


# ============================================================================
# Test Database Initialization
# ============================================================================

def test_database_initialization():
    """Test database initialization creates required tables"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        init_database(path)

        # Verify database file exists
        assert os.path.exists(path)

        # Verify tables were created (implicitly tested by workflow operations)
        workflow = ChangeWorkflow(path)
        change_request = workflow.create_change_request(
            title="Test",
            description="Test",
            requestor="test",
            technical_impact="Test",
            compliance_impact="Test",
            business_impact="Test"
        )

        assert change_request.change_id.startswith("CHG-")

    finally:
        os.unlink(path)
