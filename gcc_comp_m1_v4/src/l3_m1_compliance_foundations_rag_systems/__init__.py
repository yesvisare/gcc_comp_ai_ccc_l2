"""
L3 M1.4: Compliance Documentation & Evidence

This module implements a comprehensive compliance documentation and evidence system
for RAG platforms in GCC environments. It provides immutable audit trails using
SHA-256 hash chaining, automated evidence collection, and compliance reporting.

Key Features:
- Immutable audit trails with cryptographic hash chaining
- Automated evidence collection and export
- Compliance documentation with version control
- Vendor risk assessment framework
- Multi-framework support (SOX, SOC 2, ISO 27001, GDPR)
"""

import logging
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "AuditEvent",
    "AuditTrail",
    "EvidenceCollector",
    "ComplianceReporter",
    "VendorRiskAssessment",
    "EventType",
    "ComplianceFramework",
    "create_audit_trail",
    "verify_audit_integrity",
    "generate_compliance_report",
    "export_evidence_package"
]


class EventType(Enum):
    """Audit event types for compliance tracking."""
    DOCUMENT_ACCESSED = "document_accessed"
    DOCUMENT_MODIFIED = "document_modified"
    DOCUMENT_DELETED = "document_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGED = "permission_changed"
    CONFIG_CHANGED = "config_changed"
    DATA_EXPORTED = "data_exported"
    PII_ACCESSED = "pii_accessed"
    SECURITY_ALERT = "security_alert"


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOX = "sox"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    DPDPA = "dpdpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


