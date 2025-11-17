"""
FastAPI application for L3 M4.4: Compliance Maturity & Continuous Improvement

Provides REST API endpoints for maturity assessment, gap analysis, improvement
roadmaps, metrics tracking, and PDCA cycle management.

This module runs fully offline - no external AI services required.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from src.l3_m4_compliance_maturity import (
    MaturityAssessment,
    GapAnalysis,
    MetricsTracker,
    ImprovementRoadmap,
    PDCACycle,
    generate_maturity_report,
    calculate_overall_maturity,
    create_improvement_plan
)
from config import get_config_summary, PROMETHEUS_ENABLED, GRAFANA_ENABLED

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M4.4: Compliance Maturity API",
    description="REST API for compliance maturity assessment and continuous improvement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global instances
metrics_tracker = MetricsTracker()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class AssessmentRequest(BaseModel):
    """Request model for maturity assessment."""
    responses: Dict[str, int] = Field(
        ...,
        description="Dict mapping question text to selected level (1-5)",
        example={
            "How mature is your compliance training program?": 3,
            "How documented are your compliance processes?": 2
        }
    )


class AssessmentResponse(BaseModel):
    """Response model for maturity assessment."""
    assessment_date: str
    responses_collected: int
    scores: Dict[str, Any]
    limiting_dimension: str
    recommendations: List[str]
    next_target_level: int
    estimated_timeline: str


class GapAnalysisRequest(BaseModel):
    """Request model for gap analysis."""
    current_responses: Dict[str, int] = Field(..., description="Current assessment responses")
    target_level: int = Field(..., ge=1, le=5, description="Target maturity level (1-5)")


class ImprovementPlanRequest(BaseModel):
    """Request model for improvement plan."""
    current_responses: Dict[str, int]
    target_level: int = Field(..., ge=1, le=5)
    max_initiatives: int = Field(3, ge=1, le=10, description="Maximum concurrent initiatives")


class MetricUpdateRequest(BaseModel):
    """Request model for metric update."""
    metric_name: str = Field(
        ...,
        description="Metric name (e.g., 'pii_detection_accuracy')"
    )
    value: float = Field(..., description="Metric value")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp (optional)")


class PDCACycleRequest(BaseModel):
    """Request model for PDCA cycle creation."""
    cycle_name: str = Field(..., example="2025-Q1")
    duration_weeks: int = Field(12, ge=1, le=52)
    improvement_plan: Dict[str, Any] = Field(..., description="Improvement plan from /improvement-plan endpoint")


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def root():
    """Health check and API information."""
    config = get_config_summary()

    return {
        "status": "healthy",
        "module": "L3_M4.4_Compliance_Maturity_Continuous_Improvement",
        "version": "1.0.0",
        "mode": "offline",
        "description": "Maturity assessment framework with gap analysis and improvement planning",
        "features": [
            "5-level maturity assessment (25 questions across 5 dimensions)",
            "Gap analysis with prioritized improvements",
            "Improvement roadmap generation",
            "Metrics tracking with trend detection",
            "PDCA cycle management"
        ],
        "config": {
            "prometheus_enabled": config["prometheus_enabled"],
            "grafana_enabled": config["grafana_enabled"],
            "max_concurrent_initiatives": config["max_concurrent_initiatives"],
            "pdca_cycle_weeks": config["pdca_cycle_weeks"]
        },
        "endpoints": {
            "POST /assessment": "Submit maturity assessment responses",
            "POST /gap-analysis": "Perform gap analysis",
            "POST /improvement-plan": "Generate improvement roadmap",
            "POST /metrics/update": "Update compliance metric",
            "GET /metrics/summary": "Get metrics summary",
            "GET /metrics/regressions": "Detect metric regressions",
            "POST /pdca/cycle": "Create PDCA cycle",
            "GET /questionnaire": "Get full assessment questionnaire"
        }
    }


@app.get("/questionnaire")
def get_questionnaire():
    """Get the complete 25-question assessment questionnaire."""
    assessment = MaturityAssessment()

    questions_by_dimension = {}
    for question in assessment.questions:
        if question.dimension not in questions_by_dimension:
            questions_by_dimension[question.dimension] = []

        questions_by_dimension[question.dimension].append({
            "question": question.question,
            "level_indicators": question.level_indicators,
            "weight": question.weight
        })

    return {
        "total_questions": len(assessment.questions),
        "dimensions": list(questions_by_dimension.keys()),
        "questions_per_dimension": 5,
        "questionnaire": questions_by_dimension,
        "instructions": {
            "scoring": "Select the level (1-5) that best describes your current state",
            "overall_rule": "Overall maturity = LOWEST dimension score (weakest link)",
            "time_estimate": "15-20 minutes to complete"
        }
    }


@app.post("/assessment", response_model=AssessmentResponse)
def submit_assessment(request: AssessmentRequest):
    """
    Submit maturity assessment responses and receive comprehensive report.

    The report includes:
    - Scores across all 5 dimensions
    - Overall maturity level (weakest link rule)
    - Limiting dimension identification
    - Specific recommendations for improvement
    - Timeline estimate to reach next level
    """
    try:
        logger.info(f"Processing assessment with {len(request.responses)} responses")

        # Generate report using convenience function
        report = generate_maturity_report(request.responses)

        return AssessmentResponse(**report)

    except ValueError as e:
        logger.error(f"Invalid assessment request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gap-analysis")
def perform_gap_analysis(request: GapAnalysisRequest):
    """
    Perform gap analysis between current and target maturity states.

    Returns:
    - Gaps identified per dimension
    - Priority levels (High/Medium/Low)
    - Effort estimates
    - Recommended sequence for addressing gaps
    """
    try:
        logger.info(f"Performing gap analysis: Target Level {request.target_level}")

        # Calculate current maturity
        assessment = MaturityAssessment()
        assessment.collect_responses(request.current_responses)
        current_scores = assessment.calculate_maturity_scores()

        # Perform gap analysis
        gap_analysis = GapAnalysis(current_scores, request.target_level)
        gaps = gap_analysis.identify_gaps()

        return {
            "current_maturity": current_scores.to_dict(),
            "target_level": request.target_level,
            "gap_analysis": gaps
        }

    except ValueError as e:
        logger.error(f"Invalid gap analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Gap analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/improvement-plan")
def generate_improvement_plan(request: ImprovementPlanRequest):
    """
    Generate comprehensive improvement plan with prioritized roadmap.

    Returns:
    - Current maturity assessment
    - Gap analysis
    - Prioritized initiatives (sorted by impact/effort ratio)
    - Quarterly breakdown
    - Timeline estimates
    """
    try:
        logger.info(
            f"Generating improvement plan: Target L{request.target_level}, "
            f"Max initiatives: {request.max_initiatives}"
        )

        # Use convenience function
        plan = create_improvement_plan(
            request.current_responses,
            request.target_level,
            request.max_initiatives
        )

        return plan

    except ValueError as e:
        logger.error(f"Invalid improvement plan request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Improvement plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metrics/update")
def update_metric(request: MetricUpdateRequest):
    """
    Update a compliance metric with new value.

    Automatically tracks historical values and calculates trend direction
    (improving/stable/degrading).
    """
    try:
        timestamp = None
        if request.timestamp:
            timestamp = datetime.fromisoformat(request.timestamp)

        metrics_tracker.update_metric(
            request.metric_name,
            request.value,
            timestamp
        )

        # Get updated metric info
        summary = metrics_tracker.get_metrics_summary()
        metric_info = summary["metrics"].get(request.metric_name)

        return {
            "status": "updated",
            "metric_name": request.metric_name,
            "value": request.value,
            "metric_info": metric_info
        }

    except Exception as e:
        logger.error(f"Metric update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/summary")
def get_metrics_summary():
    """
    Get summary of all compliance metrics.

    Returns:
    - Current values for all 6 standard metrics
    - Target values
    - Trend direction (improving/stable/degrading)
    - Meeting target status
    """
    try:
        summary = metrics_tracker.get_metrics_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "prometheus_enabled": PROMETHEUS_ENABLED,
            "grafana_enabled": GRAFANA_ENABLED
        }

    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/regressions")
def detect_regressions():
    """
    Detect metrics moving in the wrong direction.

    Returns list of metrics with degrading trends that require investigation.
    """
    try:
        regressions = metrics_tracker.detect_regressions()

        return {
            "timestamp": datetime.now().isoformat(),
            "regressions_detected": len(regressions),
            "regressions": regressions,
            "action_required": len(regressions) > 0
        }

    except Exception as e:
        logger.error(f"Regression detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pdca/cycle")
def create_pdca_cycle(request: PDCACycleRequest):
    """
    Create a PDCA (Plan-Do-Check-Act) cycle for continuous improvement.

    Args:
        cycle_name: Name of the cycle (e.g., "2025-Q1")
        duration_weeks: Cycle duration (typically 12 weeks)
        improvement_plan: Improvement plan from /improvement-plan endpoint

    Returns:
        PDCA cycle with initiatives and timeline
    """
    try:
        logger.info(f"Creating PDCA cycle: {request.cycle_name}")

        # Extract initiatives from improvement plan
        roadmap_data = request.improvement_plan.get("improvement_roadmap", {})
        initiatives_data = roadmap_data.get("initiatives", [])

        # Create PDCA cycle
        cycle = PDCACycle(request.cycle_name, request.duration_weeks)

        # Convert initiative data to Initiative objects
        from src.l3_m4_compliance_maturity import Initiative
        initiatives = [
            Initiative(
                title=init["title"],
                description=f"Initiative for {init['dimension']} dimension",
                dimension=init["dimension"],
                owner=init.get("owner", "TBD"),
                timeline_weeks=init["weeks"],
                impact=init["impact"],
                effort=init["effort"],
                status=init.get("status", "Planned")
            )
            for init in initiatives_data
        ]

        # Plan phase
        cycle.plan(initiatives)

        return {
            "cycle_name": cycle.cycle_name,
            "duration_weeks": cycle.duration_weeks,
            "phase": cycle.phase,
            "start_date": cycle.start_date.isoformat(),
            "initiatives": [
                {
                    "title": i.title,
                    "dimension": i.dimension,
                    "timeline_weeks": i.timeline_weeks,
                    "impact": i.impact,
                    "effort": i.effort,
                    "status": i.status,
                    "start_date": i.start_date.isoformat() if i.start_date else None
                }
                for i in cycle.initiatives
            ],
            "next_actions": [
                "Execute initiatives (Do phase)",
                "Track metrics weekly",
                f"Review results at week {request.duration_weeks} (Check phase)",
                "Plan next cycle based on learnings (Act phase)"
            ]
        }

    except Exception as e:
        logger.error(f"PDCA cycle creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    config = get_config_summary()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "metrics_tracker_initialized": metrics_tracker is not None,
        "total_metrics": len(metrics_tracker.metrics) if metrics_tracker else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
