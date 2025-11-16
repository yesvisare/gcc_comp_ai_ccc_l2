"""
FastAPI server for L3 M1.1: Why Compliance Matters in GCC RAG Systems

Provides HTTP endpoints for compliance risk assessment, data classification,
and regulation mapping.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from src.l3_m1_compliance_foundations_rag_systems import (
    ComplianceRiskAssessor,
    DataClassifier,
    RegulationMapper,
    assess_compliance_risk
)
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M1.1: Compliance Risk Assessment for GCC RAG Systems",
    description="Automated compliance risk assessment tool for RAG systems",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AssessmentRequest(BaseModel):
    """Request model for compliance risk assessment."""
    use_case_description: str = Field(
        ...,
        description="Description of the RAG system use case",
        example="Our customer service RAG system processes support tickets containing customer names, emails, and order histories to provide automated responses."
    )
    enable_presidio: bool = Field(
        default=False,
        description="Enable Presidio for enhanced PII detection"
    )
    enable_openai: bool = Field(
        default=False,
        description="Enable OpenAI for enhanced risk analysis"
    )


class ClassificationRequest(BaseModel):
    """Request model for data classification."""
    text: str = Field(
        ...,
        description="Text to classify",
        example="Patient John Doe was prescribed medication for hypertension. Contact: john.doe@email.com, SSN: 123-45-6789"
    )
    enable_presidio: bool = Field(
        default=False,
        description="Enable Presidio for enhanced PII detection"
    )


class RegulationQueryRequest(BaseModel):
    """Request model for regulation details."""
    regulation_code: str = Field(
        ...,
        description="Regulation code (e.g., GDPR, HIPAA, SOC2)",
        example="GDPR"
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "L3 M1.1: Compliance Risk Assessment",
        "version": "1.0.0",
        "description": "Automated compliance risk assessment tool for GCC RAG systems",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "POST /assess": "Complete compliance risk assessment",
            "POST /classify": "Data classification only",
            "GET /regulations": "List all regulations",
            "POST /regulations/details": "Get regulation details"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service status and configuration.
    """
    config_summary = config.get_config_summary()

    return {
        "status": "healthy",
        "services": {
            "presidio": {
                "enabled": config.PRESIDIO_ENABLED,
                "available": config.presidio_analyzer is not None
            },
            "openai": {
                "enabled": config.OPENAI_ENABLED,
                "available": config.openai_client is not None
            }
        },
        "configuration": config_summary
    }


@app.post("/assess")
async def assess_compliance(request: AssessmentRequest) -> Dict[str, Any]:
    """
    Perform complete compliance risk assessment.

    Analyzes the use case description to:
    - Detect data types (PII, PHI, financial, proprietary)
    - Identify triggered regulations
    - Calculate risk score (1-10)
    - Generate compliance checklist
    - Recommend required controls

    Args:
        request: Assessment request with use case description

    Returns:
        Complete assessment results including regulations, risk score, and checklist
    """
    logger.info("Received compliance assessment request")

    try:
        # Check if Presidio is requested but not available
        if request.enable_presidio and not config.PRESIDIO_ENABLED:
            logger.warning("Presidio requested but not enabled")
            return {
                "status": "warning",
                "message": "⚠️ Presidio requested but not enabled. Install presidio-analyzer and set PRESIDIO_ENABLED=true",
                "fallback": "Using keyword-based detection"
            }

        # Check if OpenAI is requested but not available
        if request.enable_openai and not config.OPENAI_ENABLED:
            logger.warning("OpenAI requested but not enabled")

        # Perform assessment
        result = assess_compliance_risk(
            use_case_description=request.use_case_description,
            use_presidio=request.enable_presidio and config.PRESIDIO_ENABLED,
            use_openai=request.enable_openai and config.OPENAI_ENABLED
        )

        logger.info(f"Assessment complete: {len(result['triggered_regulations'])} regulations triggered")

        return {
            "status": "success",
            "assessment": result
        }

    except Exception as e:
        logger.error(f"Error during assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/classify")
async def classify_data(request: ClassificationRequest) -> Dict[str, Any]:
    """
    Classify data types in text.

    Detects PII, PHI, financial data, and proprietary information.

    Args:
        request: Classification request with text to analyze

    Returns:
        Classification results for each data type
    """
    logger.info("Received data classification request")

    try:
        classifier = DataClassifier(
            use_presidio=request.enable_presidio and config.PRESIDIO_ENABLED
        )

        # Run all classifiers
        pii_result = classifier.detect_pii(request.text)
        phi_result = classifier.detect_phi(request.text)
        financial_result = classifier.detect_financial(request.text)
        proprietary_result = classifier.detect_proprietary(request.text)

        logger.info("Classification complete")

        return {
            "status": "success",
            "classification": {
                "pii": {
                    "detected": pii_result.detected,
                    "entities": pii_result.entities,
                    "confidence": pii_result.confidence,
                    "examples": pii_result.examples[:3],  # Limit examples
                    "risk_factors": pii_result.risk_factors
                },
                "phi": {
                    "detected": phi_result.detected,
                    "entities": phi_result.entities,
                    "confidence": phi_result.confidence,
                    "keywords": phi_result.examples[:3],
                    "risk_factors": phi_result.risk_factors
                },
                "financial": {
                    "detected": financial_result.detected,
                    "entities": financial_result.entities,
                    "confidence": financial_result.confidence,
                    "examples": financial_result.examples[:3],
                    "risk_factors": financial_result.risk_factors
                },
                "proprietary": {
                    "detected": proprietary_result.detected,
                    "entities": proprietary_result.entities,
                    "confidence": proprietary_result.confidence,
                    "markers": proprietary_result.examples[:3],
                    "risk_factors": proprietary_result.risk_factors
                }
            }
        }

    except Exception as e:
        logger.error(f"Error during classification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.get("/regulations")
async def list_regulations() -> Dict[str, Any]:
    """
    List all available regulations.

    Returns:
        List of regulation codes with names and jurisdictions
    """
    logger.info("Fetching regulations list")

    try:
        mapper = RegulationMapper()
        all_regs = mapper.get_all_regulations()

        regulations_list = [
            {
                "code": code,
                "name": details["full_name"],
                "jurisdiction": details["jurisdiction"],
                "data_types": details["data_types"]
            }
            for code, details in all_regs.items()
        ]

        return {
            "status": "success",
            "count": len(regulations_list),
            "regulations": regulations_list
        }

    except Exception as e:
        logger.error(f"Error fetching regulations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch regulations: {str(e)}")


@app.post("/regulations/details")
async def get_regulation_details(request: RegulationQueryRequest) -> Dict[str, Any]:
    """
    Get detailed information about a specific regulation.

    Args:
        request: Regulation query with regulation code

    Returns:
        Detailed regulation information including requirements and RAG-specific controls
    """
    logger.info(f"Fetching details for regulation: {request.regulation_code}")

    try:
        mapper = RegulationMapper()
        details = mapper.get_requirements(request.regulation_code.upper())

        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"Regulation '{request.regulation_code}' not found"
            )

        return {
            "status": "success",
            "regulation": request.regulation_code.upper(),
            "details": details
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching regulation details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch details: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
