"""
FastAPI application for L3_M1 Compliance Foundations RAG Systems.
Provides REST API endpoints for data governance operations:
- Data classification and PII detection
- Lineage tracking across RAG pipeline
- Retention policy management
- Data residency enforcement
- Consent management
- GDPR Article 17 erasure workflows
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

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
from config import get_service_health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M1.2: Data Governance Requirements for RAG",
    description="Production API for comprehensive data governance in RAG systems (GCC compliance)",
    version="1.0.0"
)

# Initialize components
classifier = DataClassifier(enable_presidio=True)
lineage_tracker = LineageTracker()
retention_engine = RetentionEngine(lineage_tracker)
residency_controller = ResidencyController()
consent_manager = ConsentManager()
erasure_workflow = GDPRErasureWorkflow(lineage_tracker, consent_manager, retention_engine)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ClassifyRequest(BaseModel):
    """Request model for document classification."""
    text: str = Field(..., description="Document text to classify")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class ClassifyResponse(BaseModel):
    """Response model for classification results."""
    sensitivity_level: str
    data_types: List[str]
    pii_entities: List[Dict[str, Any]]
    retention_period_days: int
    requires_encryption: bool
    access_groups: List[str]
    classification_timestamp: str


class LineageRequest(BaseModel):
    """Request model for lineage tracking."""
    source_id: str
    metadata: Dict[str, Any]


class ConsentRequest(BaseModel):
    """Request model for consent management."""
    user_id: str
    data_type: str
    purpose: str
    legal_basis: str = "consent"


class ErasureRequest(BaseModel):
    """Request model for GDPR Article 17 erasure."""
    user_id: str
    request_reason: str = "User requested deletion under GDPR Article 17"


class ResidencyRequest(BaseModel):
    """Request model for data residency validation."""
    data_region: str
    storage_region: str


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "L3_M1_Compliance_Foundations_RAG_Systems",
        "version": "1.0.0",
        "description": "Data governance API for RAG systems in Global Capability Centers",
        "endpoints": {
            "classification": "/classify",
            "lineage": "/lineage/*",
            "retention": "/retention/*",
            "residency": "/residency/*",
            "consent": "/consent/*",
            "erasure": "/erasure/*"
        }
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check with service status."""
    service_health = get_service_health()

    return {
        "api": "healthy",
        "services": service_health,
        "warnings": [
            f"{service} unavailable"
            for service, healthy in service_health.items()
            if not healthy
        ]
    }


# ============================================================================
# DATA CLASSIFICATION ENDPOINTS
# ============================================================================

@app.post("/classify", response_model=ClassifyResponse, tags=["Classification"])
async def classify_document(request: ClassifyRequest):
    """
    Classify document and detect PII/PHI/financial data.

    Uses Presidio for PII detection and pattern matching for additional types.
    Returns sensitivity level, retention period, and access control requirements.
    """
    try:
        result = classifier.classify_document(request.text, request.metadata)
        return ClassifyResponse(**result)
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


# ============================================================================
# LINEAGE TRACKING ENDPOINTS
# ============================================================================

@app.post("/lineage/document", tags=["Lineage"])
async def track_document_upload(request: LineageRequest):
    """Track Stage 1: Source document upload."""
    try:
        record_id = lineage_tracker.track_document_upload(
            request.source_id,
            request.metadata
        )
        return {"record_id": record_id, "stage": "document_upload", "status": "tracked"}
    except Exception as e:
        logger.error(f"Lineage tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/chunks", tags=["Lineage"])