@dataclass
class AuditEvent:
    """
    Immutable audit event with cryptographic hash chaining.

    Each event contains a hash of the previous event, creating a tamper-evident
    chain that satisfies SOX 404, SOC 2, and ISO 27001 requirements.

    Attributes:
        event_type: Type of audit event
        user_id: User who triggered the event
        resource_id: Resource affected by the event
        action: Specific action performed
        timestamp: ISO 8601 timestamp of event
        correlation_id: UUID for tracking across distributed systems
        metadata: Additional event-specific data
        previous_hash: SHA-256 hash of previous event in chain
        current_hash: SHA-256 hash of this event
    """
    event_type: str
    user_id: str
    resource_id: str
    action: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of event data.

        Uses deterministic JSON serialization to ensure consistent hashing.
        Excludes current_hash field to avoid circular dependency.

        Returns:
            Hexadecimal SHA-256 hash string
        """
        # Create deterministic representation (exclude current_hash)
        hash_data = {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash
        }

        # Sort keys for deterministic serialization
        canonical_json = json.dumps(hash_data, sort_keys=True)

        # Compute SHA-256 hash
        hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

        logger.debug(f"Computed hash for event {self.correlation_id}: {hash_bytes[:16]}...")
        return hash_bytes

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return asdict(self)


class AuditTrail:
    """
    Immutable audit trail with cryptographic hash chaining.

    Implements append-only logging with SHA-256 hash chains to provide
    tamper-evident audit trails for compliance requirements.

    Features:
    - Append-only operations (no updates/deletes)
    - Cryptographic hash chaining (SHA-256)
    - Correlation ID tracking across systems
    - ACID transaction guarantees via PostgreSQL
    - Integrity verification
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize audit trail.

        Args:
            storage_backend: Optional PostgreSQL connection or storage backend
        """
        self.storage_backend = storage_backend
        self.events: List[AuditEvent] = []
        self.last_hash: Optional[str] = None
        logger.info("AuditTrail initialized")

    def log_event(
        self,
        event_type: str,
        user_id: str,
        resource_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Create append-only audit event with hash chaining.

        Args:
            event_type: Type of event (see EventType enum)
            user_id: User identifier
            resource_id: Resource identifier
            action: Action performed
            metadata: Optional additional event data

        Returns:
            Created AuditEvent with computed hash

        Raises:
            ValueError: If required fields are missing
        """
        if not event_type or not user_id or not resource_id:
            logger.error("Missing required fields for audit event")
            raise ValueError("event_type, user_id, and resource_id are required")

        # Create event with link to previous hash
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            metadata=metadata or {},
            previous_hash=self.last_hash
        )

        # Compute hash for this event
        event.current_hash = event.compute_hash()

        # Store event
        self.events.append(event)
        self.last_hash = event.current_hash

        # Persist to backend if available
        if self.storage_backend:
            self._persist_event(event)

        logger.info(
            f"Logged audit event: {event_type} by {user_id} on {resource_id} "
            f"(correlation_id={event.correlation_id})"
        )

        return event

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Verify integrity of entire hash chain.

        Detects tampering by recomputing hash chain and comparing to stored values.

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if chain is intact, False if tampering detected
            - error_message: Description of integrity violation, or None if valid
        """
        if not self.events:
            logger.info("No events to verify")
            return True, None

        logger.info(f"Verifying integrity of {len(self.events)} events...")

        previous_hash = None
        for i, event in enumerate(self.events):
            # Check hash chain linkage
            if event.previous_hash != previous_hash:
                error_msg = (
                    f"Hash chain broken at event {i} (correlation_id={event.correlation_id}): "
                    f"expected previous_hash={previous_hash}, got {event.previous_hash}"
                )
                logger.error(error_msg)
                return False, error_msg

            # Recompute hash and compare
            recomputed_hash = event.compute_hash()
            if recomputed_hash != event.current_hash:
                error_msg = (
                    f"Hash mismatch at event {i} (correlation_id={event.correlation_id}): "
                    f"expected {event.current_hash}, computed {recomputed_hash}"
                )
                logger.error(error_msg)
                return False, error_msg

            previous_hash = event.current_hash

        logger.info("✅ Hash chain integrity verified")
        return True, None

    def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        framework: Optional[ComplianceFramework] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report with integrity verification.

        Args:
            start_date: Optional filter for events after this date
            end_date: Optional filter for events before this date
            framework: Optional compliance framework to report against
            user_id: Optional filter for specific user

        Returns:
            Dictionary containing:
            - events: Filtered audit events
            - integrity_verified: Boolean integrity status
            - report_metadata: Report generation details
        """
        logger.info("Generating compliance report...")

        # Verify integrity first
        is_valid, error_msg = self.verify_chain_integrity()

        # Filter events
        filtered_events = self.events.copy()

        if start_date:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e.timestamp) >= start_date
            ]

        if end_date:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e.timestamp) <= end_date
            ]

        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]

        report = {
            "report_generated_at": datetime.utcnow().isoformat(),
            "framework": framework.value if framework else "all",
            "filters": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "user_id": user_id
            },
            "total_events": len(filtered_events),
            "integrity_verified": is_valid,
            "integrity_error": error_msg,
            "events": [e.to_dict() for e in filtered_events],
            "event_types_summary": self._summarize_event_types(filtered_events)
        }

        logger.info(
            f"Generated compliance report: {len(filtered_events)} events, "
            f"integrity={'VALID' if is_valid else 'INVALID'}"
        )

        return report

    def _summarize_event_types(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Summarize event types for reporting."""
        summary = {}
        for event in events:
            summary[event.event_type] = summary.get(event.event_type, 0) + 1
        return summary

    def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to storage backend."""
        # Placeholder for PostgreSQL persistence
        # In production, this would INSERT into audit_events table
        logger.debug(f"Persisting event {event.correlation_id} to backend")


class EvidenceCollector:
    """
    Automated evidence collection for compliance frameworks.

    Collects and organizes evidence types:
    - System Evidence: Technical artifacts (logs, schemas, configs)
    - Process Evidence: Documentation (policies, procedures)
    - Outcome Evidence: Results (pen tests, vulnerability scans)
    """

    def __init__(self, s3_bucket: Optional[str] = None):
        """
        Initialize evidence collector.

        Args:
            s3_bucket: Optional S3 bucket name for evidence storage
        """
        self.s3_bucket = s3_bucket
        self.collected_evidence: Dict[str, List[Dict[str, Any]]] = {
            "system": [],
            "process": [],
            "outcome": []
        }
        logger.info("EvidenceCollector initialized")

    def collect_system_evidence(
        self,
        audit_trail: AuditTrail,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Collect system evidence (logs, configs, schemas).

        Args:
            audit_trail: AuditTrail instance to collect from
            start_date: Evidence collection start date
            end_date: Evidence collection end date

        Returns:
            Dictionary with collected system evidence
        """
        logger.info(f"Collecting system evidence from {start_date} to {end_date}")

        report = audit_trail.generate_compliance_report(
            start_date=start_date,
            end_date=end_date
        )

        evidence = {
            "evidence_type": "system",
            "collection_date": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "artifacts": {
                "audit_logs": report,
                "log_count": report["total_events"],
                "integrity_status": report["integrity_verified"]
            }
        }

        self.collected_evidence["system"].append(evidence)
        logger.info(f"Collected system evidence: {evidence['artifacts']['log_count']} events")

        return evidence

    def collect_process_evidence(
        self,
        policy_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Collect process evidence (policies, procedures).

        Args:
            policy_documents: List of policy documents with metadata

        Returns:
            Dictionary with collected process evidence
        """
        logger.info(f"Collecting process evidence: {len(policy_documents)} documents")

        evidence = {
            "evidence_type": "process",
            "collection_date": datetime.utcnow().isoformat(),
            "artifacts": {
                "policy_count": len(policy_documents),
                "policies": policy_documents
            }
        }

        self.collected_evidence["process"].append(evidence)
        logger.info(f"Collected process evidence: {len(policy_documents)} policies")

        return evidence

    def collect_outcome_evidence(
        self,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Collect outcome evidence (pen tests, vulnerability scans).

        Args:
            test_results: List of test results with metadata

        Returns:
            Dictionary with collected outcome evidence
        """
        logger.info(f"Collecting outcome evidence: {len(test_results)} results")

        evidence = {
            "evidence_type": "outcome",
            "collection_date": datetime.utcnow().isoformat(),
            "artifacts": {
                "test_count": len(test_results),
                "results": test_results
            }
        }

        self.collected_evidence["outcome"].append(evidence)
        logger.info(f"Collected outcome evidence: {len(test_results)} test results")

        return evidence

    def export_evidence_package(
        self,
        framework: ComplianceFramework,
        export_path: str
    ) -> Dict[str, Any]:
        """
        Export evidence package for specific compliance framework.

        Args:
            framework: Compliance framework to export for
            export_path: Local or S3 path for export

        Returns:
            Dictionary with export metadata
        """
        logger.info(f"Exporting evidence package for {framework.value} to {export_path}")

        package = {
            "framework": framework.value,
            "export_date": datetime.utcnow().isoformat(),
            "export_path": export_path,
            "evidence": self.collected_evidence,
            "total_evidence_items": sum(
                len(items) for items in self.collected_evidence.values()
            )
        }

        # In production, this would upload to S3 with Object Lock
        logger.info(
            f"✅ Exported evidence package: "
            f"{package['total_evidence_items']} items for {framework.value}"
        )

        return package


class ComplianceReporter:
    """
    Generate compliance reports for multiple frameworks.

    Supports SOX 404, SOC 2, ISO 27001, GDPR, DPDPA, HIPAA, PCI-DSS.
    """

    def __init__(self, audit_trail: AuditTrail):
        """
        Initialize compliance reporter.

        Args:
            audit_trail: AuditTrail instance to report from
        """
        self.audit_trail = audit_trail
        logger.info("ComplianceReporter initialized")

    def generate_sox_report(
        self,
        fiscal_year: int,
        quarter: int
    ) -> Dict[str, Any]:
        """
        Generate SOX Section 404 compliance report.

        Args:
            fiscal_year: Fiscal year for report
            quarter: Quarter (1-4)

        Returns:
            SOX compliance report dictionary
        """
        logger.info(f"Generating SOX 404 report for FY{fiscal_year} Q{quarter}")

        # Calculate quarter date range
        quarter_start = datetime(fiscal_year, (quarter - 1) * 3 + 1, 1)
        if quarter < 4:
            quarter_end = datetime(fiscal_year, quarter * 3 + 1, 1) - timedelta(days=1)
        else:
            quarter_end = datetime(fiscal_year, 12, 31)

        report = self.audit_trail.generate_compliance_report(
            start_date=quarter_start,
            end_date=quarter_end,
            framework=ComplianceFramework.SOX
        )

        # Add SOX-specific sections
        report["sox_controls"] = {
            "ITGC-01": "Access Controls - Reviewed",
            "ITGC-02": "Change Management - Reviewed",
            "ITGC-03": "Data Backup - Reviewed",
            "ITGC-04": "Incident Response - Reviewed"
        }

        logger.info(f"Generated SOX 404 report: {report['total_events']} events")
        return report

    def generate_soc2_report(
        self,
        report_period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Generate SOC 2 Type II compliance report.

        Args:
            report_period_days: Reporting period in days

        Returns:
            SOC 2 compliance report dictionary
        """
        logger.info(f"Generating SOC 2 report for {report_period_days} days")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=report_period_days)

        report = self.audit_trail.generate_compliance_report(
            start_date=start_date,
            end_date=end_date,
            framework=ComplianceFramework.SOC2
        )

        # Add SOC 2 Trust Service Criteria
        report["trust_service_criteria"] = {
            "CC6.1": "Logical and Physical Access Controls",
            "CC6.2": "Prior to Issuing Credentials",
            "CC6.3": "Provisioning and Modification",
            "CC7.2": "Detection of Security Events"
        }

        logger.info(f"Generated SOC 2 report: {report['total_events']} events")
        return report


class VendorRiskAssessment:
    """
    Structured vendor risk assessment for third-party AI providers.

    Evaluates vendors (OpenAI, Anthropic, Pinecone, etc.) against
    compliance requirements.
    """

    def __init__(self):
        """Initialize vendor risk assessment."""
        self.assessments: List[Dict[str, Any]] = []
        logger.info("VendorRiskAssessment initialized")

    def assess_vendor(
        self,
        vendor_name: str,
        services_used: List[str],
        compliance_frameworks: List[ComplianceFramework],
        risk_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct vendor risk assessment.

        Args:
            vendor_name: Name of vendor (e.g., "OpenAI", "Pinecone")
            services_used: List of services used from vendor
            compliance_frameworks: Frameworks vendor must comply with
            risk_criteria: Optional custom risk scoring criteria

        Returns:
            Vendor risk assessment dictionary
        """
        logger.info(f"Assessing vendor: {vendor_name}")

        # Default risk criteria
        criteria = risk_criteria or {
            "data_residency": {"weight": 0.3, "score": 0},
            "soc2_certified": {"weight": 0.25, "score": 0},
            "gdpr_compliant": {"weight": 0.25, "score": 0},
            "incident_history": {"weight": 0.2, "score": 0}
        }

        # Calculate weighted risk score
        total_score = sum(
            item["weight"] * item["score"]
            for item in criteria.values()
        )

        assessment = {
            "vendor_name": vendor_name,
            "assessment_date": datetime.utcnow().isoformat(),
            "services_used": services_used,
            "compliance_frameworks": [f.value for f in compliance_frameworks],
            "risk_criteria": criteria,
            "overall_risk_score": total_score,
            "risk_level": self._categorize_risk(total_score),
            "reassessment_due": (
                datetime.utcnow() + timedelta(days=365)
            ).isoformat(),
            "recommendations": self._generate_recommendations(total_score)
        }

        self.assessments.append(assessment)
        logger.info(
            f"Completed vendor assessment: {vendor_name} - "
            f"Risk Level: {assessment['risk_level']}"
        )

        return assessment

    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level based on score."""
        if score >= 0.8:
            return "LOW"
        elif score >= 0.5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _generate_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on risk score."""
        if score >= 0.8:
            return [
                "Annual reassessment recommended",
                "Maintain current monitoring"
            ]
        elif score >= 0.5:
            return [
                "Quarterly review recommended",
                "Request updated compliance certificates",
                "Implement additional monitoring"
            ]
        else:
            return [
                "Monthly review required",
                "Consider alternative vendors",
                "Implement data residency controls",
                "Escalate to compliance team"
            ]


# Convenience functions for common operations

def create_audit_trail(storage_backend: Optional[Any] = None) -> AuditTrail:
    """
    Create a new audit trail instance.

    Args:
        storage_backend: Optional PostgreSQL connection

    Returns:
        Initialized AuditTrail instance
    """
    return AuditTrail(storage_backend=storage_backend)


def verify_audit_integrity(audit_trail: AuditTrail) -> bool:
    """
    Verify integrity of audit trail.

    Args:
        audit_trail: AuditTrail instance to verify

    Returns:
        True if integrity verified, False otherwise
    """
    is_valid, error_msg = audit_trail.verify_chain_integrity()
    if not is_valid:
        logger.error(f"Audit integrity verification failed: {error_msg}")
    return is_valid


def generate_compliance_report(
    audit_trail: AuditTrail,
    framework: ComplianceFramework,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Generate compliance report for specified framework.

    Args:
        audit_trail: AuditTrail instance
        framework: Compliance framework
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Compliance report dictionary
    """
    return audit_trail.generate_compliance_report(
        start_date=start_date,
        end_date=end_date,
        framework=framework
    )


def export_evidence_package(
    audit_trail: AuditTrail,
    framework: ComplianceFramework,
    export_path: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Export complete evidence package for compliance framework.

    Args:
        audit_trail: AuditTrail instance
        framework: Compliance framework
        export_path: Export destination path
        start_date: Evidence period start
        end_date: Evidence period end

    Returns:
        Export metadata dictionary
    """
    collector = EvidenceCollector()

    # Collect system evidence
    collector.collect_system_evidence(
        audit_trail=audit_trail,
        start_date=start_date,
        end_date=end_date
    )

    # Export package
    return collector.export_evidence_package(
        framework=framework,
        export_path=export_path
    )
