"""
Test suite for L3 M1.4: Compliance Documentation & Evidence

Tests the core functionality of the immutable audit trail and compliance
evidence system.
"""

import pytest
from datetime import datetime, timezone
from src.l3_m1_compliance_foundations_rag_systems import (
    AuditEvent,
    AuditTrail,
    EventType,
    ComplianceReportGenerator,
    VendorRiskAssessment,
    generate_correlation_id,
    verify_hash_chain
)


class TestAuditEvent:
    """Tests for AuditEvent dataclass."""

    def test_audit_event_creation(self):
        """Test creating an audit event."""
        event = AuditEvent(
            event_type="document_ingested",
            user_id="test_user",
            resource_id="doc_123",
            action="create",
            metadata={"test": "value"}
        )

        assert event.event_type == "document_ingested"
        assert event.user_id == "test_user"
        assert event.resource_id == "doc_123"
        assert event.action == "create"
        assert event.metadata == {"test": "value"}
        assert event.previous_hash == "0" * 64
        assert event.timestamp is not None
        assert event.correlation_id is not None

    def test_compute_hash(self):
        """Test hash computation."""
        event = AuditEvent(
            event_type="test_event",
            user_id="user1",
            resource_id="resource1",
            action="read"
        )

        hash1 = event.compute_hash()

        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
        assert hash1 != "0" * 64

        # Same event should produce same hash (deterministic)
        hash2 = event.compute_hash()
        assert hash1 == hash2

    def test_hash_changes_with_content(self):
        """Test that hash changes when event content changes."""
        event1 = AuditEvent(
            event_type="test_event",
            user_id="user1",
            resource_id="resource1",
            action="read"
        )

        event2 = AuditEvent(
            event_type="test_event",
            user_id="user2",  # Different user
            resource_id="resource1",
            action="read"
        )

        hash1 = event1.compute_hash()
        hash2 = event2.compute_hash()

        assert hash1 != hash2  # Different content = different hash

    def test_to_dict(self):
        """Test event serialization to dictionary."""
        event = AuditEvent(
            event_type="test_event",
            user_id="user1",
            resource_id="resource1",
            action="read"
        )
        event.current_hash = event.compute_hash()

        event_dict = event.to_dict()

        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "test_event"
        assert event_dict["user_id"] == "user1"
        assert "current_hash" in event_dict
        assert "timestamp" in event_dict


