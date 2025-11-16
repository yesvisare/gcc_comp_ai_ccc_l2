"""
FastAPI entrypoint for L3 M4.2: Vendor Risk Assessment

Production-ready API for comprehensive vendor risk assessment with DPA validation,
subprocessor tracking, and multi-jurisdiction compliance checking.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Import from src package
from src.l3_m4_enterprise_integration_governance import (
    assess_vendor,
    calculate_roi,
    VendorProfile,
    VendorRiskAssessment,
    DPAValidator,
    SubprocessorRegistry,
    ContinuousMonitor,
    multi_jurisdiction_compliance_check
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M4.2: Vendor Risk Assessment API",
    description="Production-ready API for GCC vendor risk assessment with automated compliance checking",
    version="1.0.0"
)


# Request/Response Models
class VendorAssessmentRequest(BaseModel):
    """Request model for vendor assessment."""
    name: str = Field(..., description="Vendor company name")
    soc2_date: Optional[str] = Field(None, description="SOC 2 certification date (ISO format)")
    iso27001_certified: bool = Field(False, description="ISO 27001 certification status")
    penetration_testing: bool = Field(False, description="Annual penetration testing conducted")
    breach_count: int = Field(0, description="Number of security breaches in past 3 years")
    gdpr_compliant: bool = Field(False, description="GDPR compliance status")
    dpa_available: bool = Field(False, description="Data Processing Agreement available")
    dpa_text: Optional[str] = Field(None, description="Full DPA text for validation")
    data_deletion_automated: bool = Field(False, description="Automated data deletion process")
    sla_guarantee: float = Field(0.0, description="SLA uptime guarantee percentage")
    actual_uptime: float = Field(0.0, description="Actual uptime performance percentage")
    data_center_locations: List[str] = Field(default_factory=list, description="Data center locations")
    subprocessors: List[Dict[str, Any]] = Field(default_factory=list, description="Subprocessor list")
    jurisdictions: List[str] = Field(default_factory=list, description="Jurisdictions to check (e.g., GDPR, DPDPA)")


class ROIRequest(BaseModel):
    """Request model for ROI calculation."""
    vendor_count: int = Field(..., description="Number of vendors to manage")


class DPAValidationRequest(BaseModel):
    """Request model for DPA validation."""
    dpa_text: str = Field(..., description="Full DPA text to validate")


class SubprocessorRegistrationRequest(BaseModel):
    """Request model for subprocessor registration."""
    vendor_name: str = Field(..., description="Primary vendor name")
    subprocessor_name: str = Field(..., description="Subprocessor company name")
    location: str = Field(..., description="Geographic location")
    has_dpa: bool = Field(False, description="Whether subprocessor has equivalent DPA")


# API Endpoints
@app.post("/assess", response_model=Dict[str, Any])
async def assess_vendor_endpoint(request: VendorAssessmentRequest):
    """
    Perform comprehensive vendor risk assessment.

    This endpoint evaluates vendors across 5 categories (Security, Privacy, Compliance,
    Reliability, Data Residency) and provides DPA validation, subprocessor analysis,
    and multi-jurisdiction compliance checking.
    """
    try:
        logger.info(f"Received assessment request for vendor: {request.name}")

        # Convert request to vendor data dict
        vendor_data = request.dict()

        # Parse SOC 2 date if provided
        if vendor_data.get("soc2_date"):
            try:
                vendor_data["soc2_date"] = datetime.fromisoformat(vendor_data["soc2_date"])
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid soc2_date format. Use ISO format (YYYY-MM-DD)")

        # Perform assessment
        result = assess_vendor(
            vendor_data=vendor_data,
            include_subprocessors=len(request.subprocessors) > 0,
            jurisdictions=request.jurisdictions if request.jurisdictions else None
        )

        logger.info(f"Assessment completed for {request.name}: {result['risk_assessment']['risk_level']}")

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        logger.error(f"Assessment failed for {request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-dpa", response_model=Dict[str, Any])
async def validate_dpa_endpoint(request: DPAValidationRequest):
    """
    Validate Data Processing Agreement against 12 essential clauses.

    Returns coverage percentage and missing clauses.
    """
    try:
        logger.info("Received DPA validation request")

        validator = DPAValidator()
        result = validator.validate_dpa(request.dpa_text)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        logger.error(f"DPA validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register-subprocessor")
async def register_subprocessor_endpoint(request: SubprocessorRegistrationRequest):
    """
    Register a subprocessor for a vendor.

    Maintains subprocessor registry for risk inheritance tracking.
    """
    try:
        logger.info(f"Registering subprocessor {request.subprocessor_name} for {request.vendor_name}")

        registry = SubprocessorRegistry()
        registry.register_subprocessor(
            vendor_name=request.vendor_name,
            subprocessor_name=request.subprocessor_name,
            location=request.location,
            has_dpa=request.has_dpa
        )

        return {
            "status": "success",
            "message": f"Subprocessor {request.subprocessor_name} registered successfully"
        }

    except Exception as e:
        logger.error(f"Subprocessor registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-roi", response_model=Dict[str, Any])
async def calculate_roi_endpoint(request: ROIRequest):
    """
    Calculate ROI for automated vs manual vendor management.

    Returns cost analysis and savings projections.
    """
    try:
        logger.info(f"Calculating ROI for {request.vendor_count} vendors")

        result = calculate_roi(request.vendor_count)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        logger.error(f"ROI calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "vendor-risk-assessment",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "L3 M4.2: Vendor Risk Assessment API",
        "version": "1.0.0",
        "endpoints": {
            "POST /assess": "Comprehensive vendor risk assessment",
            "POST /validate-dpa": "DPA validation against 12 essential clauses",
            "POST /register-subprocessor": "Register subprocessor for vendor",
            "POST /calculate-roi": "Calculate ROI for automation",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
