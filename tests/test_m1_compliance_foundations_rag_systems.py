"""
Test suite for L3 M1.2: Data Governance Requirements for RAG

Tests all major functions and edge cases from the augmented script:
- Data classification (Component 1)
- Lineage tracking (Component 2)
- Retention policies (Component 3)
- Data residency (Component 4)
- Consent management (Component 5)
- GDPR Article 17 erasure (Component 6)
"""

import pytest
from datetime import datetime, timedelta

from src.l3_m1_compliance_foundations_rag_systems import (
    DataClassifier,
    LineageTracker,
    RetentionEngine,
    ResidencyController,
    ConsentManager,
    GDPRErasureWorkflow,
    DataType,
    Region,
    SensitivityLevel
)


# ============================================================================
# COMPONENT 1: DATA CLASSIFICATION TESTS
# ============================================================================

class TestDataClassifier:
    """Test suite for DataClassifier component."""

    def test_classifier_initialization(self):
        """Test DataClassifier initialization."""
        classifier = DataClassifier(enable_presidio=False)
        assert classifier is not None
        assert classifier.enable_presidio == False

    def test_classify_public_document(self):
        """Test classification of public document."""
        classifier = DataClassifier(enable_presidio=False)
        text = "This is a public announcement about company policies."

        result = classifier.classify_document(text)

        assert result["sensitivity_level"] == SensitivityLevel.PUBLIC.value
        assert result["retention_period_days"] == -1  # Indefinite
        assert result["requires_encryption"] == False

    def test_classify_pii_document(self):
        """Test classification of document with PII patterns."""
        classifier = DataClassifier(enable_presidio=False)
        text = "Employee Jane Smith submitted expense report for account number 123456."

        result = classifier.classify_document(text)

        # Should detect financial patterns
        assert DataType.FINANCIAL.value in result["data_types"]
        assert result["requires_encryption"] == True

    def test_classify_financial_document(self):
        """Test classification of financial document."""
        classifier = DataClassifier(enable_presidio=False)
        text = "Invoice #12345: Payment of $50,000 for Q4 2024 services."

        result = classifier.classify_document(text, {"document_type": "financial_statement"})

        assert DataType.FINANCIAL.value in result["data_types"]
        assert result["retention_period_days"] == 3650  # 10 years (SOX)
        assert result["sensitivity_level"] == SensitivityLevel.CONFIDENTIAL.value

    def test_classify_medical_document(self):
        """Test classification of medical document."""
        classifier = DataClassifier(enable_presidio=False)
        text = "Patient diagnosis: Type 2 diabetes. Prescribed medication: Metformin 500mg."

        result = classifier.classify_document(text, {"document_type": "medical_record"})

        assert DataType.PHI.value in result["data_types"]
        assert result["retention_period_days"] == 2555  # 7 years (HIPAA)
        assert result["sensitivity_level"] == SensitivityLevel.RESTRICTED.value
        assert "healthcare_compliance" in result["access_groups"]

    def test_retention_period_hr_records(self):
        """Test retention period calculation for HR records."""
        classifier = DataClassifier(enable_presidio=False)
        text = "Employee termination notice."

        result = classifier.classify_document(text, {"document_type": "hr_records"})

        assert result["retention_period_days"] == 2555  # 7 years (FLSA)


# ============================================================================
# COMPONENT 2: LINEAGE TRACKING TESTS
# ============================================================================

