"""
L3 M1.4: Compliance Documentation & Evidence

This module implements immutable audit trails for GCC compliance using cryptographic
hash chaining (SHA-256). Designed for SOX 404, ISO 27001, SOC 2, and GDPR compliance.

Key Features:
- Immutable audit logging with hash chain integrity
- Automated evidence collection pipelines
- Compliance report generation
- Vendor risk assessment framework
"""

import logging
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "AuditEvent",
    "AuditTrail",
    "EventType",
    "verify_hash_chain",
    "generate_correlation_id",
    "ComplianceReportGenerator",
    "VendorRiskAssessment"
]


class EventType(Enum):
    """Standard event types for compliance auditing."""

    DOCUMENT_INGESTED = "document_ingested"
    QUERY_EXECUTED = "query_executed"
    PII_DETECTED = "pii_detected"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    CONFIGURATION_CHANGED = "configuration_changed"
    POLICY_UPDATED = "policy_updated"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_EXPORTED = "data_exported"
    SYSTEM_ERROR = "system_error"


@dataclass
class AuditEvent:
    """
    Immutable audit event with cryptographic hash linking.

    This dataclass represents a single audit log entry with all required
    fields for compliance (SOX 404, ISO 27001, SOC 2, GDPR).

    Attributes:
        event_type: Type of event (from EventType enum or custom string)
        user_id: Identifier of the user or system that triggered the event
        resource_id: Identifier of the resource affected
        action: Action performed (create, read, update, delete, execute)
        timestamp: ISO 8601 timestamp with timezone
        correlation_id: UUID v4 for request tracing across components
        metadata: Additional context as key-value pairs
        previous_hash: SHA-256 hash of previous event (links to chain)
        current_hash: SHA-256 hash of this event
    """

    event_type: str
    user_id: str
    resource_id: str
    action: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_hash: str = "0" * 64  # Genesis block sentinel
    current_hash: str = ""

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of this event.

        The hash includes all event fields plus the previous hash,
        creating an immutable chain. Any modification breaks subsequent hashes.

        Returns:
            64-character hexadecimal SHA-256 hash
        """
        hash_input = {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash
        }

        # Deterministic JSON serialization
        hash_string = json.dumps(hash_input, sort_keys=True, separators=(',', ':'))

        # SHA-256 hashing
        hash_bytes = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

        return hash_bytes

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash
        }


class AuditTrail:
    """
    Immutable audit trail with cryptographic hash chaining.

    This class manages append-only audit logs stored in PostgreSQL with
    SHA-256 hash chain integrity. Supports compliance reporting for
    SOX 404, ISO 27001, SOC 2, and GDPR.

    The hash chain ensures:
    - Tamper detection (any modification breaks chain)
    - Non-repudiation (events cannot be denied)
    - Chronological ordering (each event links to previous)
    """

    def __init__(self, db_connection=None):
        """
        Initialize audit trail.

        Args:
            db_connection: PostgreSQL connection string or connection object
                          (optional for testing/offline mode)
        """
        self.db_connection = db_connection
        self._latest_hash = "0" * 64  # Genesis block
        self._event_count = 0
        self._in_memory_chain: List[AuditEvent] = []  # For offline/testing mode

        logger.info("AuditTrail initialized")

        if db_connection:
            try:
                self._ensure_schema()
                self._cache_latest_hash()
            except Exception as e:
                logger.warning(f"⚠️ Database unavailable: {e}. Running in memory mode.")

    def _ensure_schema(self):
        """
        Create audit_logs table if it doesn't exist.

        Schema includes:
        - id: Primary key (auto-increment)
        - All AuditEvent fields
        - Indexes on timestamp, user_id, correlation_id, resource_id
        - JSONB metadata for flexible querying
        """
        logger.info("Schema creation would happen here (PostgreSQL required)")
        # In production, execute:
        # CREATE TABLE IF NOT EXISTS audit_logs (
        #     id SERIAL PRIMARY KEY,
        #     event_type VARCHAR(100) NOT NULL,
        #     user_id VARCHAR(255) NOT NULL,
        #     resource_id VARCHAR(255) NOT NULL,
        #     action VARCHAR(50) NOT NULL,
        #     timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        #     correlation_id UUID NOT NULL,
        #     metadata JSONB,
        #     previous_hash CHAR(64) NOT NULL,
        #     current_hash CHAR(64) NOT NULL,
        #     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        # );
        # CREATE INDEX idx_timestamp ON audit_logs(timestamp);
        # CREATE INDEX idx_user_id ON audit_logs(user_id);
        # CREATE INDEX idx_correlation_id ON audit_logs(correlation_id);
        # CREATE INDEX idx_resource_id ON audit_logs(resource_id);
        # CREATE INDEX idx_metadata ON audit_logs USING GIN(metadata);

    def _cache_latest_hash(self):
        """
        Cache the latest hash for performance.

        Fetches the most recent event's hash from database to avoid
        full chain traversal on every insert.
        """
        # In production, execute:
        # SELECT current_hash FROM audit_logs ORDER BY id DESC LIMIT 1;
        if self._in_memory_chain:
            self._latest_hash = self._in_memory_chain[-1].current_hash
            self._event_count = len(self._in_memory_chain)
        else:
            logger.info("No events in chain yet, using genesis hash")

    def log_event(
        self,
        event_type: str,
        user_id: str,
        resource_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> AuditEvent:
        """
        Log an immutable audit event.

        Creates a new event linked to the previous event via hash chain.
        The event is append-only and cannot be modified or deleted.

        Args:
            event_type: Type of event (e.g., "document_ingested")
            user_id: User or system that triggered the event
            resource_id: Resource affected (e.g., document ID)
            action: Action performed (create, read, update, delete, execute)
            metadata: Optional additional context
            correlation_id: Optional correlation ID (auto-generated if not provided)

        Returns:
            The created AuditEvent with computed hash

        Raises:
            ValueError: If required fields are empty
        """
        # Validate inputs
        if not event_type or not user_id or not resource_id or not action:
            raise ValueError("event_type, user_id, resource_id, and action are required")

        # Create event
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            metadata=metadata or {},
            correlation_id=correlation_id or str(uuid.uuid4()),
            previous_hash=self._latest_hash
        )

        # Compute hash
        event.current_hash = event.compute_hash()

        # Store event
        if self.db_connection:
            # In production: INSERT INTO audit_logs (...) VALUES (...)
            logger.info(f"Would insert event into PostgreSQL: {event.event_type}")

        # In-memory storage (for testing/offline)
        self._in_memory_chain.append(event)

        # Update cache
        self._latest_hash = event.current_hash
        self._event_count += 1

        logger.info(
            f"Logged event: {event.event_type} | User: {user_id} | "
            f"Resource: {resource_id} | Action: {action}"
        )

        return event

    def verify_chain_integrity(
        self,
        start_id: Optional[int] = None,
        end_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Verify the integrity of the hash chain.

        Recomputes hashes for all events in the specified range and
        verifies they match stored hashes. Any tampering breaks the chain.

        Args:
            start_id: Starting event ID (default: first event)
            end_id: Ending event ID (default: last event)

        Returns:
            Tuple of (is_valid, message):
            - is_valid: True if chain is intact, False if tampered
            - message: Description of result or first broken link
        """
        if not self._in_memory_chain:
            return True, "No events to verify"

        events = self._in_memory_chain[start_id:end_id] if start_id or end_id else self._in_memory_chain

        logger.info(f"Verifying hash chain integrity for {len(events)} events...")

        expected_previous_hash = "0" * 64  # Genesis

        for idx, event in enumerate(events):
            # Check previous hash linkage
            if event.previous_hash != expected_previous_hash:
                message = (
                    f"❌ Chain broken at event {idx + (start_id or 0)}: "
                    f"Expected previous_hash={expected_previous_hash[:16]}... "
                    f"but found {event.previous_hash[:16]}..."
                )
                logger.error(message)
                return False, message

            # Recompute current hash
            recomputed_hash = event.compute_hash()
            if recomputed_hash != event.current_hash:
                message = (
                    f"❌ Hash mismatch at event {idx + (start_id or 0)}: "
                    f"Stored={event.current_hash[:16]}... "
                    f"Recomputed={recomputed_hash[:16]}..."
                )
                logger.error(message)
                return False, message

            # Update for next iteration
            expected_previous_hash = event.current_hash

        message = f"✅ Hash chain verified: {len(events)} events intact, no tampering detected"
        logger.info(message)
        return True, message

    def generate_compliance_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report for audit requests.

        Filters events by date range, event types, and users, then
        generates statistics and compliance statements.

        Args:
            start_date: ISO 8601 start date (default: beginning of time)
            end_date: ISO 8601 end date (default: now)
            event_types: Filter by event types (default: all)
            user_ids: Filter by user IDs (default: all)

        Returns:
            Dictionary containing:
            - summary: Statistics (total events, date range, users)
            - events: Filtered event list
            - compliance_statement: Integrity verification result
            - metadata: Report generation details
        """
        logger.info(
            f"Generating compliance report: "
            f"dates={start_date} to {end_date}, "
            f"event_types={event_types}, users={user_ids}"
        )

        # Filter events
        filtered_events = self._in_memory_chain.copy()

        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]

        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]

        if event_types:
            filtered_events = [e for e in filtered_events if e.event_type in event_types]

        if user_ids:
            filtered_events = [e for e in filtered_events if e.user_id in user_ids]

        # Generate statistics
        unique_users = len(set(e.user_id for e in filtered_events))
        unique_resources = len(set(e.resource_id for e in filtered_events))
        event_type_counts = {}
        for event in filtered_events:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1

        # Verify integrity
        is_valid, integrity_message = self.verify_chain_integrity()

        report = {
            "summary": {
                "total_events": len(filtered_events),
                "date_range": {
                    "start": start_date or (filtered_events[0].timestamp if filtered_events else None),
                    "end": end_date or (filtered_events[-1].timestamp if filtered_events else None)
                },
                "unique_users": unique_users,
                "unique_resources": unique_resources,
                "event_type_distribution": event_type_counts
            },
            "events": [e.to_dict() for e in filtered_events[:100]],  # Limit to 100 for performance
            "compliance_statement": {
                "chain_integrity": "VERIFIED" if is_valid else "FAILED",
                "message": integrity_message,
                "audit_standard": "SOX 404, ISO 27001 A.12.4.1, SOC 2 CC7.2, GDPR Article 30"
            },
            "metadata": {
                "report_generated_at": datetime.now(timezone.utc).isoformat(),
                "total_events_in_system": self._event_count,
                "events_in_report": len(filtered_events),
                "truncated": len(filtered_events) > 100
            }
        }

        logger.info(f"Report generated: {len(filtered_events)} events, integrity={is_valid}")

        return report

    def get_events_by_correlation_id(self, correlation_id: str) -> List[AuditEvent]:
        """
        Retrieve all events with the same correlation ID.

        This traces a single request across multiple components
        (e.g., RAG query → vector DB → LLM → response).

        Args:
            correlation_id: UUID v4 correlation ID

        Returns:
            List of events with matching correlation ID, ordered by timestamp
        """
        events = [e for e in self._in_memory_chain if e.correlation_id == correlation_id]

        logger.info(f"Found {len(events)} events for correlation_id={correlation_id}")

        return events


class ComplianceReportGenerator:
    """
    Generate formatted compliance reports for various frameworks.

    Supports SOX 404, ISO 27001, SOC 2, and GDPR reporting requirements.
    """

    def __init__(self, audit_trail: AuditTrail):
        """
        Initialize report generator.

        Args:
            audit_trail: AuditTrail instance to query
        """
        self.audit_trail = audit_trail
        logger.info("ComplianceReportGenerator initialized")

    def generate_sox_404_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Generate SOX Section 404 compliance report.

        Focuses on internal controls over financial reporting:
        - Access to financial data
        - Configuration changes
        - PII detection in financial documents

        Args:
            start_date: ISO 8601 start date
            end_date: ISO 8601 end date

        Returns:
            SOX 404 formatted report
        """
        logger.info(f"Generating SOX 404 report: {start_date} to {end_date}")

        report = self.audit_trail.generate_compliance_report(
            start_date=start_date,
            end_date=end_date,
            event_types=[
                EventType.DOCUMENT_INGESTED.value,
                EventType.ACCESS_GRANTED.value,
                EventType.ACCESS_DENIED.value,
                EventType.CONFIGURATION_CHANGED.value,
                EventType.PII_DETECTED.value
            ]
        )

        report["framework"] = "SOX Section 404"
        report["retention_requirement"] = "7 years"

        return report

    def generate_iso_27001_report(
        self,
        control: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Generate ISO 27001 control evidence report.

        Args:
            control: ISO 27001 control ID (e.g., "A.12.4.1" for event logging)
            start_date: ISO 8601 start date
            end_date: ISO 8601 end date

        Returns:
            ISO 27001 formatted report
        """
        logger.info(f"Generating ISO 27001 report for control {control}")

        report = self.audit_trail.generate_compliance_report(
            start_date=start_date,
            end_date=end_date
        )

        report["framework"] = "ISO 27001"
        report["control"] = control

        return report


class VendorRiskAssessment:
    """
    Vendor risk assessment framework for third-party AI services.

    Evaluates vendors (OpenAI, Pinecone, etc.) against compliance requirements.
    """

    RISK_CRITERIA = {
        "data_residency": "Does vendor guarantee GCC data stays in India/compliant region?",
        "soc2_certified": "Is vendor SOC 2 Type II certified?",
        "gdpr_compliant": "Does vendor comply with GDPR (if EU data involved)?",
        "encryption_at_rest": "Does vendor encrypt data at rest (AES-256)?",
        "encryption_in_transit": "Does vendor use TLS 1.2+ for data in transit?",
        "access_logs": "Does vendor provide detailed access logs?",
        "data_retention": "Does vendor allow configurable retention policies?",
        "data_deletion": "Can you request complete data deletion?",
        "incident_response": "Does vendor have documented incident response SLA?",
        "subprocessor_disclosure": "Does vendor disclose all subprocessors?"
    }

    def __init__(self):
        """Initialize vendor assessment framework."""
        logger.info("VendorRiskAssessment initialized")

    def assess_vendor(
        self,
        vendor_name: str,
        responses: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Assess vendor risk based on compliance criteria.

        Args:
            vendor_name: Name of vendor (e.g., "OpenAI", "Pinecone")
            responses: Dictionary of criterion -> True/False responses

        Returns:
            Assessment report with risk score and recommendations
        """
        logger.info(f"Assessing vendor: {vendor_name}")

        total_criteria = len(self.RISK_CRITERIA)
        passed_criteria = sum(1 for v in responses.values() if v)

        risk_score = (passed_criteria / total_criteria) * 100

        if risk_score >= 90:
            risk_level = "LOW"
            recommendation = "Approved for production use"
        elif risk_score >= 70:
            risk_level = "MEDIUM"
            recommendation = "Approved with monitoring and annual review"
        elif risk_score >= 50:
            risk_level = "HIGH"
            recommendation = "Requires remediation plan before approval"
        else:
            risk_level = "CRITICAL"
            recommendation = "Not approved - find alternative vendor"

        failed_criteria = [k for k, v in responses.items() if not v]

        assessment = {
            "vendor_name": vendor_name,
            "assessment_date": datetime.now(timezone.utc).isoformat(),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "criteria_passed": passed_criteria,
            "criteria_total": total_criteria,
            "failed_criteria": failed_criteria,
            "next_review_date": "Annual review required"
        }

        logger.info(
            f"Vendor {vendor_name} assessed: "
            f"Risk={risk_level}, Score={risk_score:.1f}%"
        )

        return assessment


def generate_correlation_id() -> str:
    """
    Generate a new UUID v4 correlation ID for request tracing.

    Returns:
        UUID v4 string
    """
    return str(uuid.uuid4())


def verify_hash_chain(events: List[AuditEvent]) -> Tuple[bool, str]:
    """
    Standalone hash chain verification function.

    Args:
        events: List of AuditEvent objects to verify

    Returns:
        Tuple of (is_valid, message)
    """
    if not events:
        return True, "No events to verify"

    expected_previous_hash = "0" * 64

    for idx, event in enumerate(events):
        if event.previous_hash != expected_previous_hash:
            return False, f"Chain broken at event {idx}"

        recomputed_hash = event.compute_hash()
        if recomputed_hash != event.current_hash:
            return False, f"Hash mismatch at event {idx}"

        expected_previous_hash = event.current_hash

    return True, f"Chain verified: {len(events)} events intact"
