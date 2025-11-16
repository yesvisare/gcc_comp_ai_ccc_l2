"""
FastAPI server for L3 M1.4: Compliance Documentation & Evidence

Provides REST API endpoints for immutable audit logging, compliance reporting,
and vendor risk assessment.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from src.l3_m1_compliance_foundations_rag_systems import (
    AuditTrail,
    AuditEvent,
    EventType,
    ComplianceReportGenerator,
    VendorRiskAssessment,
    generate_correlation_id
)
from config import (
    get_config,
    validate_config,
    get_audit_trail_connection,
    MODULE_NAME,
    VERSION
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="L3 M1 Compliance Foundations RAG Systems API",
    description="Immutable audit logging and compliance evidence management for GCC environments",
    version=VERSION
)

# Initialize audit trail (global instance)
audit_trail_connection = get_audit_trail_connection()
audit_trail = AuditTrail(db_connection=audit_trail_connection)
report_generator = ComplianceReportGenerator(audit_trail)
vendor_assessor = VendorRiskAssessment()


# Pydantic models for request/response validation
class LogEventRequest(BaseModel):
    """Request model for logging audit events."""

    event_type: str = Field(..., description="Type of event (e.g., document_ingested, query_executed)")
    user_id: str = Field(..., description="User or system identifier")
    resource_id: str = Field(..., description="Resource identifier (e.g., document ID)")
    action: str = Field(..., description="Action performed (create, read, update, delete, execute)")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    correlation_id: Optional[str] = Field(default=None, description="UUID v4 for request tracing")


class LogEventResponse(BaseModel):
    """Response model for logged events."""

    success: bool
    event: Dict[str, Any]
    message: str


class VerifyChainRequest(BaseModel):
    """Request model for chain verification."""

    start_id: Optional[int] = Field(default=None, description="Starting event ID")
    end_id: Optional[int] = Field(default=None, description="Ending event ID")


class VerifyChainResponse(BaseModel):
    """Response model for chain verification."""

    is_valid: bool
    message: str
    events_checked: int


class ComplianceReportRequest(BaseModel):
    """Request model for compliance reports."""

    start_date: Optional[str] = Field(default=None, description="ISO 8601 start date")
    end_date: Optional[str] = Field(default=None, description="ISO 8601 end date")
    event_types: Optional[List[str]] = Field(default=None, description="Filter by event types")
    user_ids: Optional[List[str]] = Field(default=None, description="Filter by user IDs")


class VendorAssessmentRequest(BaseModel):
    """Request model for vendor risk assessment."""

    vendor_name: str = Field(..., description="Vendor name (e.g., OpenAI, Pinecone)")
    responses: Dict[str, bool] = Field(
        ...,
        description="Responses to risk criteria (criterion -> True/False)"
    )


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{MODULE_NAME} API",
        "version": VERSION,
        "description": "Immutable audit logging and compliance evidence management",
        "endpoints": [
            "/health",
            "/config",
            "/log_event",
            "/verify_chain",
            "/generate_report",
            "/sox_404_report",
            "/iso_27001_report",
            "/vendor_assessment",
            "/correlation/{correlation_id}",
            "/event_types"
        ],
        "documentation": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    is_valid = validate_config()

    return {
        "status": "healthy" if is_valid else "degraded",
        "config_valid": is_valid,
        "module": MODULE_NAME,
        "version": VERSION,
        "audit_trail_events": audit_trail._event_count
    }


@app.get("/config")
async def config():
    """Get current configuration."""
    return get_config()


@app.post("/log_event", response_model=LogEventResponse)
async def log_event(request: LogEventRequest):
    """
    Log an immutable audit event.

    Creates a new event in the hash-chained audit trail. Events are
    append-only and cryptographically linked to prevent tampering.

    Args:
        request: LogEventRequest with event details

    Returns:
        LogEventResponse with created event details

    Raises:
        HTTPException: If logging fails
    """
    try:
        logger.info(
            f"Logging event: {request.event_type} | User: {request.user_id} | "
            f"Resource: {request.resource_id}"
        )

        event = audit_trail.log_event(
            event_type=request.event_type,
            user_id=request.user_id,
            resource_id=request.resource_id,
            action=request.action,
            metadata=request.metadata,
            correlation_id=request.correlation_id
        )

        return LogEventResponse(
            success=True,
            event=event.to_dict(),
            message="Event logged successfully"
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error logging event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/verify_chain", response_model=VerifyChainResponse)
async def verify_chain(request: VerifyChainRequest):
    """
    Verify the integrity of the audit log hash chain.

    Recomputes hashes for all events and verifies they match stored values.
    Any tampering will be detected and reported.

    Args:
        request: VerifyChainRequest with optional range

    Returns:
        VerifyChainResponse with verification result

    Raises:
        HTTPException: If verification fails
    """
    try:
        logger.info("Verifying hash chain integrity...")

        is_valid, message = audit_trail.verify_chain_integrity(
            start_id=request.start_id,
            end_id=request.end_id
        )

        events_checked = audit_trail._event_count
        if request.start_id or request.end_id:
            start = request.start_id or 0
            end = request.end_id or events_checked
            events_checked = end - start

        return VerifyChainResponse(
            is_valid=is_valid,
            message=message,
            events_checked=events_checked
        )

    except Exception as e:
        logger.error(f"Error verifying chain: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/generate_report")
async def generate_report(request: ComplianceReportRequest):
    """
    Generate compliance report for audit requests.

    Filters events by date range, event types, and users, then generates
    statistics and compliance statements.

    Args:
        request: ComplianceReportRequest with filter criteria

    Returns:
        Compliance report with events, statistics, and integrity verification

    Raises:
        HTTPException: If report generation fails
    """
    try:
        logger.info("Generating compliance report...")

        report = audit_trail.generate_compliance_report(
            start_date=request.start_date,
            end_date=request.end_date,
            event_types=request.event_types,
            user_ids=request.user_ids
        )

        return report

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sox_404_report")
async def sox_404_report(
    start_date: str = Query(..., description="ISO 8601 start date"),
    end_date: str = Query(..., description="ISO 8601 end date")
):
    """
    Generate SOX Section 404 compliance report.

    Focuses on internal controls over financial reporting.

    Args:
        start_date: ISO 8601 start date
        end_date: ISO 8601 end date

    Returns:
        SOX 404 formatted report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        logger.info(f"Generating SOX 404 report: {start_date} to {end_date}")

        report = report_generator.generate_sox_404_report(
            start_date=start_date,
            end_date=end_date
        )

        return report

    except Exception as e:
        logger.error(f"Error generating SOX 404 report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/iso_27001_report")