class TestLineageTracker:
    """Test suite for LineageTracker component."""

    def test_tracker_initialization(self):
        """Test LineageTracker initialization."""
        tracker = LineageTracker()
        assert tracker is not None
        assert isinstance(tracker.audit_store, dict)

    def test_track_document_upload(self):
        """Test tracking document upload (Stage 1)."""
        tracker = LineageTracker()
        source_id = "doc_001"
        metadata = {"filename": "policy.pdf", "size": 102400}

        record_id = tracker.track_document_upload(source_id, metadata)

        assert record_id.startswith("lineage_")
        assert source_id in tracker.audit_store[record_id]["source_id"]
        assert tracker.audit_store[record_id]["stage"] == "document_upload"

    def test_track_chunking(self):
        """Test tracking document chunking (Stage 2)."""
        tracker = LineageTracker()
        source_id = "doc_001"
        chunk_ids = ["chunk_001", "chunk_002", "chunk_003"]

        record_ids = tracker.track_chunking(source_id, chunk_ids)

        assert len(record_ids) == 3
        for record_id in record_ids:
            assert tracker.audit_store[record_id]["stage"] == "chunking"

    def test_track_embedding(self):
        """Test tracking embedding generation (Stage 3)."""
        tracker = LineageTracker()
        chunk_id = "chunk_001"
        embedding_id = "emb_001"

        record_id = tracker.track_embedding(chunk_id, embedding_id)

        assert tracker.audit_store[record_id]["embedding_id"] == embedding_id
        assert tracker.audit_store[record_id]["stage"] == "embedding"
        assert tracker.audit_store[record_id]["model"] == "text-embedding-ada-002"

    def test_track_full_lineage_chain(self):
        """Test tracking complete lineage chain across all stages."""
        tracker = LineageTracker()
        source_id = "doc_001"

        # Stage 1: Document upload
        tracker.track_document_upload(source_id, {"filename": "test.pdf"})

        # Stage 2: Chunking
        chunk_ids = ["chunk_001", "chunk_002"]
        tracker.track_chunking(source_id, chunk_ids)

        # Stage 3: Embeddings
        tracker.track_embedding("chunk_001", "emb_001")
        tracker.track_embedding("chunk_002", "emb_002")

        # Stage 4: Vector storage
        tracker.track_vector_storage("emb_001", "vec_001")

        # Stage 5: Retrieval
        tracker.track_retrieval("query_001", ["chunk_001"], "user_123")

        # Stage 6: Generation
        tracker.track_generation("query_001", "gen_001")

        # Stage 7: Caching
        tracker.track_caching("query_001", "cache_key_001")

        # Get full lineage
        lineage = tracker.get_full_lineage(source_id)

        assert len(lineage) >= 3  # At least document upload + 2 chunks


# ============================================================================
# COMPONENT 3: RETENTION POLICY TESTS
# ============================================================================

class TestRetentionEngine:
    """Test suite for RetentionEngine component."""

    def test_engine_initialization(self):
        """Test RetentionEngine initialization."""
        tracker = LineageTracker()
        engine = RetentionEngine(tracker)

        assert engine is not None
        assert engine.lineage_tracker == tracker

    def test_check_retention_compliance_within_period(self):
        """Test retention compliance check for document within retention period."""
        tracker = LineageTracker()
        engine = RetentionEngine(tracker)

        source_id = "doc_001"
        tracker.track_document_upload(source_id, {"filename": "recent.pdf"})

        classification = {"retention_period_days": 1095}  # 3 years
        result = engine.check_retention_compliance(source_id, classification)

        assert result["compliant"] == True
        assert result["action"] == "retain"

    def test_check_retention_compliance_indefinite(self):
        """Test retention compliance for indefinite retention."""
        tracker = LineageTracker()
        engine = RetentionEngine(tracker)

        source_id = "doc_002"
        tracker.track_document_upload(source_id, {"filename": "public.pdf"})

        classification = {"retention_period_days": -1}  # Indefinite
        result = engine.check_retention_compliance(source_id, classification)

        assert result["compliant"] == True
        assert result["action"] == "retain_indefinitely"

    def test_execute_retention_deletion(self):
        """Test retention-based deletion across all systems."""
        tracker = LineageTracker()
        engine = RetentionEngine(tracker)

        source_id = "doc_003"
        tracker.track_document_upload(source_id, {"filename": "old.pdf"})
        tracker.track_chunking(source_id, ["chunk_001"])
        tracker.track_embedding("chunk_001", "emb_001")
        tracker.track_vector_storage("emb_001", "vec_001")

        result = engine.execute_retention_deletion(source_id)

        assert result["source_id"] == source_id
        assert "systems_deleted" in result
        assert len(result["systems_deleted"]) > 0

    def test_schedule_retention_job(self):
        """Test scheduling Airflow retention job."""
        tracker = LineageTracker()
        engine = RetentionEngine(tracker)

        job_config = engine.schedule_retention_job("hr_records", "0 2 * * *")

        assert job_config["retention_policy"] == "hr_records"
        assert job_config["retention_days"] == 2555  # 7 years
        assert job_config["cron_schedule"] == "0 2 * * *"
        assert job_config["status"] == "scheduled"


# ============================================================================
# COMPONENT 4: DATA RESIDENCY TESTS
# ============================================================================

