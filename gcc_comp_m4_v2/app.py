"""
FastAPI application for L3 M4.2: Vendor Risk Assessment

Provides REST API endpoints for vendor risk evaluation using a 5-category weighted matrix.
All processing is done locally - no external LLM/vector database services required.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.l3_m4_enterprise_integration_governance import VendorRiskAssessment
from config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M4.2: Vendor Risk Assessment API",
    description="Comprehensive vendor risk evaluation for GCC compliance",
    version="1.0.0"
)

# Global assessor instance
assessor = VendorRiskAssessment()


class VendorAssessmentRequest(BaseModel):
    """Request model for vendor risk assessment"""
    vendor_name: str = Field(..., description="Vendor name")

    # Security inputs
    soc2_date: Optional[str] = Field(None, description="SOC 2 Type II report date (ISO format)")
    iso27001: bool = Field(False, description="ISO 27001 certified")
    pentest_date: Optional[str] = Field(None, description="Latest penetration test date (ISO format)")
    breaches_count: int = Field(0, description="Security breaches in past 3 years")

    # Privacy inputs
    gdpr_compliant: bool = Field(False, description="GDPR compliant")
    dpa_available: bool = Field(False, description="DPA available")
    data_policy_score: int = Field(0, description="Data handling policy transparency (0-3)")
    deletion_process: str = Field('unclear', description="Data deletion process: automated_verified, manual, unclear")
    access_controls: str = Field('weak', description="Data access controls: strong, basic, weak")

    # Compliance inputs
    certifications: List[str] = Field(default_factory=list, description="Industry certifications: hipaa_baa, pci_dss, fedramp, etc.")
    audit_date: Optional[str] = Field(None, description="Latest audit report date (ISO format)")
    notification_process: str = Field('reactive', description="Compliance notifications: proactive, on_request, reactive")
    violations_count: int = Field(0, description="Regulatory violations in past 5 years")

    # Reliability inputs
    sla_guarantee: float = Field(0.0, description="SLA guarantee percentage (e.g., 99.9)")
    actual_uptime_12m: float = Field(0.0, description="Actual uptime last 12 months (percentage)")
    support_response_time: str = Field('8h', description="Support response time for critical issues (e.g., '<1h', '<4h', '8h')")
    dr_plan: str = Field('none', description="DR/BC plan status: tested_annually, documented, none")

    # Data residency inputs
    dc_locations: List[str] = Field(default_factory=list, description="Data center locations (e.g., ['US', 'EU', 'Asia'])")
    dc_selectable: bool = Field(False, description="Customer-selectable data centers")
    subproc_locations: List[str] = Field(default_factory=list, description="Subprocessor locations")
    sccs_available: bool = Field(False, description="Standard Contractual Clauses available")
    localization_support: str = Field('none', description="Data localization support: full, partial, none")


class VendorAssessmentResponse(BaseModel):
    """Response model for vendor risk assessment"""
    vendor: str
    assessment_date: str
    overall_score: float
    risk_level: str
    recommendation: str
    category_scores: Dict[str, float]
    findings: Dict[str, List[str]]


class ReportResponse(BaseModel):
    """Response model for assessment report"""
    vendors: List[Dict[str, Any]]
    total_vendors: int


@app.get("/")
def root():
    """Health check endpoint"""
    config = get_config()
    return {
        "status": "healthy",
        "module": "L3_M4_Enterprise_Integration_Governance",
        "description": "Vendor Risk Assessment API",
        "processing_mode": "offline (local processing only)",
        "config": {
            "log_level": config['log_level'],
            "database_configured": config['database_url'] is not None,
            "dpa_analysis_enabled": config['use_dpa_analysis']
        }
    }


@app.post("/assess", response_model=VendorAssessmentResponse)
def assess_vendor(request: VendorAssessmentRequest):
    """
    Assess vendor risk using 5-category weighted matrix.

    Categories:
    - Security (30%): SOC 2, ISO 27001, penetration testing, incident history
    - Privacy (25%): GDPR compliance, DPA availability, data handling
    - Compliance (20%): Certifications, audit reports, regulatory alignment
    - Reliability (15%): SLA, uptime, support responsiveness
    - Data Residency (10%): Geographic locations, subprocessors

    Returns:
        VendorAssessmentResponse with overall score, risk level, and detailed findings
    """
    try:
        logger.info(f"Assessing vendor: {request.vendor_name}")

        # Convert date strings to datetime objects
        inputs = request.model_dump()
        if inputs.get('soc2_date'):
            inputs['soc2_date'] = datetime.fromisoformat(inputs['soc2_date'])
        if inputs.get('pentest_date'):
            inputs['pentest_date'] = datetime.fromisoformat(inputs['pentest_date'])
        if inputs.get('audit_date'):
            inputs['audit_date'] = datetime.fromisoformat(inputs['audit_date'])

        # Calculate overall risk
        result = assessor.calculate_overall_risk(request.vendor_name, inputs)

        return VendorAssessmentResponse(**result)

    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report", response_model=ReportResponse)
def get_report():
    """
    Get summary report of all vendor assessments.

    Returns:
        ReportResponse with all assessed vendors sorted by risk score
    """
    try:
        report_data = assessor.generate_report(output_format='dict')

        if isinstance(report_data, dict) and 'error' in report_data:
            raise HTTPException(status_code=404, detail=report_data['error'])

        return ReportResponse(
            vendors=report_data,
            total_vendors=len(report_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vendors/{vendor_name}")
def get_vendor_assessment(vendor_name: str):
    """
    Get assessment results for a specific vendor.

    Args:
        vendor_name: Name of the vendor

    Returns:
        Assessment results or 404 if not found
    """
    if vendor_name not in assessor.vendors:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor '{vendor_name}' not found. Assess the vendor first using POST /assess"
        )

    return assessor.vendors[vendor_name]


@app.delete("/vendors/{vendor_name}")
def delete_vendor_assessment(vendor_name: str):
    """
    Delete assessment for a specific vendor.

    Args:
        vendor_name: Name of the vendor

    Returns:
        Success message
    """
    if vendor_name not in assessor.vendors:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor '{vendor_name}' not found"
        )

    del assessor.vendors[vendor_name]
    logger.info(f"Deleted assessment for vendor: {vendor_name}")

    return {
        "message": f"Assessment for vendor '{vendor_name}' deleted successfully"
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "assessments_count": len(assessor.vendors),
        "assessed_vendors": list(assessor.vendors.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
