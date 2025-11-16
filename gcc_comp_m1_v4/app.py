"""
FastAPI server for L3 M1.4: Compliance Documentation & Evidence

Provides REST API endpoints for:
- Audit event logging with hash chaining
- Compliance report generation
- Evidence collection and export
- Vendor risk assessment

No external AI services required - operates in OFFLINE mode.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from src.l3_m1_compliance_foundations_rag_systems import (
    AuditTrail,
    EvidenceCollector,
    ComplianceReporter,
    VendorRiskAssessment,
    EventType,
    ComplianceFramework,
    create_audit_trail,
    verify_audit_integrity
)
from config import get_config, validate_config, get_postgres_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="L3 M1 Compliance Documentation & Evidence API",
    description="Immutable audit trails and compliance evidence system for GCC environments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize audit trail (in-memory for demo, PostgreSQL for production)
audit_trail = create_audit_trail(storage_backend=None)

# Pydantic models for request/response validation

class AuditEventRequest(BaseModel):
    """Request model for creating audit events."""
    event_type: str = Field(..., description="Type of audit event")
    user_id: str = Field(..., description="User identifier")
    resource_id: str = Field(..., description="Resource identifier")
    action: str = Field(..., description="Action performed")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional event data")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "document_accessed",
                "user_id": "analyst_jane_doe",
                "resource_id": "financial_report_q3_2024.pdf",
                "action": "read",
                "metadata": {
                    "ip_address": "192.168.1.105",
                    "sensitivity_level": "confidential"
                }
            }
        }


class AuditEventResponse(BaseModel):
    """Response model for created audit events."""
    correlation_id: str
    event_type: str
    timestamp: str
    current_hash: str
    previous_hash: Optional[str]


class ComplianceReportRequest(BaseModel):
    """Request model for compliance reports."""
    framework: str = Field(..., description="Compliance framework (sox, soc2, iso27001, etc.)")
    start_date: Optional[str] = Field(None, description="Start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="End date (ISO 8601)")
    user_id: Optional[str] = Field(None, description="Filter by user ID")

    class Config:
        json_schema_extra = {
            "example": {
                "framework": "sox",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "user_id": None
            }
        }


class VendorAssessmentRequest(BaseModel):
    """Request model for vendor risk assessments."""
    vendor_name: str = Field(..., description="Vendor name")
    services_used: List[str] = Field(..., description="Services used from vendor")
    compliance_frameworks: List[str] = Field(..., description="Required compliance frameworks")
    risk_criteria: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None,
        description="Custom risk scoring criteria"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "OpenAI",
                "services_used": ["GPT-4", "Embeddings API"],
                "compliance_frameworks": ["soc2", "gdpr"],
                "risk_criteria": {
                    "data_residency": {"weight": 0.3, "score": 0.7},
                    "soc2_certified": {"weight": 0.25, "score": 1.0},
                    "gdpr_compliant": {"weight": 0.25, "score": 0.8},
                    "incident_history": {"weight": 0.2, "score": 0.9}
                }
            }
        }


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "L3 M1.4: Compliance Documentation & Evidence API",
        "version": "1.0.0",
        "mode": "OFFLINE (no external AI services)",
        "endpoints": {
            "audit": [
                "/audit/log",
                "/audit/verify",
                "/audit/events"
            ],
            "compliance": [
                "/compliance/report",
                "/compliance/sox",
                "/compliance/soc2"
            ],
            "evidence": [
                "/evidence/collect",
                "/evidence/export"
            ],
            "vendor": [
                "/vendor/assess"
            ],
            "system": [
                "/health",
                "/config"
            ]
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    is_valid = validate_config()
    return {
        "status": "healthy",
        "config_valid": is_valid,
        "audit_events_count": len(audit_trail.events),
        "offline_mode": True,
        "postgres_connected": get_postgres_connection() is not None
    }


@app.get("/config")
async def config():
    """Get current configuration."""
    return get_config()


@app.post("/audit/log", response_model=AuditEventResponse)
async def log_audit_event(request: AuditEventRequest):
    """
    Log an audit event with hash chaining.

    Creates an immutable audit trail entry with cryptographic linking
    to the previous event. Satisfies SOX 404, SOC 2, and ISO 27001
    requirements for audit logging.

    Args:
        request: AuditEventRequest with event details

    Returns:
        AuditEventResponse with created event metadata

    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Logging audit event: {request.event_type} by {request.user_id}")

        event = audit_trail.log_event(
            event_type=request.event_type,
            user_id=request.user_id,
            resource_id=request.resource_id,
            action=request.action,
            metadata=request.metadata
        )

        return AuditEventResponse(
            correlation_id=event.correlation_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            current_hash=event.current_hash,
            previous_hash=event.previous_hash
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/audit/verify")
async def verify_audit_trail():
    """
    Verify integrity of entire audit trail.

    Recomputes hash chain to detect tampering. Returns detailed
    information about integrity status.

    Returns:
        Dictionary with verification results
    """
    try:
        logger.info("Verifying audit trail integrity")

        is_valid, error_msg = audit_trail.verify_chain_integrity()

        return {
            "integrity_verified": is_valid,
            "total_events": len(audit_trail.events),
            "error_message": error_msg,
            "verification_timestamp": datetime.utcnow().isoformat(),
            "hash_algorithm": "SHA-256"
        }

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")


@app.get("/audit/events")
async def get_audit_events(
    limit: int = Query(default=100, le=1000, description="Maximum events to return"),
    offset: int = Query(default=0, ge=0, description="Number of events to skip"),
    user_id: Optional[str] = Query(default=None, description="Filter by user ID")
):
    """
    Get audit events with pagination.

    Args:
        limit: Maximum number of events to return (max 1000)
        offset: Number of events to skip
        user_id: Optional filter by user ID

    Returns:
        Dictionary with paginated events
    """
    try:
        events = audit_trail.events

        # Filter by user_id if provided
        if user_id:
            events = [e for e in events if e.user_id == user_id]

        # Apply pagination
        total = len(events)
        paginated_events = events[offset:offset + limit]

        return {
            "total_events": total,
            "returned_events": len(paginated_events),
            "offset": offset,
            "limit": limit,
            "events": [e.to_dict() for e in paginated_events]
        }

    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve events")


@app.post("/compliance/report")
async def generate_compliance_report(request: ComplianceReportRequest):
    """
    Generate compliance report for specified framework.

    Supports SOX, SOC 2, ISO 27001, GDPR, DPDPA, HIPAA, PCI-DSS.

    Args:
        request: ComplianceReportRequest with framework and filters

    Returns:
        Compliance report dictionary with events and metadata

    Raises:
        HTTPException: If framework is invalid
    """
    try:
        logger.info(f"Generating compliance report for {request.framework}")

        # Validate framework
        try:
            framework = ComplianceFramework(request.framework.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework: {request.framework}. "
                       f"Valid options: {[f.value for f in ComplianceFramework]}"
            )

        # Parse dates if provided
        start_date = None
        end_date = None
        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date)
        if request.end_date:
            end_date = datetime.fromisoformat(request.end_date)

        # Generate report
        report = audit_trail.generate_compliance_report(
            start_date=start_date,
            end_date=end_date,
            framework=framework,
            user_id=request.user_id
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")


@app.get("/compliance/sox")
async def generate_sox_report(
    fiscal_year: int = Query(..., description="Fiscal year"),
    quarter: int = Query(..., ge=1, le=4, description="Quarter (1-4)")
):
    """
    Generate SOX Section 404 compliance report.

    Args:
        fiscal_year: Fiscal year for report
        quarter: Quarter (1-4)

    Returns:
        SOX compliance report with ITGC controls
    """
    try:
        logger.info(f"Generating SOX 404 report for FY{fiscal_year} Q{quarter}")

        reporter = ComplianceReporter(audit_trail)
        report = reporter.generate_sox_report(
            fiscal_year=fiscal_year,
            quarter=quarter
        )

        return report

    except Exception as e:
        logger.error(f"Failed to generate SOX report: {e}")
        raise HTTPException(status_code=500, detail="SOX report generation failed")


@app.get("/compliance/soc2")
async def generate_soc2_report(
    report_period_days: int = Query(default=365, ge=1, le=730, description="Reporting period in days")
):
    """
    Generate SOC 2 Type II compliance report.

    Args:
        report_period_days: Reporting period in days (default 365)

    Returns:
        SOC 2 compliance report with Trust Service Criteria
    """
    try:
        logger.info(f"Generating SOC 2 report for {report_period_days} days")

        reporter = ComplianceReporter(audit_trail)
        report = reporter.generate_soc2_report(
            report_period_days=report_period_days
        )

        return report

    except Exception as e:
        logger.error(f"Failed to generate SOC 2 report: {e}")
        raise HTTPException(status_code=500, detail="SOC 2 report generation failed")


@app.post("/evidence/collect")
async def collect_evidence(
    start_date: str = Query(..., description="Evidence collection start (ISO 8601)"),
    end_date: str = Query(..., description="Evidence collection end (ISO 8601)"),
    evidence_type: str = Query(default="system", description="Evidence type (system, process, outcome)")
):
    """
    Collect compliance evidence for specified period.

    Args:
        start_date: Evidence collection start date
        end_date: Evidence collection end date
        evidence_type: Type of evidence to collect

    Returns:
        Collected evidence package

    Raises:
        HTTPException: If dates are invalid
    """
    try:
        logger.info(f"Collecting {evidence_type} evidence from {start_date} to {end_date}")

        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        collector = EvidenceCollector()

        if evidence_type == "system":
            evidence = collector.collect_system_evidence(
                audit_trail=audit_trail,
                start_date=start,
                end_date=end
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Evidence type '{evidence_type}' not implemented. Use 'system'"
            )

        return evidence

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format (use ISO 8601)")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evidence collection failed: {e}")
        raise HTTPException(status_code=500, detail="Evidence collection failed")


