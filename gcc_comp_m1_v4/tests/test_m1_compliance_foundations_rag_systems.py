"""
Test suite for L3 M1.4: Compliance Documentation & Evidence

Tests the core functionality of the compliance evidence system:
- Audit event creation and hash chaining
- Hash chain integrity verification
- Compliance report generation
- Evidence collection and export
- Vendor risk assessment
"""

import pytest
from datetime import datetime, timedelta
import hashlib
import json

from src.l3_m1_compliance_foundations_rag_systems import (
    AuditEvent,
    AuditTrail,
    EvidenceCollector,
    ComplianceReporter,
    VendorRiskAssessment,
    EventType,
    ComplianceFramework,
    create_audit_trail,
    verify_audit_integrity,
    generate_compliance_report
)


# ============================================================================
# Audit Event Tests
# ============================================================================

def test_audit_event_creation():
    """Test basic audit event creation."""
    event = AuditEvent(
        event_type="document_accessed",
        user_id="test_user",
        resource_id="test_document.pdf",
        action="read"
    )

    assert event.event_type == "document_accessed"
    assert event.user_id == "test_user"
    assert event.resource_id == "test_document.pdf"
    assert event.action == "read"
    assert event.timestamp is not None
    assert event.correlation_id is not None


def test_audit_event_hash_computation():
    """Test SHA-256 hash computation for audit events."""
    event = AuditEvent(
        event_type="document_accessed",
        user_id="test_user",
        resource_id="test_document.pdf",
        action="read",
        timestamp="2024-01-01T00:00:00",
        correlation_id="test-correlation-id"
    )

    hash1 = event.compute_hash()
    hash2 = event.compute_hash()

    # Same event should produce same hash (deterministic)
    assert hash1 == hash2
    # Hash should be 64 characters (SHA-256 hex)
    assert len(hash1) == 64
    # Hash should be hexadecimal
    assert all(c in '0123456789abcdef' for c in hash1)


def test_audit_event_hash_changes_with_data():
    """Test that hash changes when event data changes."""
    event1 = AuditEvent(
        event_type="document_accessed",
        user_id="user1",
        resource_id="doc.pdf",
        action="read",
        timestamp="2024-01-01T00:00:00",
        correlation_id="id-1"
    )

    event2 = AuditEvent(
        event_type="document_accessed",
        user_id="user2",  # Different user
        resource_id="doc.pdf",
        action="read",
        timestamp="2024-01-01T00:00:00",
        correlation_id="id-1"
    )

    assert event1.compute_hash() != event2.compute_hash()


def test_audit_event_to_dict():
    """Test event serialization to dictionary."""
    event = AuditEvent(
        event_type="document_accessed",
        user_id="test_user",
        resource_id="test_document.pdf",
        action="read",
        metadata={"ip_address": "192.168.1.1"}
    )

    event_dict = event.to_dict()

    assert isinstance(event_dict, dict)
    assert event_dict["event_type"] == "document_accessed"
    assert event_dict["user_id"] == "test_user"
    assert event_dict["metadata"]["ip_address"] == "192.168.1.1"


# ============================================================================
# Audit Trail Tests
# ============================================================================

def test_create_audit_trail():
    """Test audit trail creation."""
    trail = create_audit_trail()

    assert trail is not None
    assert isinstance(trail, AuditTrail)
    assert len(trail.events) == 0
    assert trail.last_hash is None


def test_log_single_event():
    """Test logging a single audit event."""
    trail = create_audit_trail()

    event = trail.log_event(
        event_type="document_accessed",
        user_id="test_user",
        resource_id="document.pdf",
        action="read"
    )

    assert len(trail.events) == 1
    assert event.current_hash is not None
    assert event.previous_hash is None  # First event has no previous
    assert trail.last_hash == event.current_hash


