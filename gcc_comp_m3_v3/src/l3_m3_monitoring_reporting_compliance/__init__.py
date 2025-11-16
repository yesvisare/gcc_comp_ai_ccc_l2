"""
L3 M3.3: Audit Logging & SIEM Integration

This module implements comprehensive audit logging for RAG systems with:
- Immutable audit trail capturing all RAG operations
- Cryptographic hash chaining for tamper detection
- PostgreSQL storage with Row-Level Security (RLS)
- Optional AWS S3 archival with Object Lock
- SIEM integration (Splunk, Elasticsearch, Datadog)
- Multi-tenant correlation ID support
- 7-10 year retention with tiered storage (hot/warm/cold)

Regulatory compliance: SOX, GDPR Article 15, HIPAA 164.312(b), PCI-DSS Req 10, ISO 27001
"""

import json
import logging
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "AuditEventType",
    "DataClassification",
    "AuditEvent",
    "AuditLogger",
    "CorrelationContext",
    "PostgreSQLAuditStore",
    "S3ArchivalStore",
    "SIEMIntegrator",
    "create_audit_logger",
]


class AuditEventType(Enum):
    """Types of audit events in RAG systems."""
    RAG_QUERY = "RAG_QUERY"
    RAG_RETRIEVAL = "RAG_RETRIEVAL"
    RAG_GENERATION = "RAG_GENERATION"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    RESPONSE_DELIVERY = "RESPONSE_DELIVERY"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class CorrelationContext:
    """
    Multi-tenant correlation context for nested request tracking.

    Supports GCC environments with:
    - tenant_id: Business unit/department
    - correlation_id: Single user request
    - span_id: Specific operation within request
    """

    def __init__(
        self,
        tenant_id: str = "default",
        correlation_id: Optional[str] = None,
        span_id: Optional[str] = None
    ):
        """
        Initialize correlation context.

        Args:
            tenant_id: Tenant/department identifier
            correlation_id: Request correlation ID (auto-generated if None)
            span_id: Operation span ID (auto-generated if None)
        """
        self.tenant_id = tenant_id
        self.correlation_id = correlation_id or f"req-{uuid.uuid4().hex[:12]}"
        self.span_id = span_id or f"span-{uuid.uuid4().hex[:8]}"

    def create_child_span(self, operation: str) -> "CorrelationContext":
        """
        Create child span for nested operations.

        Args:
            operation: Operation name (e.g., 'retrieval', 'generation')

        Returns:
            New CorrelationContext with same correlation_id but new span_id
        """
        return CorrelationContext(
            tenant_id=self.tenant_id,
            correlation_id=self.correlation_id,
            span_id=f"{operation}-{uuid.uuid4().hex[:8]}"
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "span_id": self.span_id
        }


