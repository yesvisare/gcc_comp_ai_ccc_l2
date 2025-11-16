"""
Tests for L3 M3.4: Incident Response & Breach Notification

Tests ALL major functions including:
- Incident classification
- 6-phase response workflow
- Breach notification automation
- Multi-tenant isolation
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.l3_m3_monitoring_reporting import (
    IncidentSeverity,
    ResponsePhase,
    IncidentType,
    Incident,
    NotificationRecord,
    IncidentClassifier,
    IncidentResponseWorkflow
)


class TestIncidentClassifier:
    """Test incident severity classification logic"""

    def test_classify_p0_data_breach_high_volume(self):
        """Test P0 classification for high-volume data breach"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.DATA_BREACH,
            affected_users_count=1500,
            data_sensitivity="CONFIDENTIAL",
            service_impact="PARTIAL"
        )
        assert severity == IncidentSeverity.P0

    def test_classify_p0_pii_exposure_sensitive_data(self):
        """Test P0 classification for PII exposure with sensitive data"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.PII_EXPOSURE,
            affected_users_count=500,
            data_sensitivity="RESTRICTED",
            service_impact="NONE"
        )
        assert severity == IncidentSeverity.P0

    def test_classify_p0_full_service_outage(self):
        """Test P0 classification for full service outage"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.SERVICE_OUTAGE,
            affected_users_count=1000,
            data_sensitivity="INTERNAL",
            service_impact="FULL"
        )
        assert severity == IncidentSeverity.P0

    def test_classify_p1_unauthorized_access(self):
        """Test P1 classification for unauthorized access"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.UNAUTHORIZED_ACCESS,
            affected_users_count=150,
            data_sensitivity="INTERNAL",
            service_impact="PARTIAL"
        )
        assert severity == IncidentSeverity.P1

    def test_classify_p1_partial_degradation(self):
        """Test P1 classification for partial service degradation"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.SERVICE_OUTAGE,
            affected_users_count=300,
            data_sensitivity="PUBLIC",
            service_impact="PARTIAL"
        )
        assert severity == IncidentSeverity.P1

    def test_classify_p1_confidential_data_moderate_volume(self):
        """Test P1 classification for confidential data exposure"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.DATA_BREACH,
            affected_users_count=75,
            data_sensitivity="CONFIDENTIAL",
            service_impact="NONE"
        )
        assert severity == IncidentSeverity.P1

    def test_classify_p2_security_violation(self):
        """Test P2 classification for security violation"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.SECURITY_VIOLATION,
            affected_users_count=50,
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )
        assert severity == IncidentSeverity.P2

    def test_classify_p2_moderate_users(self):
        """Test P2 classification for moderate user impact"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.COMPLIANCE_FAILURE,
            affected_users_count=50,
            data_sensitivity="PUBLIC",
            service_impact="NONE"
        )
        assert severity == IncidentSeverity.P2

    def test_classify_p3_low_impact(self):
        """Test P3 classification for low impact incident"""
        severity = IncidentClassifier.classify_incident(
            incident_type=IncidentType.SERVICE_OUTAGE,
            affected_users_count=5,
            data_sensitivity="PUBLIC",
            service_impact="NONE"
        )
        assert severity == IncidentSeverity.P3

    def test_notification_required_p0(self):
        """Test notification requirement for P0 incidents"""
        assert IncidentClassifier.requires_notification(
            IncidentSeverity.P0,
            IncidentType.DATA_BREACH
        ) is True

    def test_notification_required_data_breach(self):
        """Test notification requirement for data breaches"""
        assert IncidentClassifier.requires_notification(
            IncidentSeverity.P2,
            IncidentType.DATA_BREACH
        ) is True

    def test_notification_required_pii_exposure(self):
        """Test notification requirement for PII exposure"""
        assert IncidentClassifier.requires_notification(
            IncidentSeverity.P2,
            IncidentType.PII_EXPOSURE
        ) is True

    def test_notification_not_required_p3_non_breach(self):
        """Test notification not required for P3 non-breach incidents"""
        assert IncidentClassifier.requires_notification(
            IncidentSeverity.P3,
            IncidentType.SERVICE_OUTAGE
        ) is False


class TestIncidentResponseWorkflow:
    """Test 6-phase incident response workflow"""

    @pytest.fixture
    def workflow(self):
        """Create fresh workflow instance for each test"""
        return IncidentResponseWorkflow()

    def test_detect_incident_basic(self, workflow):
        """Test basic incident detection and classification"""
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.UNAUTHORIZED_ACCESS,
            description="Failed login attempts detected",
            detected_by="security-monitor",
            affected_users=["user-123", "user-456"],
            affected_data_types=["login_credentials"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        assert incident.tenant_id == "tenant-test"
        assert incident.incident_type == IncidentType.UNAUTHORIZED_ACCESS
        assert incident.current_phase == ResponsePhase.DETECTION
        assert incident.status == "ACTIVE"
        assert len(incident.affected_users) == 2
        assert incident.incident_id.startswith("INC-")

    def test_detect_incident_with_notification_deadline(self, workflow):
        """Test incident detection with GDPR notification deadline"""
        incident = workflow.detect_incident(
            tenant_id="tenant-acme",
            incident_type=IncidentType.DATA_BREACH,
            description="Customer database accessed without authorization",
            detected_by="admin-001",
            affected_users=["user-" + str(i) for i in range(100)],
            affected_data_types=["email", "phone", "address"],
            data_sensitivity="CONFIDENTIAL",
            service_impact="PARTIAL"
        )

        assert incident.notification_required is True
        assert incident.notification_deadline is not None

        # Verify deadline is ~72 hours from now
        deadline = datetime.fromisoformat(incident.notification_deadline)
        now = datetime.now(timezone.utc)
        time_diff = deadline - now

        assert time_diff.total_seconds() > 71 * 3600  # At least 71 hours
        assert time_diff.total_seconds() < 73 * 3600  # At most 73 hours

    def test_contain_incident(self, workflow):
        """Test incident containment phase"""
        # First detect incident
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.SECURITY_VIOLATION,
            description="SQL injection attempt",
            detected_by="waf",
            affected_users=["user-789"],
            affected_data_types=["database_query"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        # Then contain it
        result = workflow.contain_incident(
            incident_id=incident.incident_id,
            containment_actions=[
                "Blocked IP address 192.168.1.100",
                "Disabled affected user account",
                "Revoked active session tokens"
            ]
        )

        assert result["phase"] == ResponsePhase.CONTAINMENT
        assert result["status"] == "contained"
        assert len(result["actions_taken"]) == 3

        # Verify phase updated
        updated_incident = workflow.get_incident(incident.incident_id)
        assert updated_incident.current_phase == ResponsePhase.CONTAINMENT

    def test_investigate_incident(self, workflow):
        """Test incident investigation phase"""
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.UNAUTHORIZED_ACCESS,
            description="Privilege escalation detected",
            detected_by="audit-system",
            affected_users=["user-999"],
            affected_data_types=["access_control"],
            data_sensitivity="CONFIDENTIAL",
            service_impact="NONE"
        )

        result = workflow.investigate_incident(
            incident_id=incident.incident_id,
            investigation_findings="User exploited RBAC misconfiguration to gain admin privileges. "
                                  "No data exfiltration detected. Affected system: auth-service-v2."
        )

        assert result["phase"] == ResponsePhase.INVESTIGATION
        assert "RBAC misconfiguration" in result["findings"]

        updated_incident = workflow.get_incident(incident.incident_id)
        assert updated_incident.current_phase == ResponsePhase.INVESTIGATION

    def test_eradicate_threat(self, workflow):
        """Test threat eradication phase"""
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.SECURITY_VIOLATION,
            description="Malicious script injection",
            detected_by="security-scan",
            affected_users=["user-555"],
            affected_data_types=["application_code"],
            data_sensitivity="INTERNAL",
            service_impact="PARTIAL"
        )

        result = workflow.eradicate_threat(
            incident_id=incident.incident_id,
            eradication_actions=[
                "Patched XSS vulnerability in user input validation",
                "Deployed WAF rule to block similar attacks",
                "Removed malicious scripts from application cache"
            ]
        )

        assert result["phase"] == ResponsePhase.ERADICATION
        assert len(result["actions_taken"]) == 3

        updated_incident = workflow.get_incident(incident.incident_id)
        assert updated_incident.current_phase == ResponsePhase.ERADICATION

    def test_recover_services(self, workflow):
        """Test service recovery phase"""
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.SERVICE_OUTAGE,
            description="Database connection pool exhausted",
            detected_by="monitoring",
            affected_users=["user-" + str(i) for i in range(50)],
            affected_data_types=["service_availability"],
            data_sensitivity="PUBLIC",
            service_impact="PARTIAL"
        )

        result = workflow.recover_services(
            incident_id=incident.incident_id,
            recovery_steps=[
                "Restarted database connection pool",
                "Increased max connections from 100 to 200",
                "Re-enabled API endpoints",
                "Verified all services operational"
            ]
        )

        assert result["phase"] == ResponsePhase.RECOVERY
        assert len(result["recovery_steps"]) == 4

        updated_incident = workflow.get_incident(incident.incident_id)
        assert updated_incident.current_phase == ResponsePhase.RECOVERY

    def test_close_with_post_mortem(self, workflow):
        """Test incident closure with post-mortem"""
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.COMPLIANCE_FAILURE,
            description="Audit log retention policy violated",
            detected_by="compliance-check",
            affected_users=["system"],
            affected_data_types=["audit_logs"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        result = workflow.close_with_post_mortem(
            incident_id=incident.incident_id,
            lessons_learned="Log retention policy was not enforced by automated scripts. "
                           "Manual intervention required to restore deleted logs.",
            preventive_measures=[
                "Implemented automated log retention enforcement",
                "Added compliance checks to CI/CD pipeline",
                "Scheduled weekly compliance audits"
            ]
        )

        assert result["phase"] == ResponsePhase.POST_MORTEM
        assert len(result["preventive_measures"]) == 3
        assert "duration" in result

        # Verify incident closed
        updated_incident = workflow.get_incident(incident.incident_id)
        assert updated_incident.status == "CLOSED"
        assert updated_incident.resolution_time is not None

    def test_send_breach_notification_gdpr(self, workflow):
        """Test GDPR breach notification"""
        incident = workflow.detect_incident(
            tenant_id="tenant-eu",
            incident_type=IncidentType.DATA_BREACH,
            description="Customer PII exposed via API vulnerability",
            detected_by="security-team",
            affected_users=["user-" + str(i) for i in range(200)],
            affected_data_types=["email", "name", "phone_number"],
            data_sensitivity="CONFIDENTIAL",
            service_impact="PARTIAL"
        )

        notification = workflow.send_breach_notification(
            incident_id=incident.incident_id,
            recipient="dpa@example.eu",
            notification_type="REGULATORY",
            regulation="GDPR"
        )

        assert notification.notification_type == "REGULATORY"
        assert notification.regulation == "GDPR"
        assert "GDPR Article 33" in notification.notification_content
        assert notification.acknowledgment_received is False

    def test_send_breach_notification_dpdpa(self, workflow):
        """Test DPDPA breach notification"""
        incident = workflow.detect_incident(
            tenant_id="tenant-india",
            incident_type=IncidentType.PII_EXPOSURE,
            description="User data accessed by unauthorized employee",
            detected_by="hr-audit",
            affected_users=["user-" + str(i) for i in range(50)],
            affected_data_types=["personal_data"],
            data_sensitivity="RESTRICTED",
            service_impact="NONE"
        )

        notification = workflow.send_breach_notification(
            incident_id=incident.incident_id,
            recipient="dpdpa@india.gov",
            notification_type="REGULATORY",
            regulation="DPDPA"
        )

        assert notification.regulation == "DPDPA"
        assert "DPDPA" in notification.notification_content

    def test_list_incidents_by_tenant(self, workflow):
        """Test multi-tenant incident isolation"""
        # Create incidents for different tenants
        workflow.detect_incident(
            tenant_id="tenant-a",
            incident_type=IncidentType.SERVICE_OUTAGE,
            description="Tenant A incident",
            detected_by="system",
            affected_users=["user-a1"],
            affected_data_types=["service"],
            data_sensitivity="PUBLIC",
            service_impact="PARTIAL"
        )

        workflow.detect_incident(
            tenant_id="tenant-b",
            incident_type=IncidentType.SECURITY_VIOLATION,
            description="Tenant B incident",
            detected_by="system",
            affected_users=["user-b1"],
            affected_data_types=["security"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        # Filter by tenant A
        tenant_a_incidents = workflow.list_incidents(tenant_id="tenant-a")
        assert len(tenant_a_incidents) == 1
        assert tenant_a_incidents[0].tenant_id == "tenant-a"

        # Filter by tenant B
        tenant_b_incidents = workflow.list_incidents(tenant_id="tenant-b")
        assert len(tenant_b_incidents) == 1
        assert tenant_b_incidents[0].tenant_id == "tenant-b"

    def test_list_incidents_by_severity(self, workflow):
        """Test filtering incidents by severity"""
        # Create P0 incident
        workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.DATA_BREACH,
            description="P0 incident",
            detected_by="system",
            affected_users=["user-" + str(i) for i in range(2000)],
            affected_data_types=["pii"],
            data_sensitivity="RESTRICTED",
            service_impact="FULL"
        )

        # Create P3 incident
        workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.SERVICE_OUTAGE,
            description="P3 incident",
            detected_by="system",
            affected_users=["user-1"],
            affected_data_types=["service"],
            data_sensitivity="PUBLIC",
            service_impact="NONE"
        )

        # Filter by P0
        p0_incidents = workflow.list_incidents(severity=IncidentSeverity.P0)
        assert len(p0_incidents) >= 1
        assert all(i.severity == IncidentSeverity.P0 for i in p0_incidents)

    def test_list_incidents_by_status(self, workflow):
        """Test filtering incidents by status"""
        # Create and close one incident
        incident = workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.COMPLIANCE_FAILURE,
            description="Closed incident",
            detected_by="system",
            affected_users=["user-1"],
            affected_data_types=["compliance"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        workflow.close_with_post_mortem(
            incident_id=incident.incident_id,
            lessons_learned="Test",
            preventive_measures=["Test measure"]
        )

        # Create active incident
        workflow.detect_incident(
            tenant_id="tenant-test",
            incident_type=IncidentType.SECURITY_VIOLATION,
            description="Active incident",
            detected_by="system",
            affected_users=["user-2"],
            affected_data_types=["security"],
            data_sensitivity="INTERNAL",
            service_impact="NONE"
        )

        # Filter by ACTIVE
        active = workflow.list_incidents(status="ACTIVE")
        assert len(active) >= 1
        assert all(i.status == "ACTIVE" for i in active)

        # Filter by CLOSED
        closed = workflow.list_incidents(status="CLOSED")
        assert len(closed) >= 1
        assert all(i.status == "CLOSED" for i in closed)

    def test_incident_not_found(self, workflow):
        """Test error handling for non-existent incident"""
        with pytest.raises(ValueError, match="not found"):
            workflow.contain_incident("nonexistent-id", ["action"])

        with pytest.raises(ValueError, match="not found"):
            workflow.investigate_incident("nonexistent-id", "findings")

        with pytest.raises(ValueError, match="not found"):
            workflow.eradicate_threat("nonexistent-id", ["action"])

        with pytest.raises(ValueError, match="not found"):
            workflow.recover_services("nonexistent-id", ["step"])

        with pytest.raises(ValueError, match="not found"):
            workflow.close_with_post_mortem("nonexistent-id", "lessons", ["measure"])

        with pytest.raises(ValueError, match="not found"):
            workflow.send_breach_notification("nonexistent-id", "recipient", "REGULATORY")

    def test_full_workflow_end_to_end(self, workflow):
        """Test complete 6-phase workflow from detection to closure"""
        # Phase 1: Detection
        incident = workflow.detect_incident(
            tenant_id="tenant-prod",
            incident_type=IncidentType.UNAUTHORIZED_ACCESS,
            description="Unauthorized API access detected from external IP",
            detected_by="api-gateway",
            affected_users=["user-123", "user-456"],
            affected_data_types=["customer_data", "api_keys"],
            data_sensitivity="CONFIDENTIAL",
            service_impact="PARTIAL"
        )

        assert incident.current_phase == ResponsePhase.DETECTION
        assert incident.status == "ACTIVE"

        # Phase 2: Containment
        workflow.contain_incident(
            incident.incident_id,
            ["Blocked IP 203.0.113.0", "Revoked API keys", "Disabled affected accounts"]
        )
        assert workflow.get_incident(incident.incident_id).current_phase == ResponsePhase.CONTAINMENT

        # Phase 3: Investigation
        workflow.investigate_incident(
            incident.incident_id,
            "Attacker used stolen API keys to access customer data. 2 accounts compromised."
        )
        assert workflow.get_incident(incident.incident_id).current_phase == ResponsePhase.INVESTIGATION

        # Phase 4: Eradication
        workflow.eradicate_threat(
            incident.incident_id,
            ["Rotated all API keys", "Implemented API rate limiting", "Added IP allowlisting"]
        )
        assert workflow.get_incident(incident.incident_id).current_phase == ResponsePhase.ERADICATION

        # Phase 5: Recovery
        workflow.recover_services(
            incident.incident_id,
            ["Re-enabled API access with new keys", "Notified affected users", "Resumed normal operations"]
        )
        assert workflow.get_incident(incident.incident_id).current_phase == ResponsePhase.RECOVERY

        # Phase 6: Post-Mortem
        result = workflow.close_with_post_mortem(
            incident.incident_id,
            "API keys were stored in plaintext in source code. Implemented secrets management solution.",
            ["Use secrets manager for all credentials", "Enable API key rotation policy", "Add security scanning to CI/CD"]
        )

        final_incident = workflow.get_incident(incident.incident_id)
        assert final_incident.current_phase == ResponsePhase.POST_MORTEM
        assert final_incident.status == "CLOSED"
        assert final_incident.resolution_time is not None
