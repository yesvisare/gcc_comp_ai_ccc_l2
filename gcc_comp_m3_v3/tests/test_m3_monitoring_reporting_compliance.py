"""
Tests for L3 M3.3: Audit Logging & SIEM Integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.l3_m3_monitoring_reporting_compliance import (
    AuditEventType,
    DataClassification,
    AuditEvent,
    CorrelationContext,
    PostgreSQLAuditStore,
    S3ArchivalStore,
    SIEMIntegrator,
    AuditLogger,
    create_audit_logger,
)


class TestCorrelationContext:
    """Test correlation context for multi-tenant tracking."""

    def test_create_context_with_defaults(self):
        """Test creating context with auto-generated IDs."""
        context = CorrelationContext(tenant_id="finance")

        assert context.tenant_id == "finance"
        assert context.correlation_id.startswith("req-")
        assert context.span_id.startswith("span-")

    def test_create_context_with_custom_ids(self):
        """Test creating context with custom IDs."""
        context = CorrelationContext(
            tenant_id="hr",
            correlation_id="req-custom-123",
            span_id="span-custom-456"
        )

        assert context.tenant_id == "hr"
        assert context.correlation_id == "req-custom-123"
        assert context.span_id == "span-custom-456"

    def test_create_child_span(self):
        """Test creating child span with same correlation ID."""
        parent = CorrelationContext(tenant_id="finance", correlation_id="req-abc")
        child = parent.create_child_span("retrieval")

        assert child.tenant_id == parent.tenant_id
        assert child.correlation_id == parent.correlation_id
        assert child.span_id != parent.span_id
        assert child.span_id.startswith("retrieval-")

    def test_to_dict(self):
        """Test dictionary conversion."""
        context = CorrelationContext(
            tenant_id="finance",
            correlation_id="req-123",
            span_id="span-456"
        )

        result = context.to_dict()

        assert result["tenant_id"] == "finance"
        assert result["correlation_id"] == "req-123"
        assert result["span_id"] == "span-456"


class TestAuditEvent:
    """Test audit event creation and hashing."""

    def test_create_audit_event(self):
        """Test creating audit event with all fields."""
        context = CorrelationContext(tenant_id="finance")

        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test query"},
            data_classification=DataClassification.CONFIDENTIAL,
            compliance_flags=["SOX_RELEVANT"]
        )

        assert event.event_type == AuditEventType.RAG_QUERY
        assert event.user_id == "emp-1234"
        assert event.user_role == "analyst"
        assert event.data["query"] == "test query"
        assert event.data_classification == DataClassification.CONFIDENTIAL
        assert "SOX_RELEVANT" in event.compliance_flags
        assert event.current_hash is not None
        assert len(event.current_hash) == 64  # SHA-256 hex length

    def test_hash_chaining(self):
        """Test cryptographic hash chaining."""
        context = CorrelationContext(tenant_id="finance")

        event1 = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "first query"}
        )

        event2 = AuditEvent(
            event_type=AuditEventType.RAG_RETRIEVAL,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"doc_ids": ["doc-1", "doc-2"]},
            previous_hash=event1.current_hash
        )

        assert event1.previous_hash is None
        assert event2.previous_hash == event1.current_hash
        assert event2.current_hash != event1.current_hash

    def test_to_dict(self):
        """Test dictionary conversion."""
        context = CorrelationContext(tenant_id="finance", correlation_id="req-123")

        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        result = event.to_dict()

        assert result["event_type"] == "RAG_QUERY"
        assert result["tenant_id"] == "finance"
        assert result["correlation_id"] == "req-123"
        assert result["user_id"] == "emp-1234"
        assert result["data"]["query"] == "test"

    def test_to_json(self):
        """Test JSON serialization."""
        context = CorrelationContext(tenant_id="finance")

        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["event_type"] == "RAG_QUERY"
        assert parsed["user_id"] == "emp-1234"


class TestPostgreSQLAuditStore:
    """Test PostgreSQL audit storage."""

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect):
        """Test database connection."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        store = PostgreSQLAuditStore("host=localhost dbname=test")
        store.connect()

        mock_connect.assert_called_once_with("host=localhost dbname=test")
        assert store._conn == mock_conn

    @patch('psycopg2.connect')
    def test_create_schema(self, mock_connect):
        """Test schema creation."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        store = PostgreSQLAuditStore("host=localhost dbname=test")
        store.create_schema()

        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_store_event(self, mock_connect):
        """Test storing audit event."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        store = PostgreSQLAuditStore("host=localhost dbname=test")
        store.connect()

        context = CorrelationContext(tenant_id="finance")
        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        store.store_event(event)

        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_get_last_hash(self, mock_connect):
        """Test retrieving last hash for chain continuity."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("abc123hash",)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        store = PostgreSQLAuditStore("host=localhost dbname=test")
        store.connect()

        last_hash = store.get_last_hash("finance")

        assert last_hash == "abc123hash"
        mock_cursor.execute.assert_called()


class TestS3ArchivalStore:
    """Test S3 archival storage."""

    @patch('boto3.client')
    def test_initialization(self, mock_boto_client):
        """Test S3 client initialization."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        store = S3ArchivalStore(
            bucket_name="audit-logs",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region="us-east-1",
            retention_days=2555
        )

        assert store.bucket_name == "audit-logs"
        assert store.retention_days == 2555
        mock_boto_client.assert_called_once()

    @patch('boto3.client')
    def test_archive_event(self, mock_boto_client):
        """Test archiving event to S3."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        store = S3ArchivalStore(
            bucket_name="audit-logs",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret"
        )

        context = CorrelationContext(tenant_id="finance")
        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        store.archive_event(event)

        mock_s3.put_object.assert_called_once()
        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs['Bucket'] == "audit-logs"
        assert call_kwargs['ObjectLockMode'] == 'COMPLIANCE'


class TestSIEMIntegrator:
    """Test SIEM platform integration."""

    def test_initialization(self):
        """Test SIEM integrator initialization."""
        integrator = SIEMIntegrator(
            platform="splunk",
            config={"splunk_hec_url": "https://splunk:8088"}
        )

        assert integrator.platform == "splunk"
        assert integrator.config["splunk_hec_url"] == "https://splunk:8088"

    @patch('requests.post')
    def test_send_to_splunk(self, mock_post):
        """Test sending event to Splunk HEC."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        integrator = SIEMIntegrator(
            platform="splunk",
            config={
                "splunk_hec_url": "https://splunk:8088/services/collector",
                "splunk_hec_token": "test-token"
            }
        )

        context = CorrelationContext(tenant_id="finance")
        event = AuditEvent(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        integrator.send_event(event)

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert "Authorization" in call_kwargs['headers']


class TestAuditLogger:
    """Test main audit logger orchestration."""

    def test_initialization(self):
        """Test audit logger initialization."""
        postgres_store = Mock(spec=PostgreSQLAuditStore)
        s3_store = Mock(spec=S3ArchivalStore)
        siem_integrator = Mock(spec=SIEMIntegrator)

        logger = AuditLogger(
            postgres_store=postgres_store,
            s3_store=s3_store,
            siem_integrator=siem_integrator,
            enable_hash_chain=True
        )

        assert logger.postgres_store == postgres_store
        assert logger.s3_store == s3_store
        assert logger.siem_integrator == siem_integrator
        assert logger.enable_hash_chain is True

    def test_log_event_to_postgres(self):
        """Test logging event to PostgreSQL."""
        postgres_store = Mock(spec=PostgreSQLAuditStore)
        postgres_store.get_last_hash.return_value = None

        logger = AuditLogger(postgres_store=postgres_store)

        context = CorrelationContext(tenant_id="finance")
        event = logger.log_event(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test query"}
        )

        assert event is not None
        postgres_store.store_event.assert_called_once()

    def test_log_event_with_all_integrations(self):
        """Test logging event with PostgreSQL, S3, and SIEM."""
        postgres_store = Mock(spec=PostgreSQLAuditStore)
        postgres_store.get_last_hash.return_value = "prev-hash-123"
        s3_store = Mock(spec=S3ArchivalStore)
        siem_integrator = Mock(spec=SIEMIntegrator)

        logger = AuditLogger(
            postgres_store=postgres_store,
            s3_store=s3_store,
            siem_integrator=siem_integrator,
            enable_hash_chain=True
        )

        context = CorrelationContext(tenant_id="finance")
        event = logger.log_event(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test query"},
            data_classification=DataClassification.CONFIDENTIAL,
            compliance_flags=["SOX_RELEVANT", "PII"]
        )

        assert event.previous_hash == "prev-hash-123"
        postgres_store.store_event.assert_called_once()
        s3_store.archive_event.assert_called_once()
        siem_integrator.send_event.assert_called_once()

    def test_log_event_continues_on_s3_failure(self):
        """Test that S3 failure doesn't break logging."""
        postgres_store = Mock(spec=PostgreSQLAuditStore)
        postgres_store.get_last_hash.return_value = None
        s3_store = Mock(spec=S3ArchivalStore)
        s3_store.archive_event.side_effect = Exception("S3 error")

        logger = AuditLogger(
            postgres_store=postgres_store,
            s3_store=s3_store
        )

        context = CorrelationContext(tenant_id="finance")
        # Should not raise exception even though S3 fails
        event = logger.log_event(
            event_type=AuditEventType.RAG_QUERY,
            context=context,
            user_id="emp-1234",
            user_role="analyst",
            user_department="finance",
            data={"query": "test"}
        )

        assert event is not None
        postgres_store.store_event.assert_called_once()


class TestCreateAuditLogger:
    """Test factory function for creating audit logger."""

    @patch('src.l3_m3_monitoring_reporting_compliance.PostgreSQLAuditStore')
    def test_create_logger_minimal_config(self, mock_postgres_class):
        """Test creating logger with minimal configuration."""
        config = {
            "db_host": "localhost",
            "db_port": 5432,
            "db_name": "audit_logs",
            "db_user": "audit_user",
            "db_password": "password",
            "aws_enabled": False,
            "siem_enabled": False,
            "enable_hash_chain": True
        }

        logger = create_audit_logger(config)

        assert logger is not None
        assert logger.postgres_store is not None
        assert logger.s3_store is None
        assert logger.siem_integrator is None


# Parametrized tests for comprehensive coverage

@pytest.mark.parametrize("event_type,expected_value", [
    (AuditEventType.RAG_QUERY, "RAG_QUERY"),
    (AuditEventType.RAG_RETRIEVAL, "RAG_RETRIEVAL"),
    (AuditEventType.RAG_GENERATION, "RAG_GENERATION"),
    (AuditEventType.ACCESS_CONTROL, "ACCESS_CONTROL"),
    (AuditEventType.ERROR, "ERROR"),
])
def test_audit_event_types(event_type, expected_value):
    """Test all audit event types."""
    assert event_type.value == expected_value


@pytest.mark.parametrize("classification,expected_value", [
    (DataClassification.PUBLIC, "PUBLIC"),
    (DataClassification.INTERNAL, "INTERNAL"),
    (DataClassification.CONFIDENTIAL, "CONFIDENTIAL"),
    (DataClassification.RESTRICTED, "RESTRICTED"),
])
def test_data_classifications(classification, expected_value):
    """Test all data classification levels."""
    assert classification.value == expected_value


# Integration-style tests (require mocking)

def test_full_audit_workflow():
    """Test complete audit logging workflow."""
    # Create mocked components
    postgres_store = Mock(spec=PostgreSQLAuditStore)
    postgres_store.get_last_hash.return_value = None

    logger = AuditLogger(postgres_store=postgres_store)

    # Simulate RAG query workflow
    context = CorrelationContext(tenant_id="finance", correlation_id="req-workflow-1")

    # 1. Log query
    query_event = logger.log_event(
        event_type=AuditEventType.RAG_QUERY,
        context=context,
        user_id="emp-1234",
        user_role="analyst",
        user_department="finance",
        data={"query": "What were Q4 earnings?"}
    )

    # 2. Log retrieval
    retrieval_context = context.create_child_span("retrieval")
    retrieval_event = logger.log_event(
        event_type=AuditEventType.RAG_RETRIEVAL,
        context=retrieval_context,
        user_id="emp-1234",
        user_role="analyst",
        user_department="finance",
        data={"doc_ids": ["doc-991", "doc-992"], "scores": [0.95, 0.87]}
    )

    # 3. Log generation
    generation_context = context.create_child_span("generation")
    generation_event = logger.log_event(
        event_type=AuditEventType.RAG_GENERATION,
        context=generation_context,
        user_id="emp-1234",
        user_role="analyst",
        user_department="finance",
        data={"model": "gpt-4", "tokens": 250}
    )

    # Verify all events share same correlation ID
    assert query_event.context.correlation_id == "req-workflow-1"
    assert retrieval_event.context.correlation_id == "req-workflow-1"
    assert generation_event.context.correlation_id == "req-workflow-1"

    # Verify 3 events were logged
    assert postgres_store.store_event.call_count == 3