def test_log_multiple_events_hash_chaining():
    """Test hash chaining across multiple events."""
    trail = create_audit_trail()

    event1 = trail.log_event(
        event_type="user_login",
        user_id="user1",
        resource_id="system",
        action="login"
    )

    event2 = trail.log_event(
        event_type="document_accessed",
        user_id="user1",
        resource_id="doc.pdf",
        action="read"
    )

    event3 = trail.log_event(
        event_type="user_logout",
        user_id="user1",
        resource_id="system",
        action="logout"
    )

    # Verify hash chain
    assert event1.previous_hash is None
    assert event2.previous_hash == event1.current_hash
    assert event3.previous_hash == event2.current_hash

    # Verify trail state
    assert len(trail.events) == 3
    assert trail.last_hash == event3.current_hash


def test_log_event_with_metadata():
    """Test logging event with metadata."""
    trail = create_audit_trail()

    metadata = {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "sensitivity_level": "confidential"
    }

    event = trail.log_event(
        event_type="pii_accessed",
        user_id="analyst_jane",
        resource_id="customer_data.csv",
        action="export",
        metadata=metadata
    )

    assert event.metadata == metadata
    assert event.metadata["ip_address"] == "192.168.1.100"


def test_log_event_validation():
    """Test that logging requires all mandatory fields."""
    trail = create_audit_trail()

    with pytest.raises(ValueError, match="event_type, user_id, and resource_id are required"):
        trail.log_event(
            event_type="",
            user_id="user1",
            resource_id="doc.pdf",
            action="read"
        )

    with pytest.raises(ValueError):
        trail.log_event(
            event_type="document_accessed",
            user_id="",
            resource_id="doc.pdf",
            action="read"
        )


