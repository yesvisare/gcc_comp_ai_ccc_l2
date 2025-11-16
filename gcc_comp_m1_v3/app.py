"""
FastAPI entrypoint for L3 M1.3: Regulatory Frameworks Deep Dive

Provides REST API endpoints for multi-framework compliance analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from src.l3_m1_compliance_foundations import (
    MultiFrameworkAnalyzer,
    GDPRAnalyzer,
    SOC2Analyzer,
    ISO27001Analyzer,
    HIPAAAnalyzer,
    ComplianceReport
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M1.3: Regulatory Frameworks Deep Dive",
    description="Multi-framework compliance analysis for RAG systems (GDPR, SOC 2, ISO 27001, HIPAA)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RAGArchitecture(BaseModel):
    """RAG architecture specification for compliance analysis."""
    components: List[str] = Field(description="RAG components (e.g., vector_db, embedding_model, llm)")
    data_flows: List[str] = Field(description="Data flows (e.g., ingestion, retrieval, generation)")
    storage: Dict[str, Any] = Field(description="Storage configuration")
    access_control: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)
    apis: List[str] = Field(default_factory=list)
    documentation: Dict[str, Any] = Field(default_factory=dict)
    retention_policy: Dict[str, Any] = Field(default_factory=dict)
    infrastructure: Dict[str, Any] = Field(default_factory=dict)
    data_processing: Dict[str, Any] = Field(default_factory=dict)
    backups: Dict[str, Any] = Field(default_factory=dict)
    incident_response: Dict[str, Any] = Field(default_factory=dict)
    training: Dict[str, Any] = Field(default_factory=dict)
    vendors: List[Dict[str, Any]] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """Request model for compliance analysis."""
    rag_architecture: Dict[str, Any]
    frameworks: Optional[List[str]] = None  # Default: all frameworks


class FrameworkAnalysisRequest(BaseModel):
    """Request model for single-framework analysis."""
    rag_architecture: Dict[str, Any]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "module": "L3_M1_Compliance_Foundations",
        "frameworks": ["GDPR", "SOC2", "ISO27001", "HIPAA"],
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "Multi-Framework Compliance Analyzer",
        "frameworks_available": ["GDPR", "SOC2", "ISO27001", "HIPAA"],
        "endpoints": [
            "/analyze",
            "/analyze/gdpr",
            "/analyze/soc2",
            "/analyze/iso27001",
            "/analyze/hipaa",
            "/overlapping-controls"
        ]
    }


@app.post("/analyze")
async def analyze_all_frameworks(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze RAG architecture against all selected compliance frameworks.

    Returns comprehensive compliance report with:
    - Compliance scores per framework
    - Gap analysis with remediation roadmap
    - Overlapping control identification
    - Audit readiness assessment
    """
    try:
        analyzer = MultiFrameworkAnalyzer()

        # Convert frameworks to uppercase if provided
        frameworks = None
        if request.frameworks:
            frameworks = [f.upper() for f in request.frameworks]

        # Run multi-framework analysis
        report: ComplianceReport = analyzer.analyze_all_frameworks(
            request.rag_architecture,
            frameworks=frameworks
        )

        # Convert to dictionary for JSON response
        return {
            "overall_score": report.overall_score,
            "framework_scores": {
                "GDPR": report.gdpr_score,
                "SOC2": report.soc2_score,
                "ISO27001": report.iso27001_score,
                "HIPAA": report.hipaa_score
            },
            "audit_ready": report.audit_ready,
            "gap_summary": {
                framework: {
                    "compliance_score": gap.compliance_score,
                    "total_controls_checked": gap.total_controls_checked,
                    "compliant_controls": gap.compliant_controls,
                    "non_compliant_controls": gap.non_compliant_controls,
                    "total_remediation_hours": gap.total_remediation_hours,
                    "total_penalty_risk_eur": gap.total_penalty_risk,
                    "priority_gaps": [
                        {
                            "control_id": g.control_id,
                            "control_name": g.control_name,
                            "gap_description": g.gap_description,
                            "effort_hours": g.effort_hours,
                            "penalty_risk_eur": g.penalty_risk_eur
                        }
                        for g in gap.prioritized_gaps[:5]  # Top 5 priorities
                    ]
                }
                for framework, gap in report.gap_analyses.items()
            },
            "remediation_plans": {
                framework: {
                    "timeline_weeks": plan.timeline_weeks,
                    "estimated_cost_inr": plan.estimated_cost_inr,
                    "quick_wins": plan.quick_wins,
                    "long_term_initiatives": plan.long_term_initiatives
                }
                for framework, plan in report.remediation_plans.items()
            },
            "overlapping_controls": report.overlapping_controls,
            "total_unique_controls": report.total_unique_controls
        }

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/gdpr")
async def analyze_gdpr(request: FrameworkAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze RAG architecture against GDPR requirements only.

    Checks:
    - 7 core principles
    - 8 data subject rights
    - Technical and organizational measures
    """
    try:
        analyzer = GDPRAnalyzer()
        gap_analysis = analyzer.analyze(request.rag_architecture)

        return {
            "framework": "GDPR",
            "compliance_score": gap_analysis.compliance_score,
            "total_controls_checked": gap_analysis.total_controls_checked,
            "compliant_controls": gap_analysis.compliant_controls,
            "non_compliant_controls": gap_analysis.non_compliant_controls,
            "gaps": [
                {
                    "control_id": gap.control_id,
                    "control_name": gap.control_name,
                    "gap_description": gap.gap_description,
                    "remediation_steps": gap.remediation_steps,
                    "effort_hours": gap.effort_hours,
                    "penalty_risk_eur": gap.penalty_risk_eur
                }
                for gap in gap_analysis.gaps
            ],
            "total_remediation_hours": gap_analysis.total_remediation_hours,
            "total_penalty_risk_eur": gap_analysis.total_penalty_risk
        }

    except Exception as e:
        logger.error(f"GDPR analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/soc2")
async def analyze_soc2(request: FrameworkAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze RAG architecture against SOC 2 Trust Service Criteria.

    Checks:
    - Security TSC (required)
    - Availability, Processing Integrity, Confidentiality, Privacy TSC
    - Type II evidence collection
    """
    try:
        analyzer = SOC2Analyzer()
        gap_analysis = analyzer.analyze(request.rag_architecture)

        return {
            "framework": "SOC2",
            "compliance_score": gap_analysis.compliance_score,
            "total_controls_checked": gap_analysis.total_controls_checked,
            "compliant_controls": gap_analysis.compliant_controls,
            "non_compliant_controls": gap_analysis.non_compliant_controls,
            "gaps": [
                {
                    "control_id": gap.control_id,
                    "control_name": gap.control_name,
                    "gap_description": gap.gap_description,
                    "remediation_steps": gap.remediation_steps,
                    "effort_hours": gap.effort_hours
                }
                for gap in gap_analysis.gaps
            ],
            "total_remediation_hours": gap_analysis.total_remediation_hours
        }

    except Exception as e:
        logger.error(f"SOC 2 analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/iso27001")
async def analyze_iso27001(request: FrameworkAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze RAG architecture against ISO 27001 requirements.

    Checks:
    - 93 Annex A controls (sample)
    - ISMS documentation requirements
    """
    try:
        analyzer = ISO27001Analyzer()
        gap_analysis = analyzer.analyze(request.rag_architecture)

        return {
            "framework": "ISO27001",
            "compliance_score": gap_analysis.compliance_score,
            "total_controls_checked": gap_analysis.total_controls_checked,
            "compliant_controls": gap_analysis.compliant_controls,
            "non_compliant_controls": gap_analysis.non_compliant_controls,
            "gaps": [
                {
                    "control_id": gap.control_id,
                    "control_name": gap.control_name,
                    "gap_description": gap.gap_description,
                    "remediation_steps": gap.remediation_steps,
                    "effort_hours": gap.effort_hours
                }
                for gap in gap_analysis.gaps
            ],
            "total_remediation_hours": gap_analysis.total_remediation_hours
        }

    except Exception as e:
        logger.error(f"ISO 27001 analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/hipaa")
async def analyze_hipaa(request: FrameworkAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze RAG architecture against HIPAA Security Rule.

    Checks:
    - Administrative safeguards
    - Physical safeguards
    - Technical safeguards
    - BAA requirements
    """
    try:
        analyzer = HIPAAAnalyzer()
        gap_analysis = analyzer.analyze(request.rag_architecture)

        return {
            "framework": "HIPAA",
            "compliance_score": gap_analysis.compliance_score,
            "total_controls_checked": gap_analysis.total_controls_checked,
            "compliant_controls": gap_analysis.compliant_controls,
            "non_compliant_controls": gap_analysis.non_compliant_controls,
            "gaps": [
                {
                    "control_id": gap.control_id,
                    "control_name": gap.control_name,
                    "gap_description": gap.gap_description,
                    "remediation_steps": gap.remediation_steps,
                    "effort_hours": gap.effort_hours,
                    "penalty_risk_eur": gap.penalty_risk_eur
                }
                for gap in gap_analysis.gaps
            ],
            "total_remediation_hours": gap_analysis.total_remediation_hours,
            "total_penalty_risk_eur": gap_analysis.total_penalty_risk
        }

    except Exception as e:
        logger.error(f"HIPAA analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/overlapping-controls")
async def identify_overlapping_controls(request: FrameworkAnalysisRequest) -> Dict[str, Any]:
    """
    Identify controls that satisfy multiple frameworks simultaneously.

    This helps optimize implementation by reducing redundant work.
    Example: Encryption satisfies GDPR Article 32, SOC2 Confidentiality, ISO A.10, HIPAA 164.312
    """
    try:
        analyzer = MultiFrameworkAnalyzer()
        overlapping = analyzer._identify_overlapping_controls(request.rag_architecture)

        return {
            "overlapping_controls": overlapping,
            "total_overlapping": len(overlapping),
            "optimization_benefit": "Implementing these controls once satisfies multiple framework requirements"
        }

    except Exception as e:
        logger.error(f"Overlapping controls analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