async def track_chunking(source_id: str, chunk_ids: List[str]):
    """Track Stage 2: Document chunking."""
    try:
        record_ids = lineage_tracker.track_chunking(source_id, chunk_ids)
        return {"record_ids": record_ids, "stage": "chunking", "count": len(record_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/embedding", tags=["Lineage"])
async def track_embedding(chunk_id: str, embedding_id: str, model: str = "text-embedding-ada-002"):
    """Track Stage 3: Embedding generation."""
    try:
        record_id = lineage_tracker.track_embedding(chunk_id, embedding_id, model)
        return {"record_id": record_id, "stage": "embedding"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/vector", tags=["Lineage"])
async def track_vector_storage(embedding_id: str, vector_db_id: str, namespace: str = "default"):
    """Track Stage 4: Vector database storage."""
    try:
        record_id = lineage_tracker.track_vector_storage(embedding_id, vector_db_id, namespace)
        return {"record_id": record_id, "stage": "vector_storage"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/retrieval", tags=["Lineage"])
async def track_retrieval(query_id: str, retrieved_chunk_ids: List[str], user_id: str):
    """Track Stage 5: Chunk retrieval."""
    try:
        record_id = lineage_tracker.track_retrieval(query_id, retrieved_chunk_ids, user_id)
        return {"record_id": record_id, "stage": "retrieval"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/generation", tags=["Lineage"])
async def track_generation(query_id: str, generation_id: str, model: str = "gpt-4"):
    """Track Stage 6: LLM answer generation."""
    try:
        record_id = lineage_tracker.track_generation(query_id, generation_id, model)
        return {"record_id": record_id, "stage": "generation"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lineage/cache", tags=["Lineage"])
async def track_caching(query_id: str, cache_key: str, ttl_seconds: int = 86400):
    """Track Stage 7: Response caching."""
    try:
        record_id = lineage_tracker.track_caching(query_id, cache_key, ttl_seconds)
        return {"record_id": record_id, "stage": "caching"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lineage/{source_id}", tags=["Lineage"])
async def get_full_lineage(source_id: str):
    """Retrieve complete lineage chain for a document."""
    try:
        lineage = lineage_tracker.get_full_lineage(source_id)
        return {
            "source_id": source_id,
            "lineage_records": lineage,
            "record_count": len(lineage)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RETENTION POLICY ENDPOINTS
# ============================================================================

@app.get("/retention/check/{source_id}", tags=["Retention"])
async def check_retention(source_id: str):
    """Check if document exceeds retention period."""
    try:
        # First classify the document (in production, retrieve from storage)
        classification = {"retention_period_days": 1095}  # Example

        compliance = retention_engine.check_retention_compliance(source_id, classification)
        return compliance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/retention/{source_id}", tags=["Retention"])
async def execute_retention_deletion(source_id: str):
    """Execute retention-based deletion across all systems."""
    try:
        result = retention_engine.execute_retention_deletion(source_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retention/schedule", tags=["Retention"])
async def schedule_retention_job(retention_policy: str, cron_schedule: str = "0 2 * * *"):
    """Schedule Airflow DAG for automated retention enforcement."""
    try:
        job_config = retention_engine.schedule_retention_job(retention_policy, cron_schedule)
        return job_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DATA RESIDENCY ENDPOINTS
# ============================================================================

@app.post("/residency/validate", tags=["Residency"])
async def validate_residency(request: ResidencyRequest):
    """Validate data residency compliance (GDPR Article 44, DPDPA)."""
    try:
        data_region = Region[request.data_region.upper()]
        storage_region = Region[request.storage_region.upper()]

        result = residency_controller.validate_residency(data_region, storage_region)
        return result
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region. Must be one of: {[r.name for r in Region]}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/residency/route/{country_code}", tags=["Residency"])
async def route_to_region(country_code: str):
    """Route data to compliant region based on country code."""
    try:
        classification = {"sensitivity_level": "confidential"}  # Example
        region = residency_controller.route_to_compliant_region(country_code, classification)
        return {"country_code": country_code, "target_region": region.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONSENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/consent/grant", tags=["Consent"])
async def grant_consent(request: ConsentRequest):
    """Grant user consent for data processing (GDPR Article 6/7)."""
    try:
        data_type = DataType[request.data_type.upper()]
        consent = consent_manager.grant_consent(
            request.user_id,
            data_type,
            request.purpose,
            request.legal_basis
        )
        return consent
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data_type. Must be one of: {[dt.name for dt in DataType]}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/consent/revoke", tags=["Consent"])
async def revoke_consent(user_id: str, data_type: str):
    """Revoke user consent (GDPR Article 7(3))."""
    try:
        data_type_enum = DataType[data_type.upper()]
        result = consent_manager.revoke_consent(user_id, data_type_enum)
        return result
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data_type. Must be one of: {[dt.name for dt in DataType]}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consent/check", tags=["Consent"])
async def check_consent(user_id: str, data_type: str, purpose: str):
    """Check if user has valid consent for specific purpose."""
    try:
        data_type_enum = DataType[data_type.upper()]
        has_consent = consent_manager.check_consent(user_id, data_type_enum, purpose)
        return {"user_id": user_id, "has_consent": has_consent, "purpose": purpose}
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid data_type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consent/{user_id}", tags=["Consent"])
async def get_user_consents(user_id: str):
    """Retrieve all consents for a user (GDPR Article 15)."""
    try:
        consents = consent_manager.get_user_consents(user_id)
        return {"user_id": user_id, "consents": consents, "count": len(consents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GDPR ARTICLE 17 ERASURE ENDPOINTS
# ============================================================================

@app.post("/erasure/validate", tags=["GDPR Erasure"])
async def validate_erasure(request: ErasureRequest):
    """Validate GDPR Article 17 erasure request against legal exceptions."""
    try:
        validation = erasure_workflow.validate_erasure_request(
            request.user_id,
            request.request_reason
        )
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/erasure/{user_id}", tags=["GDPR Erasure"])
async def execute_erasure(user_id: str):
    """Execute complete GDPR Article 17 erasure across all 7 systems."""
    try:
        # First validate
        validation = erasure_workflow.validate_erasure_request(user_id, "User request")

        if not validation["validated"]:
            raise HTTPException(
                status_code=403,
                detail=f"Erasure denied: {validation['exceptions']}"
            )

        # Execute erasure
        erasure_report = erasure_workflow.execute_erasure(user_id)
        return erasure_report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erasure execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/erasure/verify/{user_id}", tags=["GDPR Erasure"])
async def verify_erasure(user_id: str):
    """Verify complete erasure across all systems."""
    try:
        verification = erasure_workflow.verify_erasure(user_id)
        return verification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/erasure/certificate/{user_id}", response_class=PlainTextResponse, tags=["GDPR Erasure"])
async def get_deletion_certificate(user_id: str):
    """Generate deletion certificate for GDPR compliance proof."""
    try:
        # Get erasure report (in production, retrieve from database)
        erasure_report = {
            "user_id": user_id,
            "erasure_timestamp": "2025-01-01T00:00:00",
            "systems_processed": [],
            "total_records_deleted": 0,
            "completion_status": "completed"
        }

        certificate = erasure_workflow.generate_deletion_certificate(user_id, erasure_report)
        return certificate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log service initialization on startup."""
    logger.info("=" * 70)
    logger.info("L3 M1.2: Data Governance Requirements for RAG - API Started")
    logger.info("=" * 70)

    service_health = get_service_health()
    for service, healthy in service_health.items():
        status_icon = "✅" if healthy else "⚠️"
        logger.info(f"{status_icon} {service}: {'available' if healthy else 'unavailable'}")

    logger.info("=" * 70)