@app.post("/evidence/export")
async def export_evidence(
    framework: str = Query(..., description="Compliance framework"),
    start_date: str = Query(..., description="Evidence period start (ISO 8601)"),
    end_date: str = Query(..., description="Evidence period end (ISO 8601)"),
    export_path: str = Query(default="./exports", description="Export destination path")
):
    """
    Export evidence package for compliance framework.

    Args:
        framework: Compliance framework (sox, soc2, iso27001, etc.)
        start_date: Evidence period start
        end_date: Evidence period end
        export_path: Export destination path

    Returns:
        Export metadata

    Raises:
        HTTPException: If framework or dates are invalid
    """
    try:
        logger.info(f"Exporting evidence for {framework} to {export_path}")

        # Validate framework
        try:
            framework_enum = ComplianceFramework(framework.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework: {framework}"
            )

        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        # Collect and export evidence
        collector = EvidenceCollector()
        collector.collect_system_evidence(audit_trail, start, end)

        export_metadata = collector.export_evidence_package(
            framework=framework_enum,
            export_path=export_path
        )

        return export_metadata

    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format (use ISO 8601)")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evidence export failed: {e}")
        raise HTTPException(status_code=500, detail="Evidence export failed")


@app.post("/vendor/assess")
async def assess_vendor(request: VendorAssessmentRequest):
    """
    Conduct vendor risk assessment.

    Evaluates third-party vendors (OpenAI, Anthropic, Pinecone, etc.)
    against compliance requirements.

    Args:
        request: VendorAssessmentRequest with vendor details

    Returns:
        Vendor risk assessment with recommendations

    Raises:
        HTTPException: If assessment fails
    """
    try:
        logger.info(f"Assessing vendor: {request.vendor_name}")

        # Convert framework strings to enums
        frameworks = [
            ComplianceFramework(f.lower())
            for f in request.compliance_frameworks
        ]

        assessor = VendorRiskAssessment()
        assessment = assessor.assess_vendor(
            vendor_name=request.vendor_name,
            services_used=request.services_used,
            compliance_frameworks=frameworks,
            risk_criteria=request.risk_criteria
        )

        return assessment

    except ValueError as e:
        logger.error(f"Invalid framework: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Vendor assessment failed: {e}")
        raise HTTPException(status_code=500, detail="Vendor assessment failed")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting L3 M1 Compliance Documentation & Evidence API")
    logger.info("Mode: OFFLINE (no external AI services required)")
    validate_config()

    # Log a startup event
    audit_trail.log_event(
        event_type="system_startup",
        user_id="system",
        resource_id="api_server",
        action="started",
        metadata={"version": "1.0.0", "mode": "offline"}
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down L3 M1 Compliance Documentation & Evidence API")

    # Log a shutdown event
    audit_trail.log_event(
        event_type="system_shutdown",
        user_id="system",
        resource_id="api_server",
        action="stopped",
        metadata={"total_events": len(audit_trail.events)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
