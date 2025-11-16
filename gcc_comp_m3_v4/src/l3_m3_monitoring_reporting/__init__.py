"""
L3 M3.4: Incident Response & Breach Notification

This module implements a production-grade incident response and breach notification
system for GCC compliance environments, featuring:
- 4-tier incident classification (P0-P3)
- 6-phase response workflow (Detection → Post-Mortem)
- GDPR Article 33 & DPDPA notification automation
- Multi-tenant incident isolation
"""

import logging
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime, timedelta, timezone
from enum import Enum
from dataclasses import dataclass, asdict
import json
import hashlib

logger = logging.getLogger(__name__)

# Incident severity levels (P0 = Critical, P3 = Low)
class IncidentSeverity(str, Enum):
    P0 = "P0_CRITICAL"      # Data breach, system-wide outage, regulatory violation
    P1 = "P1_HIGH"          # Partial data exposure, service degradation, security incident
    P2 = "P2_MEDIUM"        # Minor security event, isolated tenant issue
    P3 = "P3_LOW"           # Low-impact incident, configuration drift

# Incident response phases
class ResponsePhase(str, Enum):
    DETECTION = "detection"
    CONTAINMENT = "containment"
    INVESTIGATION = "investigation"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    POST_MORTEM = "post_mortem"

# Incident types
class IncidentType(str, Enum):
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SERVICE_OUTAGE = "service_outage"
    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_FAILURE = "compliance_failure"
    PII_EXPOSURE = "pii_exposure"

@dataclass
class Incident:
    """Represents a security or compliance incident"""
    incident_id: str
    tenant_id: str
    severity: IncidentSeverity
    incident_type: IncidentType
    description: str
    detected_at: str  # ISO 8601 timestamp
    detected_by: str  # User ID or system component
    affected_users: List[str]
    affected_data_types: List[str]
    current_phase: ResponsePhase
    notification_required: bool
    notification_deadline: Optional[str] = None  # GDPR: 72 hours from detection
    status: str = "ACTIVE"
    resolution_time: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class NotificationRecord:
    """Records breach notification to authorities or users"""
    notification_id: str
    incident_id: str
    recipient: str  # DPA email, user email, etc.
    notification_type: Literal["REGULATORY", "USER", "INTERNAL"]
    sent_at: str
    regulation: str  # GDPR, DPDPA, HIPAA, etc.
    notification_content: str
    acknowledgment_received: bool = False


class IncidentClassifier:
    """
    Classifies incidents by severity based on impact assessment.

    Classification criteria:
    - P0 (Critical): >1000 users affected OR PII/financial data exposed OR regulatory deadline
    - P1 (High): 100-1000 users affected OR authentication bypass OR service degradation
    - P2 (Medium): 10-100 users affected OR minor security event
    - P3 (Low): <10 users affected OR configuration issue
    """

    @staticmethod
    def classify_incident(
        incident_type: IncidentType,
        affected_users_count: int,
        data_sensitivity: Literal["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"],
        service_impact: Literal["NONE", "PARTIAL", "FULL"]
    ) -> IncidentSeverity:
        """
        Classify incident severity based on multiple factors.

        Args:
            incident_type: Type of incident
            affected_users_count: Number of users impacted
            data_sensitivity: Sensitivity level of affected data
            service_impact: Scope of service disruption

        Returns:
            IncidentSeverity enum value (P0-P3)
        """
        logger.info(f"Classifying incident: type={incident_type}, users={affected_users_count}, "
                   f"data={data_sensitivity}, impact={service_impact}")

        # P0 criteria: Critical incidents requiring immediate escalation
        if incident_type in [IncidentType.DATA_BREACH, IncidentType.PII_EXPOSURE]:
            if affected_users_count > 1000 or data_sensitivity in ["CONFIDENTIAL", "RESTRICTED"]:
                logger.warning("Classified as P0_CRITICAL - data breach with high impact")
                return IncidentSeverity.P0

        if service_impact == "FULL" and affected_users_count > 500:
            logger.warning("Classified as P0_CRITICAL - full service outage")
            return IncidentSeverity.P0

        # P1 criteria: High-priority incidents
        if incident_type == IncidentType.UNAUTHORIZED_ACCESS and affected_users_count > 100:
            logger.warning("Classified as P1_HIGH - unauthorized access")
            return IncidentSeverity.P1

        if service_impact == "PARTIAL" and affected_users_count > 200:
            logger.warning("Classified as P1_HIGH - partial service degradation")
            return IncidentSeverity.P1

        if data_sensitivity == "CONFIDENTIAL" and affected_users_count > 50:
            logger.warning("Classified as P1_HIGH - confidential data exposure")
            return IncidentSeverity.P1

        # P2 criteria: Medium-priority incidents
        if affected_users_count > 10 and affected_users_count <= 100:
            logger.info("Classified as P2_MEDIUM - moderate user impact")
            return IncidentSeverity.P2

        if incident_type == IncidentType.SECURITY_VIOLATION:
            logger.info("Classified as P2_MEDIUM - security violation")
            return IncidentSeverity.P2

        # P3 criteria: Low-priority incidents
        logger.info("Classified as P3_LOW - low impact incident")
        return IncidentSeverity.P3

    @staticmethod
    def requires_notification(severity: IncidentSeverity, incident_type: IncidentType) -> bool:
        """
        Determine if incident requires regulatory notification.

        GDPR Article 33: Breach notification to DPA within 72 hours if risk to rights/freedoms
        DPDPA: Similar requirement for data breaches

        Returns:
            True if notification required, False otherwise
        """
        # P0 incidents always require notification
        if severity == IncidentSeverity.P0:
            logger.warning("Notification REQUIRED - P0 incident")
            return True

        # Data breaches and PII exposure require notification
        if incident_type in [IncidentType.DATA_BREACH, IncidentType.PII_EXPOSURE]:
            logger.warning("Notification REQUIRED - data breach/PII exposure")
            return True

        logger.info("Notification NOT required for this incident")
        return False