class TestResidencyController:
    """Test suite for ResidencyController component."""

    def test_controller_initialization(self):
        """Test ResidencyController initialization."""
        controller = ResidencyController()
        assert controller is not None

    def test_validate_residency_eu_to_eu(self):
        """Test validation of EU data staying in EU (compliant)."""
        controller = ResidencyController()

        result = controller.validate_residency(Region.EU, Region.EU)

        assert result["compliant"] == True
        assert result["action"] == "allow"
        assert result["regulation"] == "GDPR Article 44"

    def test_validate_residency_eu_to_us(self):
        """Test validation of EU data to US (non-compliant)."""
        controller = ResidencyController()

        result = controller.validate_residency(Region.EU, Region.US)

        assert result["compliant"] == False
        assert result["action"] == "block"

    def test_validate_residency_india_to_india(self):
        """Test validation of India data staying in India (compliant)."""
        controller = ResidencyController()

        result = controller.validate_residency(Region.INDIA, Region.INDIA)

        assert result["compliant"] == True
        assert result["regulation"] == "DPDPA 2023"

    def test_route_to_compliant_region_eu(self):
        """Test routing EU user data to EU region."""
        controller = ResidencyController()
        classification = {"sensitivity_level": "confidential"}

        region = controller.route_to_compliant_region("DE", classification)

        assert region == Region.EU

    def test_route_to_compliant_region_india(self):
        """Test routing India user data to India region."""
        controller = ResidencyController()
        classification = {"sensitivity_level": "confidential"}

        region = controller.route_to_compliant_region("IN", classification)

        assert region == Region.INDIA

    def test_enforce_cross_border_restrictions_eu_to_us(self):
        """Test cross-border transfer restrictions for EU to US."""
        controller = ResidencyController()

        result = controller.enforce_cross_border_restrictions(Region.EU, Region.US)

        assert result["allowed"] == False
        assert "Standard Contractual Clauses" in result["required_mechanism"]


# ============================================================================
# COMPONENT 5: CONSENT MANAGEMENT TESTS
# ============================================================================

class TestConsentManager:
    """Test suite for ConsentManager component."""

    def test_manager_initialization(self):
        """Test ConsentManager initialization."""
        manager = ConsentManager()
        assert manager is not None
        assert isinstance(manager.consent_store, dict)

    def test_grant_consent(self):
        """Test granting user consent."""
        manager = ConsentManager()

        consent = manager.grant_consent(
            user_id="user_001",
            data_type=DataType.PII,
            purpose="RAG query processing",
            legal_basis="consent"
        )

        assert consent["user_id"] == "user_001"
        assert consent["data_type"] == DataType.PII.value
        assert consent["purpose"] == "RAG query processing"
        assert consent["status"] == "active"

    def test_revoke_consent(self):
        """Test revoking user consent (GDPR Article 7(3))."""
        manager = ConsentManager()

        # Grant consent first
        manager.grant_consent("user_001", DataType.PII, "RAG processing")

        # Revoke consent
        result = manager.revoke_consent("user_001", DataType.PII)

        assert result["user_id"] == "user_001"
        assert result["revoked_count"] >= 1

    def test_check_consent_valid(self):
        """Test checking valid consent."""
        manager = ConsentManager()

        manager.grant_consent("user_001", DataType.PII, "analytics")

        has_consent = manager.check_consent("user_001", DataType.PII, "analytics")

        assert has_consent == True

    def test_check_consent_invalid_purpose(self):
        """Test checking consent for different purpose (should fail)."""
        manager = ConsentManager()

        manager.grant_consent("user_001", DataType.PII, "analytics")

        has_consent = manager.check_consent("user_001", DataType.PII, "marketing")

        assert has_consent == False

    def test_get_user_consents(self):
        """Test retrieving all user consents (GDPR Article 15)."""
        manager = ConsentManager()

        manager.grant_consent("user_001", DataType.PII, "analytics")
        manager.grant_consent("user_001", DataType.FINANCIAL, "reporting")

        consents = manager.get_user_consents("user_001")

        assert len(consents) == 2


# ============================================================================
# COMPONENT 6: GDPR ARTICLE 17 ERASURE TESTS
# ============================================================================