async def iso_27001_report(
    control: str = Query(..., description="ISO 27001 control ID (e.g., A.12.4.1)"),
    start_date: str = Query(..., description="ISO 8601 start date"),
    end_date: str = Query(..., description="ISO 8601 end date")
):
    """
    Generate ISO 27001 control evidence report.

    Args:
        control: ISO 27001 control ID
        start_date: ISO 8601 start date
        end_date: ISO 8601 end date

    Returns:
        ISO 27001 formatted report

    Raises:
        HTTPException: If report generation fails
    """
    try:
        logger.info(f"Generating ISO 27001 report for control {control}")

        report = report_generator.generate_iso_27001_report(
            control=control,
            start_date=start_date,
            end_date=end_date
        )

        return report

    except Exception as e:
        logger.error(f"Error generating ISO 27001 report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/vendor_assessment")
async def vendor_assessment(request: VendorAssessmentRequest):
    """
    Conduct vendor risk assessment.

    Evaluates third-party AI vendors (OpenAI, Pinecone, etc.) against
    compliance requirements.

    Args:
        request: VendorAssessmentRequest with vendor details and criteria responses

    Returns:
        Assessment report with risk score and recommendations

    Raises:
        HTTPException: If assessment fails
    """
    try:
        logger.info(f"Assessing vendor: {request.vendor_name}")

        assessment = vendor_assessor.assess_vendor(
            vendor_name=request.vendor_name,
            responses=request.responses
        )

        return assessment

    except Exception as e:
        logger.error(f"Error assessing vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/correlation/{correlation_id}")
async def get_correlation_events(correlation_id: str):
    """
    Get all events with the same correlation ID.

    Traces a single request across multiple components (e.g., RAG query
    → vector DB → LLM → response).

    Args:
        correlation_id: UUID v4 correlation ID

    Returns:
        List of events with matching correlation ID

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info(f"Retrieving events for correlation_id: {correlation_id}")

        events = audit_trail.get_events_by_correlation_id(correlation_id)

        return {
            "correlation_id": correlation_id,
            "event_count": len(events),
            "events": [e.to_dict() for e in events]
        }

    except Exception as e:
        logger.error(f"Error retrieving correlation events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/event_types")
async def get_event_types():
    """
    Get list of standard event types.

    Returns:
        List of EventType enum values with descriptions
    """
    event_types = {
        "standard_types": [
            {
                "name": event.value,
                "description": event.name.replace("_", " ").title()
            }
            for event in EventType
        ],
        "custom_types_allowed": True,
        "recommendation": "Use standard types when possible for consistency"
    }

    return event_types


@app.get("/generate_correlation_id")
async def create_correlation_id():
    """
    Generate a new UUID v4 correlation ID.

    Returns:
        New correlation ID
    """
    correlation_id = generate_correlation_id()

    return {
        "correlation_id": correlation_id,
        "usage": "Use this ID to trace requests across multiple components"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {MODULE_NAME} API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