class TestAuditTrail:
    """Tests for AuditTrail class."""

    def test_audit_trail_initialization(self):
        """Test audit trail initialization."""
        audit = AuditTrail()

        assert audit._latest_hash == "0" * 64
        assert audit._event_count == 0
        assert len(audit._in_memory_chain) == 0

    def test_log_event(self):
        """Test logging an event."""
        audit = AuditTrail()

        event = audit.log_event(
            event_type="test_event",
            user_id="user1",
            resource_id="resource1",
            action="create"
        )

        assert event is not None
        assert event.current_hash != "0" * 64
        assert event.previous_hash == "0" * 64  # First event
        assert audit._event_count == 1

    def test_log_event_validation(self):
        """Test event validation on logging."""
        audit = AuditTrail()

        with pytest.raises(ValueError, match="are required"):
            audit.log_event(
                event_type="",
                user_id="user1",
                resource_id="resource1",
                action="create"
            )

        with pytest.raises(ValueError, match="are required"):
            audit.log_event(
                event_type="test",
                user_id="",
                resource_id="resource1",
                action="create"
            )

    def test_hash_chain_linking(self):
        """Test that events are properly linked in hash chain."""
        audit = AuditTrail()

        event1 = audit.log_event(
            event_type="event1",
            user_id="user1",
            resource_id="res1",
            action="create"
        )

        event2 = audit.log_event(
            event_type="event2",
            user_id="user1",
            resource_id="res2",
            action="create"
        )

        event3 = audit.log_event(
            event_type="event3",
            user_id="user1",
            resource_id="res3",
            action="create"
        )

        # Verify chain linking
        assert event1.previous_hash == "0" * 64
        assert event2.previous_hash == event1.current_hash
        assert event3.previous_hash == event2.current_hash

    def test_verify_chain_integrity_valid(self):
        """Test chain integrity verification with valid chain."""
        audit = AuditTrail()

        # Create chain
        for i in range(5):
            audit.log_event(
                event_type=f"event_{i}",
                user_id="user1",
                resource_id=f"res_{i}",
                action="create"
            )

        is_valid, message = audit.verify_chain_integrity()

        assert is_valid is True
        assert "verified" in message.lower()
        assert "5 events" in message

    def test_verify_chain_integrity_tampered(self):
        """Test chain integrity detection of tampering."""
        audit = AuditTrail()

        # Create chain
        for i in range(3):
            audit.log_event(
                event_type=f"event_{i}",
                user_id="user1",
                resource_id=f"res_{i}",
                action="create"
            )

        # Tamper with middle event
        audit._in_memory_chain[1].metadata["tampered"] = True

        is_valid, message = audit.verify_chain_integrity()

        assert is_valid is False
        assert "mismatch" in message.lower() or "broken" in message.lower()

    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        audit = AuditTrail()

        # Create some events
        for i in range(10):
            audit.log_event(
                event_type="document_ingested" if i % 2 == 0 else "query_executed",
                user_id=f"user_{i % 3}",
                resource_id=f"res_{i}",
                action="create"
            )

        report = audit.generate_compliance_report()

        assert "summary" in report
        assert "events" in report
        assert "compliance_statement" in report
        assert "metadata" in report
        assert report["summary"]["total_events"] == 10
        assert report["summary"]["unique_users"] == 3

    def test_generate_compliance_report_with_filters(self):
        """Test compliance report with filters."""
        audit = AuditTrail()

        # Create events
        audit.log_event(
            event_type="document_ingested",
            user_id="user1",
            resource_id="res1",
            action="create"
        )

        audit.log_event(
            event_type="query_executed",
            user_id="user2",
            resource_id="res2",
            action="execute"
        )

        audit.log_event(
            event_type="document_ingested",
            user_id="user1",
            resource_id="res3",
            action="create"
        )

        # Filter by event type
        report = audit.generate_compliance_report(
            event_types=["document_ingested"]
        )

        assert report["summary"]["total_events"] == 2

        # Filter by user
        report = audit.generate_compliance_report(
            user_ids=["user1"]
        )

        assert report["summary"]["total_events"] == 2

    def test_get_events_by_correlation_id(self):
        """Test retrieving events by correlation ID."""
        audit = AuditTrail()

        correlation_id = generate_correlation_id()

        # Create events with same correlation ID
        for i in range(3):
            audit.log_event(
                event_type=f"event_{i}",
                user_id="user1",
                resource_id=f"res_{i}",
                action="create",
                correlation_id=correlation_id
            )

        # Create event with different correlation ID
        audit.log_event(
            event_type="event_other",
            user_id="user1",
            resource_id="res_other",
            action="create"
        )

        events = audit.get_events_by_correlation_id(correlation_id)

        assert len(events) == 3
        assert all(e.correlation_id == correlation_id for e in events)


class TestComplianceReportGenerator:
    """Tests for ComplianceReportGenerator class."""

    def test_generate_sox_404_report(self):
        """Test SOX 404 report generation."""
        audit = AuditTrail()

        # Create compliance events
        audit.log_event(
            event_type=EventType.DOCUMENT_INGESTED.value,
            user_id="user1",
            resource_id="financial_report.pdf",
            action="create"
        )

        audit.log_event(
            event_type=EventType.ACCESS_GRANTED.value,
            user_id="user2",
            resource_id="compliance_dashboard",
            action="read"
        )

        generator = ComplianceReportGenerator(audit)

        report = generator.generate_sox_404_report(
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z"
        )

        assert report is not None
        assert "framework" in report
        assert report["framework"] == "SOX Section 404"
        assert "retention_requirement" in report

    def test_generate_iso_27001_report(self):
        """Test ISO 27001 report generation."""
        audit = AuditTrail()

        audit.log_event(
            event_type=EventType.SYSTEM_ERROR.value,
            user_id="system",
            resource_id="app_server",
            action="error"
        )

        generator = ComplianceReportGenerator(audit)

        report = generator.generate_iso_27001_report(
            control="A.12.4.1",
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-12-31T23:59:59Z"
        )

        assert report is not None
        assert "framework" in report
        assert report["framework"] == "ISO 27001"
        assert report["control"] == "A.12.4.1"


