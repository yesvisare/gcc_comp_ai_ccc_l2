"""
FastAPI wrapper for L3 M3.2: Automated Compliance Testing

Provides HTTP API endpoints for:
- PII detection
- Policy evaluation
- Compliance validation
- Test execution
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from config import get_config, check_service_availability
from src.l3_m3_monitoring_reporting import (
    check_compliance,
    evaluate_policy,
    run_compliance_tests,
    contains_pii,
    redaction_quality_sufficient,
    ComplianceValidator
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M3.2 - Automated Compliance Testing API",
    description="OPA-based compliance testing for RAG systems with PII detection",
    version="1.0.0"
)


# Request/Response Models

class PIICheckRequest(BaseModel):
    """Request model for PII detection."""
    text: str = Field(..., description="Text to check for PII")


class PIICheckResponse(BaseModel):
    """Response model for PII detection."""
    has_pii: bool
    message: str
    service: str


class RedactionCheckRequest(BaseModel):
    """Request model for redaction quality check."""
    text: str = Field(..., description="Text to validate for proper redaction")


class RedactionCheckResponse(BaseModel):
    """Response model for redaction quality check."""
    is_sufficient: bool
    message: str


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance validation."""
    operation: str = Field(..., description="Operation type (embed, query, store, etc.)")
    text: str = Field(..., description="Text content to validate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    use_presidio: bool = Field(False, description="Use Presidio for enhanced PII detection")


class ComplianceCheckResponse(BaseModel):
    """Response model for compliance validation."""
    allowed: bool
    violations: List[str]
    policy_decisions: Dict[str, Any]


class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation."""
    input_data: Dict[str, Any] = Field(..., description="Input data for policy")
    policy: str = Field("pii", description="Policy name (pii, access, audit, retention)")


class PolicyEvaluationResponse(BaseModel):
    """Response model for policy evaluation."""
    allow: bool
    violations: List[str]
    pii_detected: Optional[bool] = None
    pii_types: Optional[List[str]] = None
    policy: str


# Endpoints

@app.get("/")
async def root():
    """
    Health check endpoint.

    Returns service status and availability.
    """
    config = get_config()
    availability = check_service_availability()

    return {
        "status": "healthy",
        "module": "L3_M3.2_Automated_Compliance_Testing",
        "services": {
            "opa": {
                "enabled": config["opa_enabled"],
                "available": availability["opa"],
                "note": "Requires OPA binary installation" if not availability["opa"] else "Ready"
            },
            "presidio": {
                "enabled": config["presidio_enabled"],
                "available": availability["presidio"],
                "note": "Optional - uses regex fallback if unavailable"
            }
        },
        "endpoints": [
            "/pii/check",
            "/pii/redaction",
            "/compliance/check",
            "/policy/evaluate",
            "/tests/run"
        ]
    }


@app.post("/pii/check", response_model=PIICheckResponse)
async def check_pii(request: PIICheckRequest):
    """
    Check if text contains PII.

    Uses regex-based detection matching OPA Rego patterns.
    """
    try:
        has_pii = contains_pii(request.text)

        return PIICheckResponse(
            has_pii=has_pii,
            message=(
                "PII detected - GDPR/DPDPA violation risk"
                if has_pii
                else "No PII detected"
            ),
            service="regex-based (OPA patterns)"
        )

    except Exception as e:
        logger.error(f"PII check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pii/redaction", response_model=RedactionCheckResponse)
async def check_redaction(request: RedactionCheckRequest):
    """
    Validate redaction quality.

    Checks if PII is properly redacted with [REDACTED] markers.
    """
    try:
        is_sufficient = redaction_quality_sufficient(request.text)

        return RedactionCheckResponse(
            is_sufficient=is_sufficient,
            message=(
                "Redaction quality sufficient"
                if is_sufficient
                else "Insufficient redaction - unredacted PII found"
            )
        )

    except Exception as e:
        logger.error(f"Redaction check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/check", response_model=ComplianceCheckResponse)
async def validate_compliance(request: ComplianceCheckRequest):
    """
    Validate operation for compliance.

    Evaluates operation against PII policy using OPA logic.
    """
    try:
        availability = check_service_availability()

        # Check if Presidio requested but unavailable
        if request.use_presidio and not availability["presidio"]:
            logger.warning(
                "Presidio requested but unavailable - falling back to regex"
            )

        result = check_compliance(
            operation=request.operation,
            text=request.text,
            use_presidio=request.use_presidio and availability["presidio"]
        )

        return ComplianceCheckResponse(
            allowed=result.allowed,
            violations=result.violations,
            policy_decisions=result.policy_decisions
        )

    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policy/evaluate", response_model=PolicyEvaluationResponse)
async def evaluate_policy_endpoint(request: PolicyEvaluationRequest):
    """
    Evaluate OPA policy against input data.

    Supports policies: pii, access, audit, retention
    """
    try:
        availability = check_service_availability()

        if not availability["opa"] and request.policy != "pii":
            return {
                "allow": False,
                "violations": [
                    f"OPA not available - only 'pii' policy supported in offline mode"
                ],
                "policy": request.policy
            }

        decision = evaluate_policy(
            input_data=request.input_data,
            policy=request.policy
        )

        return PolicyEvaluationResponse(**decision)

    except Exception as e:
        logger.error(f"Policy evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tests/run")
async def run_tests():
    """
    Run compliance test suite.

    Executes automated tests matching the test pyramid:
    - PII Detection tests (70%)
    - Integration tests (20%)
    - End-to-end tests (10%)

    Target: 55-77 total tests per script specification
    """
    try:
        logger.info("Starting compliance test suite execution...")

        results = run_compliance_tests()

        return {
            "status": "completed",
            "summary": {
                "total_tests": results["total_tests"],
                "passed": results["passed"],
                "failed": results["failed"],
                "pass_rate": f"{results['pass_rate']:.1f}%"
            },
            "coverage": results["coverage"],
            "sample_results": results["results"],
            "note": f"Showing {len(results['results'])} of {results['total_tests']} test results"
        }

    except Exception as e:
        logger.error(f"Test execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Detailed health check with service diagnostics.
    """
    config = get_config()
    availability = check_service_availability()

    health_status = {
        "status": "healthy" if availability["opa"] or availability["presidio"] else "degraded",
        "timestamp": None,  # Add timestamp if needed
        "services": {
            "opa": {
                "enabled": config["opa_enabled"],
                "available": availability["opa"],
                "binary_path": config["opa_binary_path"],
                "policy_path": config["opa_policy_path"]
            },
            "presidio": {
                "enabled": config["presidio_enabled"],
                "available": availability["presidio"],
                "fallback": "regex-based PII detection active"
            }
        },
        "configuration": {
            "log_level": config["log_level"],
            "api_timeout": config["api_timeout"],
            "test_coverage_threshold": config["test_coverage_threshold"]
        },
        "mode": (
            "full" if availability["opa"] and availability["presidio"]
            else "opa_only" if availability["opa"]
            else "regex_only" if not availability["opa"] and not availability["presidio"]
            else "presidio_only"
        )
    }

    return health_status


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute startup checks and optional test run.
    """
    logger.info("=" * 60)
    logger.info("L3 M3.2: Automated Compliance Testing API - Starting")
    logger.info("=" * 60)

    config = get_config()
    availability = check_service_availability()

    logger.info(f"Configuration: {config}")
    logger.info(f"Service Availability: {availability}")

    if config["run_tests_on_startup"]:
        logger.info("Running compliance tests on startup...")
        try:
            results = run_compliance_tests()
            logger.info(
                f"Startup tests: {results['passed']}/{results['total_tests']} passed "
                f"({results['pass_rate']:.1f}%)"
            )
        except Exception as e:
            logger.error(f"Startup test execution failed: {e}")

    logger.info("API ready - visit /docs for interactive documentation")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