class IncidentResponseWorkflow:
    """
    Implements 6-phase incident response workflow.

    Phases:
    1. Detection: Identify and log incident
    2. Containment: Isolate affected systems/tenants
    3. Investigation: Analyze root cause and scope
    4. Eradication: Remove threat/vulnerability
    5. Recovery: Restore normal operations
    6. Post-Mortem: Document lessons learned
    """

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.notifications: List[NotificationRecord] = []

    def detect_incident(
        self,
        tenant_id: str,
        incident_type: IncidentType,
        description: str,
        detected_by: str,
        affected_users: List[str],
        affected_data_types: List[str],
        data_sensitivity: Literal["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"],
        service_impact: Literal["NONE", "PARTIAL", "FULL"]
    ) -> Incident:
        """
        Phase 1: Detect and classify incident.

        Args:
            tenant_id: Affected tenant ID (multi-tenant isolation)
            incident_type: Type of incident
            description: Human-readable description
            detected_by: User/system that detected incident
            affected_users: List of user IDs impacted
            affected_data_types: Types of data affected (PII, financial, health, etc.)
            data_sensitivity: Sensitivity classification
            service_impact: Service availability impact

        Returns:
            Incident object with assigned ID and severity
        """
        logger.info(f"DETECTION: New incident for tenant {tenant_id}")

        # Generate unique incident ID
        timestamp = datetime.now(timezone.utc).isoformat()
        incident_id = self._generate_incident_id(tenant_id, timestamp)

        # Classify severity
        severity = IncidentClassifier.classify_incident(
            incident_type,
            len(affected_users),
            data_sensitivity,
            service_impact
        )

        # Check if notification required
        notification_required = IncidentClassifier.requires_notification(severity, incident_type)
        notification_deadline = None

        if notification_required:
            # GDPR Article 33: 72 hours from detection
            deadline = datetime.now(timezone.utc) + timedelta(hours=72)
            notification_deadline = deadline.isoformat()
            logger.warning(f"Notification deadline: {notification_deadline}")

        # Create incident record
        incident = Incident(
            incident_id=incident_id,
            tenant_id=tenant_id,
            severity=severity,
            incident_type=incident_type,
            description=description,
            detected_at=timestamp,
            detected_by=detected_by,
            affected_users=affected_users,
            affected_data_types=affected_data_types,
            current_phase=ResponsePhase.DETECTION,
            notification_required=notification_required,
            notification_deadline=notification_deadline,
            status="ACTIVE"
        )

        self.incidents[incident_id] = incident
        logger.info(f"Incident {incident_id} created with severity {severity}")

        return incident

    def contain_incident(self, incident_id: str, containment_actions: List[str]) -> Dict[str, Any]:
        """
        Phase 2: Contain incident to prevent further damage.

        Containment actions:
        - Disable affected user accounts
        - Revoke API keys/access tokens
        - Isolate affected tenant
        - Block network traffic
        - Disable vulnerable services

        Args:
            incident_id: Incident to contain
            containment_actions: List of actions taken

        Returns:
            Status dict with containment confirmation
        """
        if incident_id not in self.incidents:
            logger.error(f"Incident {incident_id} not found")
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.info(f"CONTAINMENT: Incident {incident_id}")

        # Update phase
        incident.current_phase = ResponsePhase.CONTAINMENT

        # Log containment actions
        logger.info(f"Containment actions for {incident_id}: {containment_actions}")

        return {
            "incident_id": incident_id,
            "phase": ResponsePhase.CONTAINMENT,
            "actions_taken": containment_actions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "contained"
        }

    def investigate_incident(self, incident_id: str, investigation_findings: str) -> Dict[str, Any]:
        """
        Phase 3: Investigate root cause and scope.

        Investigation tasks:
        - Analyze audit logs
        - Interview affected users
        - Review system changes
        - Identify attack vector
        - Assess full scope of damage

        Args:
            incident_id: Incident to investigate
            investigation_findings: Summary of investigation results

        Returns:
            Investigation report dict
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.info(f"INVESTIGATION: Incident {incident_id}")

        incident.current_phase = ResponsePhase.INVESTIGATION

        return {
            "incident_id": incident_id,
            "phase": ResponsePhase.INVESTIGATION,
            "findings": investigation_findings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def eradicate_threat(self, incident_id: str, eradication_actions: List[str]) -> Dict[str, Any]:
        """
        Phase 4: Eradicate root cause.

        Eradication actions:
        - Patch vulnerabilities
        - Remove malware
        - Reset compromised credentials
        - Update access policies
        - Apply security hardening

        Args:
            incident_id: Incident to eradicate
            eradication_actions: Actions taken to remove threat

        Returns:
            Eradication confirmation dict
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.info(f"ERADICATION: Incident {incident_id}")

        incident.current_phase = ResponsePhase.ERADICATION

        return {
            "incident_id": incident_id,
            "phase": ResponsePhase.ERADICATION,
            "actions_taken": eradication_actions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def recover_services(self, incident_id: str, recovery_steps: List[str]) -> Dict[str, Any]:
        """
        Phase 5: Recover normal operations.

        Recovery steps:
        - Re-enable affected services
        - Restore user access
        - Verify system integrity
        - Monitor for recurrence
        - Update runbooks

        Args:
            incident_id: Incident to recover from
            recovery_steps: Steps taken to restore operations

        Returns:
            Recovery status dict
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.info(f"RECOVERY: Incident {incident_id}")

        incident.current_phase = ResponsePhase.RECOVERY

        return {
            "incident_id": incident_id,
            "phase": ResponsePhase.RECOVERY,
            "recovery_steps": recovery_steps,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def close_with_post_mortem(
        self,
        incident_id: str,
        lessons_learned: str,
        preventive_measures: List[str]
    ) -> Dict[str, Any]:
        """
        Phase 6: Document post-mortem and close incident.

        Post-mortem content:
        - Timeline of events
        - Root cause analysis
        - Lessons learned
        - Preventive measures
        - Process improvements

        Args:
            incident_id: Incident to close
            lessons_learned: Summary of lessons learned
            preventive_measures: Actions to prevent recurrence

        Returns:
            Post-mortem report dict
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.info(f"POST-MORTEM: Closing incident {incident_id}")

        incident.current_phase = ResponsePhase.POST_MORTEM
        incident.status = "CLOSED"
        incident.resolution_time = datetime.now(timezone.utc).isoformat()

        # Calculate time to resolution
        detected = datetime.fromisoformat(incident.detected_at)
        resolved = datetime.fromisoformat(incident.resolution_time)
        duration = resolved - detected

        logger.info(f"Incident {incident_id} resolved in {duration}")

        return {
            "incident_id": incident_id,
            "phase": ResponsePhase.POST_MORTEM,
            "detected_at": incident.detected_at,
            "resolved_at": incident.resolution_time,
            "duration": str(duration),
            "lessons_learned": lessons_learned,
            "preventive_measures": preventive_measures
        }

    def send_breach_notification(
        self,
        incident_id: str,
        recipient: str,
        notification_type: Literal["REGULATORY", "USER", "INTERNAL"],
        regulation: str = "GDPR"
    ) -> NotificationRecord:
        """
        Send breach notification to authorities or affected users.

        GDPR Article 33: Notify DPA within 72 hours
        GDPR Article 34: Notify users if high risk to rights/freedoms
        DPDPA: Similar notification requirements

        Args:
            incident_id: Incident requiring notification
            recipient: Email/contact for notification
            notification_type: Type of notification (regulatory, user, internal)
            regulation: Applicable regulation (GDPR, DPDPA, HIPAA, etc.)

        Returns:
            NotificationRecord with confirmation
        """
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        logger.warning(f"Sending {regulation} breach notification for {incident_id}")

        # Check if within deadline
        if incident.notification_deadline:
            deadline = datetime.fromisoformat(incident.notification_deadline)
            now = datetime.now(timezone.utc)
            if now > deadline:
                logger.error(f"DEADLINE MISSED: Notification due by {deadline}, now is {now}")

        # Generate notification content
        notification_content = self._generate_notification_content(incident, regulation)

        # Create notification record
        notification_id = self._generate_notification_id(incident_id)
        notification = NotificationRecord(
            notification_id=notification_id,
            incident_id=incident_id,
            recipient=recipient,
            notification_type=notification_type,
            sent_at=datetime.now(timezone.utc).isoformat(),
            regulation=regulation,
            notification_content=notification_content,
            acknowledgment_received=False
        )

        self.notifications.append(notification)

        logger.info(f"Notification {notification_id} sent to {recipient}")

        return notification

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieve incident by ID"""
        return self.incidents.get(incident_id)

    def list_incidents(
        self,
        tenant_id: Optional[str] = None,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[str] = None
    ) -> List[Incident]:
        """
        List incidents with optional filters.

        Args:
            tenant_id: Filter by tenant (multi-tenant isolation)
            severity: Filter by severity level
            status: Filter by status (ACTIVE, CLOSED)

        Returns:
            List of matching incidents
        """
        incidents = list(self.incidents.values())

        if tenant_id:
            incidents = [i for i in incidents if i.tenant_id == tenant_id]

        if severity:
            incidents = [i for i in incidents if i.severity == severity]

        if status:
            incidents = [i for i in incidents if i.status == status]

        logger.info(f"Found {len(incidents)} incidents matching filters")
        return incidents

    def _generate_incident_id(self, tenant_id: str, timestamp: str) -> str:
        """Generate unique incident ID with tenant isolation"""
        hash_input = f"{tenant_id}-{timestamp}".encode('utf-8')
        hash_hex = hashlib.sha256(hash_input).hexdigest()[:8]
        return f"INC-{tenant_id[:4]}-{hash_hex}"

    def _generate_notification_id(self, incident_id: str) -> str:
        """Generate unique notification ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_input = f"{incident_id}-{timestamp}".encode('utf-8')
        hash_hex = hashlib.sha256(hash_input).hexdigest()[:8]
        return f"NOT-{hash_hex}"

    def _generate_notification_content(self, incident: Incident, regulation: str) -> str:
        """Generate notification content based on regulation requirements"""
        if regulation == "GDPR":
            return f"""
GDPR Article 33 Breach Notification

Incident ID: {incident.incident_id}
Detected: {incident.detected_at}
Severity: {incident.severity}
Type: {incident.incident_type}

Description: {incident.description}

Affected Users: {len(incident.affected_users)} users
Affected Data Types: {', '.join(incident.affected_data_types)}

Current Status: {incident.current_phase}

This notification is made pursuant to GDPR Article 33 (Notification of a personal data breach to the supervisory authority).
"""
        elif regulation == "DPDPA":
            return f"""
DPDPA Breach Notification

Incident ID: {incident.incident_id}
Detected: {incident.detected_at}
Severity: {incident.severity}

Description: {incident.description}

Affected Individuals: {len(incident.affected_users)}
Data Categories: {', '.join(incident.affected_data_types)}

This notification is made pursuant to the Digital Personal Data Protection Act, 2023.
"""
        else:
            return f"""
Security Incident Notification

Incident ID: {incident.incident_id}
Detected: {incident.detected_at}
Severity: {incident.severity}
Type: {incident.incident_type}

Description: {incident.description}

Affected Users: {len(incident.affected_users)}
"""


# Export public API
__all__ = [
    "IncidentSeverity",
    "ResponsePhase",
    "IncidentType",
    "Incident",
    "NotificationRecord",
    "IncidentClassifier",
    "IncidentResponseWorkflow"
]