class TestVendorRiskAssessment:
    """Tests for VendorRiskAssessment class."""

    def test_assess_vendor_low_risk(self):
        """Test vendor assessment with low risk (high score)."""
        assessor = VendorRiskAssessment()

        # All criteria passed
        responses = {criterion: True for criterion in assessor.RISK_CRITERIA.keys()}

        assessment = assessor.assess_vendor(
            vendor_name="TestVendor",
            responses=responses
        )

        assert assessment["vendor_name"] == "TestVendor"
        assert assessment["risk_score"] == 100.0
        assert assessment["risk_level"] == "LOW"
        assert "Approved" in assessment["recommendation"]

    def test_assess_vendor_medium_risk(self):
        """Test vendor assessment with medium risk."""
        assessor = VendorRiskAssessment()

        # 80% criteria passed
        responses = {}
        criteria_list = list(assessor.RISK_CRITERIA.keys())
        for i, criterion in enumerate(criteria_list):
            responses[criterion] = i < 8  # 8 out of 10 passed

        assessment = assessor.assess_vendor(
            vendor_name="TestVendor",
            responses=responses
        )

        assert assessment["risk_level"] == "MEDIUM"
        assert len(assessment["failed_criteria"]) == 2

    def test_assess_vendor_high_risk(self):
        """Test vendor assessment with high risk."""
        assessor = VendorRiskAssessment()

        # 60% criteria passed
        responses = {}
        criteria_list = list(assessor.RISK_CRITERIA.keys())
        for i, criterion in enumerate(criteria_list):
            responses[criterion] = i < 6  # 6 out of 10 passed

        assessment = assessor.assess_vendor(
            vendor_name="TestVendor",
            responses=responses
        )

        assert assessment["risk_level"] == "HIGH"
        assert "remediation" in assessment["recommendation"].lower()

    def test_assess_vendor_critical_risk(self):
        """Test vendor assessment with critical risk."""
        assessor = VendorRiskAssessment()

        # Only 40% criteria passed
        responses = {}
        criteria_list = list(assessor.RISK_CRITERIA.keys())
        for i, criterion in enumerate(criteria_list):
            responses[criterion] = i < 4  # 4 out of 10 passed

        assessment = assessor.assess_vendor(
            vendor_name="TestVendor",
            responses=responses
        )

        assert assessment["risk_level"] == "CRITICAL"
        assert "Not approved" in assessment["recommendation"]


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        assert len(id1) == 36  # UUID v4 format
        assert id1 != id2  # Should be unique

    def test_verify_hash_chain_standalone(self):
        """Test standalone hash chain verification."""
        # Create a valid chain
        events = []

        event1 = AuditEvent(
            event_type="event1",
            user_id="user1",
            resource_id="res1",
            action="create"
        )
        event1.current_hash = event1.compute_hash()
        events.append(event1)

        event2 = AuditEvent(
            event_type="event2",
            user_id="user1",
            resource_id="res2",
            action="create",
            previous_hash=event1.current_hash
        )
        event2.current_hash = event2.compute_hash()
        events.append(event2)

        is_valid, message = verify_hash_chain(events)

        assert is_valid is True
        assert "verified" in message.lower()


class TestEventTypes:
    """Tests for EventType enum."""

    def test_event_type_enum(self):
        """Test EventType enum values."""
        assert EventType.DOCUMENT_INGESTED.value == "document_ingested"
        assert EventType.QUERY_EXECUTED.value == "query_executed"
        assert EventType.PII_DETECTED.value == "pii_detected"
        assert EventType.ACCESS_GRANTED.value == "access_granted"
        assert EventType.ACCESS_DENIED.value == "access_denied"

    def test_event_type_usage(self):
        """Test using EventType enum in audit trail."""
        audit = AuditTrail()

        event = audit.log_event(
            event_type=EventType.CONFIGURATION_CHANGED.value,
            user_id="admin",
            resource_id="system_config",
            action="update"
        )

        assert event.event_type == "configuration_changed"