class TestGDPRErasureWorkflow:
    """Test suite for GDPRErasureWorkflow component."""

    def test_workflow_initialization(self):
        """Test GDPRErasureWorkflow initialization."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        assert workflow is not None

    def test_validate_erasure_request_approved(self):
        """Test validation of erasure request (approved)."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        validation = workflow.validate_erasure_request(
            user_id="user_001",
            request_reason="I want my data deleted"
        )

        assert validation["validated"] == True
        assert validation["approval_status"] == "approved"

    def test_validate_erasure_request_denied_legal_exception(self):
        """Test validation with legal exception (denied)."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        validation = workflow.validate_erasure_request(
            user_id="user_001",
            request_reason="Delete data but active legal_claim pending"
        )

        assert validation["validated"] == False
        assert validation["approval_status"] == "denied"
        assert len(validation["exceptions"]) > 0

    def test_execute_erasure(self):
        """Test executing complete erasure across all systems."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        # Grant some consents first
        consent_manager.grant_consent("user_001", DataType.PII, "analytics")

        # Execute erasure
        report = workflow.execute_erasure("user_001")

        assert report["user_id"] == "user_001"
        assert report["completion_status"] == "completed"
        assert len(report["systems_processed"]) > 0

    def test_verify_erasure(self):
        """Test verification of complete erasure."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        # Execute erasure first
        workflow.execute_erasure("user_001")

        # Verify erasure
        verification = workflow.verify_erasure("user_001")

        assert verification["user_id"] == "user_001"
        assert verification["verification_status"] == "passed"
        assert len(verification["systems_checked"]) > 0

    def test_generate_deletion_certificate(self):
        """Test generation of deletion certificate for GDPR compliance."""
        tracker = LineageTracker()
        consent_manager = ConsentManager()
        retention_engine = RetentionEngine(tracker)
        workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        erasure_report = {
            "user_id": "user_001",
            "erasure_timestamp": datetime.utcnow().isoformat(),
            "systems_processed": [
                {"system": "Vector Database", "status": "deleted"},
                {"system": "Document Store", "status": "deleted"}
            ],
            "total_records_deleted": 2,
            "completion_status": "completed"
        }

        certificate = workflow.generate_deletion_certificate("user_001", erasure_report)

        assert "GDPR ARTICLE 17 DELETION CERTIFICATE" in certificate
        assert "user_001" in certificate
        assert "Vector Database" in certificate


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests across multiple components."""

    def test_end_to_end_governance_workflow(self):
        """Test complete governance workflow from classification to erasure."""
        # Initialize all components
        classifier = DataClassifier(enable_presidio=False)
        tracker = LineageTracker()
        retention_engine = RetentionEngine(tracker)
        residency_controller = ResidencyController()
        consent_manager = ConsentManager()
        erasure_workflow = GDPRErasureWorkflow(tracker, consent_manager, retention_engine)

        # Step 1: Classify document
        text = "Employee Jane Smith submitted expense report."
        classification = classifier.classify_document(text, {"document_type": "hr_records"})
        assert DataType.FINANCIAL.value in classification["data_types"]

        # Step 2: Track lineage
        source_id = "doc_e2e_001"
        tracker.track_document_upload(source_id, {"filename": "expense.pdf"})
        tracker.track_chunking(source_id, ["chunk_001"])

        # Step 3: Check residency
        validation = residency_controller.validate_residency(Region.EU, Region.EU)
        assert validation["compliant"] == True

        # Step 4: Grant consent
        consent = consent_manager.grant_consent("user_001", DataType.PII, "HR processing")
        assert consent["status"] == "active"

        # Step 5: Check retention
        compliance = retention_engine.check_retention_compliance(source_id, classification)
        assert "compliant" in compliance

        # Step 6: Execute erasure
        report = erasure_workflow.execute_erasure("user_001")
        assert report["completion_status"] == "completed"

    def test_cross_region_data_flow_with_consent(self):
        """Test cross-region data flow with proper consent and residency checks."""
        residency_controller = ResidencyController()
        consent_manager = ConsentManager()

        # Grant consent for cross-border transfer
        consent_manager.grant_consent(
            "user_002",
            DataType.PII,
            "cross_region_analytics",
            legal_basis="consent"
        )

        # Check consent before transfer
        has_consent = consent_manager.check_consent("user_002", DataType.PII, "cross_region_analytics")
        assert has_consent == True

        # Validate residency (should fail without SCCs)
        validation = residency_controller.validate_residency(Region.EU, Region.US)
        assert validation["compliant"] == False