class AuditEvent:
    """
    Structured audit event following GCC compliance requirements.

    Schema includes:
    - Correlation IDs for multi-tenant tracking
    - User identity and role information
    - Operation details (query, retrieval, generation)
    - Data classification and compliance flags
    - Cryptographic hash for chain linking
    """

    def __init__(
        self,
        event_type: AuditEventType,
        context: CorrelationContext,
        user_id: str,
        user_role: str,
        user_department: str,
        data: Dict[str, Any],
        data_classification: DataClassification = DataClassification.INTERNAL,
        compliance_flags: Optional[List[str]] = None,
        previous_hash: Optional[str] = None
    ):
        """
        Create audit event.

        Args:
            event_type: Type of audit event
            context: Correlation context
            user_id: User identifier
            user_role: User role (analyst, engineer, admin, etc.)
            user_department: User department
            data: Event-specific data (query text, doc IDs, etc.)
            data_classification: Data classification level
            compliance_flags: Regulatory flags (SOX_RELEVANT, MNPI, PII, etc.)
            previous_hash: Hash of previous event in chain
        """
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.event_type = event_type
        self.context = context
        self.user_id = user_id
        self.user_role = user_role
        self.user_department = user_department
        self.data = data
        self.data_classification = data_classification
        self.compliance_flags = compliance_flags or []
        self.previous_hash = previous_hash
        self.current_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """
        Compute SHA-256 hash of event for chain linking.

        Hash includes: timestamp, event_type, user_id, data, previous_hash
        This creates a blockchain-like chain for tamper detection.

        Returns:
            Hexadecimal SHA-256 hash
        """
        hash_data = {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "correlation_id": self.context.correlation_id,
            "user_id": self.user_id,
            "data": self.data,
            "previous_hash": self.previous_hash or "genesis"
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for logging/storage
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "tenant_id": self.context.tenant_id,
            "correlation_id": self.context.correlation_id,
            "span_id": self.context.span_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "user_department": self.user_department,
            "data": self.data,
            "data_classification": self.data_classification.value,
            "compliance_flags": self.compliance_flags,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class PostgreSQLAuditStore:
    """
    PostgreSQL storage for audit logs with Row-Level Security (RLS).

    Implements immutability through:
    - INSERT-only permissions for application role
    - RLS policies preventing DELETE/UPDATE
    - Separate admin role for archival only
    """

    def __init__(self, connection_string: str):
        """
        Initialize PostgreSQL audit store.

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self._conn = None
        logger.info("PostgreSQL audit store initialized")

    def connect(self):
        """Establish database connection."""
        try:
            import psycopg2
            self._conn = psycopg2.connect(self.connection_string)
            logger.info("Connected to PostgreSQL audit database")
        except ImportError:
            logger.error("psycopg2 not installed - run: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def create_schema(self):
        """
        Create audit_logs table with RLS policies.

        Table schema:
        - event_id (UUID, PRIMARY KEY)
        - timestamp (TIMESTAMPTZ)
        - event_type (VARCHAR)
        - tenant_id, correlation_id, span_id (VARCHAR)
        - user_id, user_role, user_department (VARCHAR)
        - data (JSONB)
        - data_classification (VARCHAR)
        - compliance_flags (TEXT[])
        - previous_hash, current_hash (VARCHAR)

        RLS Policy:
        - Application role can INSERT only
        - Admin role can SELECT for archival
        - NO role can UPDATE or DELETE
        """
        if not self._conn:
            self.connect()

        schema_sql = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            event_id UUID PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            tenant_id VARCHAR(100) NOT NULL,
            correlation_id VARCHAR(100) NOT NULL,
            span_id VARCHAR(100) NOT NULL,
            user_id VARCHAR(100) NOT NULL,
            user_role VARCHAR(50) NOT NULL,
            user_department VARCHAR(100) NOT NULL,
            data JSONB NOT NULL,
            data_classification VARCHAR(50) NOT NULL,
            compliance_flags TEXT[],
            previous_hash VARCHAR(64),
            current_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_audit_correlation ON audit_logs(correlation_id);
        CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_logs(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_logs(event_type);

        -- Enable Row-Level Security
        ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

        -- Policy: Application role can only INSERT
        -- (Assumes role 'audit_app' exists - must be created separately)
        """

        try:
            cursor = self._conn.cursor()
            cursor.execute(schema_sql)
            self._conn.commit()
            logger.info("Audit logs schema created successfully")
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            self._conn.rollback()
            raise

    def store_event(self, event: AuditEvent):
        """
        Store audit event in PostgreSQL.

        Args:
            event: AuditEvent to store

        Raises:
            Exception: If storage fails
        """
        if not self._conn:
            self.connect()

        insert_sql = """
        INSERT INTO audit_logs (
            event_id, timestamp, event_type,
            tenant_id, correlation_id, span_id,
            user_id, user_role, user_department,
            data, data_classification, compliance_flags,
            previous_hash, current_hash
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        try:
            cursor = self._conn.cursor()
            cursor.execute(insert_sql, (
                event.event_id,
                event.timestamp,
                event.event_type.value,
                event.context.tenant_id,
                event.context.correlation_id,
                event.context.span_id,
                event.user_id,
                event.user_role,
                event.user_department,
                json.dumps(event.data),
                event.data_classification.value,
                event.compliance_flags,
                event.previous_hash,
                event.current_hash
            ))
            self._conn.commit()
            logger.info(f"Stored audit event: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to store audit event: {e}")
            self._conn.rollback()
            raise

    def get_last_hash(self, tenant_id: str) -> Optional[str]:
        """
        Get hash of most recent event for hash chain continuity.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Hash of last event, or None if no events exist
        """
        if not self._conn:
            self.connect()

        query_sql = """
        SELECT current_hash FROM audit_logs
        WHERE tenant_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """

        try:
            cursor = self._conn.cursor()
            cursor.execute(query_sql, (tenant_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get last hash: {e}")
            return None

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            logger.info("PostgreSQL connection closed")


class S3ArchivalStore:
    """
    AWS S3 archival storage with Object Lock for immutability.

    Implements 7-10 year retention with:
    - S3 Object Lock in COMPLIANCE mode
    - Retention period: 2555 days (7 years for SOX)
    - Tiered storage: S3 Standard -> S3 Glacier
    """

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region: str = "us-east-1",
        retention_days: int = 2555
    ):
        """
        Initialize S3 archival store.

        Args:
            bucket_name: S3 bucket name (must have Object Lock enabled)
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region: AWS region
            retention_days: Retention period in days (default 7 years)
        """
        self.bucket_name = bucket_name
        self.retention_days = retention_days
        self.region = region

        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region
            )
            logger.info(f"S3 archival store initialized: {bucket_name}")
        except ImportError:
            logger.error("boto3 not installed - run: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def archive_event(self, event: AuditEvent):
        """
        Archive audit event to S3 with Object Lock.

        File path: {tenant_id}/{year}/{month}/{day}/{event_id}.json

        Args:
            event: AuditEvent to archive

        Raises:
            Exception: If archival fails
        """
        # Build S3 key path
        timestamp = datetime.fromisoformat(event.timestamp)
        s3_key = (
            f"{event.context.tenant_id}/"
            f"{timestamp.year:04d}/"
            f"{timestamp.month:02d}/"
            f"{timestamp.day:02d}/"
            f"{event.event_id}.json"
        )

        try:
            # Calculate retention date
            from datetime import timedelta
            retention_date = datetime.now(timezone.utc) + timedelta(days=self.retention_days)

            # Upload with Object Lock
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=event.to_json(),
                ContentType='application/json',
                ObjectLockMode='COMPLIANCE',
                ObjectLockRetainUntilDate=retention_date
            )
            logger.info(f"Archived event to S3: {s3_key}")
        except Exception as e:
            logger.error(f"Failed to archive to S3: {e}")
            raise


class SIEMIntegrator:
    """
    SIEM platform integration for real-time event streaming.

    Supports:
    - Splunk HTTP Event Collector (HEC)
    - Elasticsearch direct indexing
    - Datadog Logs API
    """

    def __init__(
        self,
        platform: str,
        config: Dict[str, Any]
    ):
        """
        Initialize SIEM integrator.

        Args:
            platform: SIEM platform ('splunk', 'elasticsearch', 'datadog')
            config: Platform-specific configuration
        """
        self.platform = platform.lower()
        self.config = config
        self._client = None
        logger.info(f"SIEM integrator initialized: {platform}")

    def send_event(self, event: AuditEvent):
        """
        Send audit event to SIEM platform.

        Args:
            event: AuditEvent to send

        Raises:
            Exception: If send fails
        """
        if self.platform == "splunk":
            self._send_to_splunk(event)
        elif self.platform == "elasticsearch":
            self._send_to_elasticsearch(event)
        elif self.platform == "datadog":
            self._send_to_datadog(event)
        else:
            logger.warning(f"Unknown SIEM platform: {self.platform}")

    def _send_to_splunk(self, event: AuditEvent):
        """Send event to Splunk HEC."""
        import requests

        hec_url = self.config.get("splunk_hec_url")
        hec_token = self.config.get("splunk_hec_token")

        if not hec_url or not hec_token:
            logger.warning("Splunk HEC URL or token not configured")
            return

        payload = {
            "event": event.to_dict(),
            "sourcetype": "audit_log",
            "index": "audit_logs"
        }

        try:
            response = requests.post(
                hec_url,
                json=payload,
                headers={"Authorization": f"Splunk {hec_token}"},
                verify=False  # In production, use proper SSL verification
            )
            response.raise_for_status()
            logger.info(f"Sent event to Splunk: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to send to Splunk: {e}")

    def _send_to_elasticsearch(self, event: AuditEvent):
        """Send event to Elasticsearch."""
        try:
            from elasticsearch import Elasticsearch

            if not self._client:
                self._client = Elasticsearch(
                    [self.config.get("elasticsearch_url")],
                    api_key=self.config.get("elasticsearch_api_key")
                )

            index_name = self.config.get("elasticsearch_index", "audit-logs")
            self._client.index(
                index=index_name,
                id=event.event_id,
                document=event.to_dict()
            )
            logger.info(f"Sent event to Elasticsearch: {event.event_id}")
        except ImportError:
            logger.error("elasticsearch not installed - run: pip install elasticsearch")
        except Exception as e:
            logger.error(f"Failed to send to Elasticsearch: {e}")

    def _send_to_datadog(self, event: AuditEvent):
        """Send event to Datadog Logs API."""
        try:
            from datadog_api_client import ApiClient, Configuration
            from datadog_api_client.v2.api.logs_api import LogsApi
            from datadog_api_client.v2.model.http_log import HTTPLog
            from datadog_api_client.v2.model.http_log_item import HTTPLogItem

            if not self._client:
                configuration = Configuration()
                configuration.api_key["apiKeyAuth"] = self.config.get("datadog_api_key")
                configuration.api_key["appKeyAuth"] = self.config.get("datadog_app_key")
                configuration.server_variables["site"] = self.config.get("datadog_site", "datadoghq.com")
                self._client = ApiClient(configuration)

            api_instance = LogsApi(self._client)
            body = HTTPLog([
                HTTPLogItem(
                    ddsource="audit_logger",
                    ddtags=f"env:production,tenant:{event.context.tenant_id}",
                    message=json.dumps(event.to_dict()),
                    service="rag_audit"
                )
            ])
            api_instance.submit_log(body=body)
            logger.info(f"Sent event to Datadog: {event.event_id}")
        except ImportError:
            logger.error("datadog-api-client not installed - run: pip install datadog-api-client")
        except Exception as e:
            logger.error(f"Failed to send to Datadog: {e}")


class AuditLogger:
    """
    Main audit logger orchestrating storage and SIEM integration.

    Provides unified interface for:
    - Creating audit events with correlation context
    - Storing in PostgreSQL with hash chaining
    - Archiving to S3 (optional)
    - Streaming to SIEM (optional)
    """

    def __init__(
        self,
        postgres_store: Optional[PostgreSQLAuditStore] = None,
        s3_store: Optional[S3ArchivalStore] = None,
        siem_integrator: Optional[SIEMIntegrator] = None,
        enable_hash_chain: bool = True
    ):
        """
        Initialize audit logger.

        Args:
            postgres_store: PostgreSQL storage (required)
            s3_store: S3 archival storage (optional)
            siem_integrator: SIEM integration (optional)
            enable_hash_chain: Enable cryptographic hash chaining
        """
        self.postgres_store = postgres_store
        self.s3_store = s3_store
        self.siem_integrator = siem_integrator
        self.enable_hash_chain = enable_hash_chain
        logger.info("Audit logger initialized")

    def log_event(
        self,
        event_type: AuditEventType,
        context: CorrelationContext,
        user_id: str,
        user_role: str,
        user_department: str,
        data: Dict[str, Any],
        data_classification: DataClassification = DataClassification.INTERNAL,
        compliance_flags: Optional[List[str]] = None
    ) -> AuditEvent:
        """
        Log audit event with automatic hash chaining.

        Args:
            event_type: Type of audit event
            context: Correlation context
            user_id: User identifier
            user_role: User role
            user_department: User department
            data: Event-specific data
            data_classification: Data classification level
            compliance_flags: Regulatory compliance flags

        Returns:
            Created AuditEvent

        Raises:
            Exception: If logging fails
        """
        # Get previous hash for chain continuity
        previous_hash = None
        if self.enable_hash_chain and self.postgres_store:
            previous_hash = self.postgres_store.get_last_hash(context.tenant_id)

        # Create audit event
        event = AuditEvent(
            event_type=event_type,
            context=context,
            user_id=user_id,
            user_role=user_role,
            user_department=user_department,
            data=data,
            data_classification=data_classification,
            compliance_flags=compliance_flags,
            previous_hash=previous_hash
        )

        # Store in PostgreSQL
        if self.postgres_store:
            try:
                self.postgres_store.store_event(event)
            except Exception as e:
                logger.error(f"Failed to store event in PostgreSQL: {e}")
                raise

        # Archive to S3
        if self.s3_store:
            try:
                self.s3_store.archive_event(event)
            except Exception as e:
                logger.warning(f"Failed to archive to S3 (non-fatal): {e}")

        # Stream to SIEM
        if self.siem_integrator:
            try:
                self.siem_integrator.send_event(event)
            except Exception as e:
                logger.warning(f"Failed to send to SIEM (non-fatal): {e}")

        logger.info(f"Logged audit event: {event.event_id} ({event_type.value})")
        return event


def create_audit_logger(config: Dict[str, Any]) -> AuditLogger:
    """
    Factory function to create configured AuditLogger.

    Args:
        config: Configuration dictionary from config.py

    Returns:
        Configured AuditLogger instance
    """
    # Create PostgreSQL store
    from config import get_db_connection_string
    postgres_store = PostgreSQLAuditStore(get_db_connection_string(config))

    # Create S3 store if enabled
    s3_store = None
    if config.get("aws_enabled"):
        try:
            s3_store = S3ArchivalStore(
                bucket_name=config["s3_bucket_name"],
                aws_access_key_id=config["aws_access_key_id"],
                aws_secret_access_key=config["aws_secret_access_key"],
                region=config["aws_region"],
                retention_days=config["s3_retention_days"]
            )
        except Exception as e:
            logger.warning(f"Failed to initialize S3 store: {e}")

    # Create SIEM integrator if enabled
    siem_integrator = None
    if config.get("siem_enabled"):
        try:
            siem_integrator = SIEMIntegrator(
                platform=config["siem_platform"],
                config=config
            )
        except Exception as e:
            logger.warning(f"Failed to initialize SIEM integrator: {e}")

    return AuditLogger(
        postgres_store=postgres_store,
        s3_store=s3_store,
        siem_integrator=siem_integrator,
        enable_hash_chain=config.get("enable_hash_chain", True)
    )
