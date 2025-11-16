"""
FastAPI application for L3 M4.1: Model Cards & AI Governance

Provides REST API endpoints for:
- Generating model cards for RAG systems
- Running bias detection tests
- Managing human-in-the-loop workflows
- Tracking governance reviews

SERVICE: LOCAL (No external AI APIs - fully offline operation)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional
import os

from src.l3_m4_enterprise_integration import (
    RAGModelCard,
    BiasDetector,
    HumanInTheLoopWorkflow,
    GovernanceReviewer
)
from config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M4.1: AI Governance API",
    description="Model Cards, Bias Detection, and Governance Workflows for RAG Systems",
    version="1.0.0"
)

# Initialize global instances
bias_detector = BiasDetector(disparity_threshold=0.10)
hitl_workflow = HumanInTheLoopWorkflow()
governance_reviewer = GovernanceReviewer(
    committee_members=["Security", "Legal", "Privacy", "Product", "Engineering"],
    review_cadence="Quarterly",
    approval_threshold=0.75
)


# ============================================================================
# Pydantic Models
# ============================================================================

class ModelCardRequest(BaseModel):
    """Request to create a model card"""
    model_name: str
    model_version: str
    model_owner: str
    contact_email: str
    embedding_model: str
    vector_database: str
    generation_model: str
    retrieval_method: str
    primary_use_cases: List[str]
    out_of_scope_uses: List[str]


class BiasTestRequest(BaseModel):
    """Request to run bias detection test"""
    group_a_scores: List[float] = Field(..., description="Quality scores for first group")
    group_b_scores: List[float] = Field(..., description="Quality scores for second group")
    group_a_name: str = Field(default="Group A", description="Label for first group")
    group_b_name: str = Field(default="Group B", description="Label for second group")


class QueryClassificationRequest(BaseModel):
    """Request to classify query risk"""
    query: str
    user_context: Optional[Dict[str, str]] = None


class GovernanceReviewRequest(BaseModel):
    """Request to submit change for governance review"""
    change_type: str
    description: str
    impact_assessment: str
    submitted_by: str


class VoteRequest(BaseModel):
    """Committee member vote on a review"""
    committee_member: str
    vote: str = Field(..., pattern="^(approve|reject)$")
    comments: Optional[str] = None


class IncidentRequest(BaseModel):
    """Report an AI system incident"""
    incident_type: str
    description: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    reported_by: str


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    config = get_config()
    return {
        "status": "healthy",
        "module": "L3_M4_Enterprise_Integration",
        "service": "LOCAL (offline operation)",
        "config": config,
        "capabilities": [
            "Model card generation",
            "Bias detection",
            "Human-in-the-loop workflows",
            "Governance review processes"
        ]
    }


# ============================================================================
# Model Card Endpoints
# ============================================================================

@app.post("/model-card/create")
def create_model_card(request: ModelCardRequest):
    """
    Create a new model card for a RAG system.

    Returns both JSON and Markdown representations.
    """
    try:
        # Initialize model card
        card = RAGModelCard(
            model_name=request.model_name,
            model_version=request.model_version,
            model_owner=request.model_owner,
            contact_email=request.contact_email
        )

        # Set components
        card.set_components(
            embedding_model=request.embedding_model,
            vector_database=request.vector_database,
            generation_model=request.generation_model,
            retrieval_method=request.retrieval_method
        )

        # Set intended use
        card.set_intended_use(
            primary_use_cases=request.primary_use_cases,
            out_of_scope_uses=request.out_of_scope_uses,
            target_users=["Internal employees", "Authorized partners"],
            use_limitations=["Not for high-stakes decisions without human review"]
        )

        # Add standard recommendations
        card.add_limitation("May produce inconsistent results with ambiguous queries")
        card.add_limitation("Retrieval quality depends on document collection completeness")
        card.add_recommendation("Conduct quarterly bias testing across user demographics")
        card.add_recommendation("Implement human-in-the-loop for high-stakes queries")

        # Set governance
        card.set_governance(
            review_committee=["Security", "Legal", "Privacy", "Product", "Engineering"],
            review_cadence="Quarterly",
            incident_escalation="Report to governance committee via JIRA",
            approval_authority="VP of Engineering and Chief Legal Officer"
        )

        return {
            "status": "success",
            "model_card_json": card.to_json(),
            "model_card_markdown": card.to_markdown()
        }

    except Exception as e:
        logger.error(f"Model card creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Bias Detection Endpoints
# ============================================================================

@app.post("/bias/test")
def test_bias(request: BiasTestRequest):
    """
    Run demographic parity test between two groups.

    Detects if quality differences exceed 10% threshold.
    """
    try:
        result = bias_detector.test_demographic_parity(
            group_a_scores=request.group_a_scores,
            group_b_scores=request.group_b_scores,
            group_a_name=request.group_a_name,
            group_b_name=request.group_b_name
        )
        return result

    except Exception as e:
        logger.error(f"Bias test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bias/summary")
def get_bias_summary():
    """Get summary of all bias tests conducted."""
    return bias_detector.get_summary()


# ============================================================================
# Human-in-the-Loop Endpoints
# ============================================================================

@app.post("/hitl/classify")
def classify_query(request: QueryClassificationRequest):
    """
    Classify query risk level and route if needed.

    HIGH-RISK queries (containing keywords like "legal", "termination", "investment")
    are automatically routed to human review queue.
    """
    try:
        result = hitl_workflow.process_query(
            query=request.query,
            user_context=request.user_context
        )
        return result

    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hitl/queue")
def get_queue_status():
    """Get current human review queue status."""
    return hitl_workflow.get_queue_status()


# ============================================================================
# Governance Endpoints
# ============================================================================

@app.post("/governance/submit")
def submit_for_review(request: GovernanceReviewRequest):
    """
    Submit a change for governance committee review.

    Examples of changes requiring review:
    - Model updates
    - New data sources
    - Algorithm changes
    - Deployment to new user groups
    """
    try:
        result = governance_reviewer.submit_for_review(
            change_type=request.change_type,
            description=request.description,
            impact_assessment=request.impact_assessment,
            submitted_by=request.submitted_by
        )
        return result

    except Exception as e:
        logger.error(f"Submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/governance/vote/{review_id}")
def cast_vote(review_id: int, request: VoteRequest):
    """
    Committee member casts vote on a pending review.

    Requires 75% approval (4 of 5 members) to pass.
    """
    try:
        result = governance_reviewer.cast_vote(
            review_id=review_id,
            committee_member=request.committee_member,
            vote=request.vote,
            comments=request.comments
        )
        return result

    except Exception as e:
        logger.error(f"Vote failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/governance/incident")
def report_incident(request: IncidentRequest):
    """
    Report an AI system incident for governance review.

    Severity levels:
    - low: Minor issue, track for patterns
    - medium: Needs committee review
    - high: Immediate committee attention
    - critical: Escalate to executive team immediately
    """
    try:
        result = governance_reviewer.report_incident(
            incident_type=request.incident_type,
            description=request.description,
            severity=request.severity,
            reported_by=request.reported_by
        )
        return result

    except Exception as e:
        logger.error(f"Incident reporting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/governance/summary")
def get_governance_summary():
    """Get overall governance health metrics."""
    return governance_reviewer.get_governance_summary()


# ============================================================================
# Combined Workflow Example
# ============================================================================

@app.get("/demo/full-workflow")
def demo_full_workflow():
    """
    Demonstrate complete AI governance workflow.

    Shows integration of all components:
    1. Model card documentation
    2. Bias detection testing
    3. Human-in-the-loop classification
    4. Governance review process
    """
    return {
        "workflow": "AI Governance for RAG System Deployment",
        "steps": [
            {
                "step": 1,
                "action": "Create Model Card",
                "endpoint": "POST /model-card/create",
                "purpose": "Document system components, intended use, limitations"
            },
            {
                "step": 2,
                "action": "Run Bias Testing",
                "endpoint": "POST /bias/test",
                "purpose": "Test demographic parity across user groups"
            },
            {
                "step": 3,
                "action": "Configure Human Review",
                "endpoint": "POST /hitl/classify",
                "purpose": "Route high-stakes queries (legal, HR, financial) to reviewers"
            },
            {
                "step": 4,
                "action": "Submit for Governance Approval",
                "endpoint": "POST /governance/submit",
                "purpose": "Get committee approval before deployment"
            },
            {
                "step": 5,
                "action": "Committee Voting",
                "endpoint": "POST /governance/vote/{review_id}",
                "purpose": "5-member committee votes (75% approval required)"
            },
            {
                "step": 6,
                "action": "Monitor and Report",
                "endpoint": "POST /governance/incident",
                "purpose": "Track incidents, update model card quarterly"
            }
        ],
        "regulatory_compliance": [
            "NIST AI RMF (Govern, Map, Measure, Manage)",
            "EU AI Act (High-risk system documentation)",
            "GDPR (Transparency and accountability)",
            "DPDPA (Data protection in India)"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