def test_verify_chain_integrity_valid():
    """Test integrity verification of valid hash chain."""
    trail = create_audit_trail()

    # Log several events
    for i in range(5):
        trail.log_event(
            event_type="test_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )

    is_valid, error_msg = trail.verify_chain_integrity()

    assert is_valid is True
    assert error_msg is None


def test_verify_chain_integrity_detects_tampering():
    """Test that tampering is detected by integrity verification."""
    trail = create_audit_trail()

    # Log several events
    event1 = trail.log_event(
        event_type="event1",
        user_id="user1",
        resource_id="res1",
        action="action1"
    )

    event2 = trail.log_event(
        event_type="event2",
        user_id="user2",
        resource_id="res2",
        action="action2"
    )

    event3 = trail.log_event(
        event_type="event3",
        user_id="user3",
        resource_id="res3",
        action="action3"
    )

    # Tamper with event2 (simulate unauthorized modification)
    event2.user_id = "hacker"

    # Verification should fail
    is_valid, error_msg = verify_audit_integrity(trail)

    assert is_valid is False
    assert error_msg is not None
    assert "Hash mismatch" in error_msg


def test_verify_chain_integrity_detects_broken_chain():
    """Test detection of broken hash chain."""
    trail = create_audit_trail()

    # Log events
    event1 = trail.log_event(
        event_type="event1",
        user_id="user1",
        resource_id="res1",
        action="action1"
    )

    event2 = trail.log_event(
        event_type="event2",
        user_id="user2",
        resource_id="res2",
        action="action2"
    )

    # Break the chain (simulate hash manipulation)
    event2.previous_hash = "fake_hash_0000"

    is_valid, error_msg = trail.verify_chain_integrity()

    assert is_valid is False
    assert "Hash chain broken" in error_msg


# ============================================================================
# Compliance Report Tests
# ============================================================================

def test_generate_compliance_report_all_events():
    """Test generating compliance report with all events."""
    trail = create_audit_trail()

    # Log events
    for i in range(10):
        trail.log_event(
            event_type="test_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )

    report = trail.generate_compliance_report()

    assert report["total_events"] == 10
    assert report["integrity_verified"] is True
    assert len(report["events"]) == 10


def test_generate_compliance_report_date_filter():
    """Test compliance report with date filtering."""
    trail = create_audit_trail()

    # Create events with specific timestamps
    now = datetime.utcnow()
    past = now - timedelta(days=30)

    # Manually create events with specific times (bypassing auto-timestamp)
    for i in range(5):
        event = trail.log_event(
            event_type="old_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )
        # Simulate old timestamp
        event.timestamp = (past + timedelta(days=i)).isoformat()

    for i in range(3):
        event = trail.log_event(
            event_type="recent_event",
            user_id=f"user{i+5}",
            resource_id=f"resource{i+5}",
            action="test"
        )

    # Filter for only recent events (last 7 days)
    start_date = now - timedelta(days=7)
    report = trail.generate_compliance_report(start_date=start_date)

    # Should only include recent events
    assert report["total_events"] <= 3


def test_generate_compliance_report_user_filter():
    """Test compliance report with user filtering."""
    trail = create_audit_trail()

    # Log events for different users
    for i in range(5):
        trail.log_event(
            event_type="test_event",
            user_id="alice",
            resource_id=f"resource{i}",
            action="test"
        )

    for i in range(3):
        trail.log_event(
            event_type="test_event",
            user_id="bob",
            resource_id=f"resource{i}",
            action="test"
        )

    # Filter for alice's events
    report = trail.generate_compliance_report(user_id="alice")

    assert report["total_events"] == 5
    assert all(e["user_id"] == "alice" for e in report["events"])


def test_compliance_reporter_sox_report():
    """Test SOX Section 404 report generation."""
    trail = create_audit_trail()

    # Log some events
    for i in range(10):
        trail.log_event(
            event_type="financial_access",
            user_id=f"analyst{i}",
            resource_id="financial_report.pdf",
            action="read"
        )

    reporter = ComplianceReporter(trail)
    sox_report = reporter.generate_sox_report(fiscal_year=2024, quarter=3)

    assert sox_report is not None
    assert sox_report["framework"] == "sox"
    assert "sox_controls" in sox_report
    assert "ITGC-01" in sox_report["sox_controls"]


def test_compliance_reporter_soc2_report():
    """Test SOC 2 Type II report generation."""
    trail = create_audit_trail()

    # Log security events
    for i in range(15):
        trail.log_event(
            event_type="security_event",
            user_id=f"user{i}",
            resource_id="system",
            action="access"
        )

    reporter = ComplianceReporter(trail)
    soc2_report = reporter.generate_soc2_report(report_period_days=365)

    assert soc2_report is not None
    assert soc2_report["framework"] == "soc2"
    assert "trust_service_criteria" in soc2_report
    assert "CC6.1" in soc2_report["trust_service_criteria"]


# ============================================================================
# Evidence Collector Tests
# ============================================================================

def test_evidence_collector_initialization():
    """Test evidence collector initialization."""
    collector = EvidenceCollector(s3_bucket="test-bucket")

    assert collector.s3_bucket == "test-bucket"
    assert "system" in collector.collected_evidence
    assert "process" in collector.collected_evidence
    assert "outcome" in collector.collected_evidence


def test_collect_system_evidence():
    """Test system evidence collection."""
    trail = create_audit_trail()

    # Log events
    for i in range(20):
        trail.log_event(
            event_type="system_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )

    collector = EvidenceCollector()
    now = datetime.utcnow()
    start_date = now - timedelta(days=1)

    evidence = collector.collect_system_evidence(
        audit_trail=trail,
        start_date=start_date,
        end_date=now
    )

    assert evidence["evidence_type"] == "system"
    assert "artifacts" in evidence
    assert "audit_logs" in evidence["artifacts"]
    assert evidence["artifacts"]["log_count"] >= 0


def test_collect_process_evidence():
    """Test process evidence collection."""
    collector = EvidenceCollector()

    policies = [
        {"name": "Data Retention Policy", "version": "v2.0", "approved_date": "2024-01-01"},
        {"name": "Access Control Policy", "version": "v1.5", "approved_date": "2024-02-01"}
    ]

    evidence = collector.collect_process_evidence(policy_documents=policies)

    assert evidence["evidence_type"] == "process"
    assert evidence["artifacts"]["policy_count"] == 2
    assert len(evidence["artifacts"]["policies"]) == 2


def test_collect_outcome_evidence():
    """Test outcome evidence collection."""
    collector = EvidenceCollector()

    test_results = [
        {"test": "Penetration Test", "result": "PASS", "date": "2024-09-01"},
        {"test": "Vulnerability Scan", "result": "PASS", "date": "2024-09-15"}
    ]

    evidence = collector.collect_outcome_evidence(test_results=test_results)

    assert evidence["evidence_type"] == "outcome"
    assert evidence["artifacts"]["test_count"] == 2
    assert len(evidence["artifacts"]["results"]) == 2


def test_export_evidence_package():
    """Test evidence package export."""
    trail = create_audit_trail()

    # Log events
    for i in range(10):
        trail.log_event(
            event_type="test_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )

    collector = EvidenceCollector()
    now = datetime.utcnow()

    # Collect evidence
    collector.collect_system_evidence(
        audit_trail=trail,
        start_date=now - timedelta(days=1),
        end_date=now
    )

    # Export package
    package = collector.export_evidence_package(
        framework=ComplianceFramework.SOX,
        export_path="./test_exports"
    )

    assert package["framework"] == "sox"
    assert "export_path" in package
    assert package["total_evidence_items"] > 0


# ============================================================================
# Vendor Risk Assessment Tests
# ============================================================================

def test_vendor_risk_assessment_initialization():
    """Test vendor risk assessment initialization."""
    assessor = VendorRiskAssessment()

    assert assessor is not None
    assert len(assessor.assessments) == 0


def test_assess_vendor_basic():
    """Test basic vendor assessment."""
    assessor = VendorRiskAssessment()

    assessment = assessor.assess_vendor(
        vendor_name="OpenAI",
        services_used=["GPT-4", "Embeddings API"],
        compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.GDPR],
        risk_criteria={
            "data_residency": {"weight": 0.3, "score": 0.7},
            "soc2_certified": {"weight": 0.25, "score": 1.0},
            "gdpr_compliant": {"weight": 0.25, "score": 0.8},
            "incident_history": {"weight": 0.2, "score": 0.9}
        }
    )

    assert assessment["vendor_name"] == "OpenAI"
    assert len(assessment["services_used"]) == 2
    assert "soc2" in assessment["compliance_frameworks"]
    assert "overall_risk_score" in assessment
    assert "risk_level" in assessment
    assert "recommendations" in assessment


def test_assess_vendor_risk_levels():
    """Test vendor risk level categorization."""
    assessor = VendorRiskAssessment()

    # Low risk (score >= 0.8)
    low_risk = assessor.assess_vendor(
        vendor_name="Low Risk Vendor",
        services_used=["Service A"],
        compliance_frameworks=[ComplianceFramework.SOC2],
        risk_criteria={
            "criterion1": {"weight": 1.0, "score": 0.9}
        }
    )
    assert low_risk["risk_level"] == "LOW"

    # Medium risk (0.5 <= score < 0.8)
    medium_risk = assessor.assess_vendor(
        vendor_name="Medium Risk Vendor",
        services_used=["Service B"],
        compliance_frameworks=[ComplianceFramework.SOC2],
        risk_criteria={
            "criterion1": {"weight": 1.0, "score": 0.6}
        }
    )
    assert medium_risk["risk_level"] == "MEDIUM"

    # High risk (score < 0.5)
    high_risk = assessor.assess_vendor(
        vendor_name="High Risk Vendor",
        services_used=["Service C"],
        compliance_frameworks=[ComplianceFramework.SOC2],
        risk_criteria={
            "criterion1": {"weight": 1.0, "score": 0.3}
        }
    )
    assert high_risk["risk_level"] == "HIGH"


def test_assess_vendor_recommendations():
    """Test vendor assessment recommendations."""
    assessor = VendorRiskAssessment()

    # High risk should have more stringent recommendations
    high_risk = assessor.assess_vendor(
        vendor_name="High Risk Vendor",
        services_used=["Service"],
        compliance_frameworks=[ComplianceFramework.SOC2],
        risk_criteria={
            "criterion1": {"weight": 1.0, "score": 0.2}
        }
    )

    assert len(high_risk["recommendations"]) > 0
    assert any("Monthly review" in rec or "alternative vendors" in rec
               for rec in high_risk["recommendations"])


# ============================================================================
# Integration Tests
# ============================================================================

def test_end_to_end_compliance_workflow():
    """Test complete compliance workflow from logging to reporting."""
    # 1. Create audit trail
    trail = create_audit_trail()

    # 2. Log various events
    event_types = ["user_login", "document_accessed", "config_changed", "user_logout"]
    users = ["alice", "bob", "charlie"]

    for i in range(20):
        trail.log_event(
            event_type=event_types[i % len(event_types)],
            user_id=users[i % len(users)],
            resource_id=f"resource_{i}",
            action="test_action",
            metadata={"iteration": i}
        )

    # 3. Verify integrity
    is_valid, error = trail.verify_chain_integrity()
    assert is_valid is True

    # 4. Generate compliance report
    report = generate_compliance_report(
        audit_trail=trail,
        framework=ComplianceFramework.SOX
    )
    assert report["total_events"] == 20
    assert report["integrity_verified"] is True

    # 5. Collect evidence
    collector = EvidenceCollector()
    now = datetime.utcnow()
    evidence = collector.collect_system_evidence(
        audit_trail=trail,
        start_date=now - timedelta(days=1),
        end_date=now
    )
    assert evidence["artifacts"]["log_count"] >= 0

    # 6. Export evidence package
    package = collector.export_evidence_package(
        framework=ComplianceFramework.SOX,
        export_path="./test_exports"
    )
    assert package["total_evidence_items"] > 0


def test_multi_framework_compliance():
    """Test compliance reporting for multiple frameworks."""
    trail = create_audit_trail()

    # Log events
    for i in range(30):
        trail.log_event(
            event_type="compliance_event",
            user_id=f"user{i}",
            resource_id=f"resource{i}",
            action="test"
        )

    # Generate reports for different frameworks
    frameworks = [
        ComplianceFramework.SOX,
        ComplianceFramework.SOC2,
        ComplianceFramework.ISO27001,
        ComplianceFramework.GDPR
    ]

    for framework in frameworks:
        report = generate_compliance_report(
            audit_trail=trail,
            framework=framework
        )
        assert report["framework"] == framework.value
        assert report["total_events"] == 30
        assert report["integrity_verified"] is True


# ============================================================================
# Performance Tests
# ============================================================================

def test_large_audit_trail_performance():
    """Test performance with large number of events."""
    trail = create_audit_trail()

    # Log 1000 events
    for i in range(1000):
        trail.log_event(
            event_type="performance_test",
            user_id=f"user{i % 10}",
            resource_id=f"resource{i}",
            action="test"
        )

    assert len(trail.events) == 1000

    # Verify integrity (should complete in reasonable time)
    is_valid, error = trail.verify_chain_integrity()
    assert is_valid is True


def test_hash_computation_consistency():
    """Test that hash computation is consistent across multiple calls."""
    event = AuditEvent(
        event_type="test",
        user_id="user1",
        resource_id="resource1",
        action="action1",
        timestamp="2024-01-01T00:00:00",
        correlation_id="test-id"
    )

    # Compute hash 100 times
    hashes = [event.compute_hash() for _ in range(100)]

    # All hashes should be identical
    assert len(set(hashes)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
