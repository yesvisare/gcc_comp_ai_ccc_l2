"""
FastAPI application for L3 M4.3: Change Management & Compliance

Provides REST API endpoints for:
- Change request submission
- Approval routing
- Compliance verification
- Rollback detection
- Audit trail queries
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import Dict, List, Any, Optional
import os

from src.l3_m4_change_management import (
    ChangeType,
    ChangeStatus,
    RiskLevel,
    RollbackTrigger,
    ChangeRequest,
    ChangeClassifier,
    ApprovalRouter,
    ComplianceVerifier,
    RollbackDetector,
    AuditTrailManager,
    ChangeWorkflow,
    init_database
)
from config import get_db_path, is_offline_mode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on startup
db_path = get_db_path()
init_database(db_path)

# Initialize change workflow
workflow = ChangeWorkflow(db_path)
audit_manager = AuditTrailManager(db_path)

app = FastAPI(
    title="L3 M4.3: Change Management & Compliance API",
    description="GCC-grade change management system with 6-phase workflow, CAB approval, and immutable audit trail",
    version="1.0.0"
)

# ============================================================================
# Request/Response Models
# ============================================================================

class CreateChangeRequestModel(BaseModel):
    """Request model for creating new change request"""
    title: str = Field(..., description="Change title")
    description: str = Field(..., description="Detailed description of change")
    requestor: str = Field(..., description="Username of requestor")
    technical_impact: str = Field(..., description="Technical impact assessment")
    compliance_impact: str = Field(..., description="Compliance impact assessment")
    business_impact: str = Field(..., description="Business impact assessment")
    affects_pii: bool = Field(False, description="Does change affect PII processing?")
    affects_financial_data: bool = Field(False, description="Does change affect financial data?")
    affects_sox_controls: bool = Field(False, description="Does change modify SOX controls?")
    affects_gdpr: bool = Field(False, description="Does change affect GDPR compliance?")
    affects_dpdpa: bool = Field(False, description="Does change affect DPDPA compliance?")
    is_emergency: bool = Field(False, description="Is this an emergency change?")


class ApproveChangeModel(BaseModel):
    """Request model for approving change"""
    change_id: str = Field(..., description="Change ID to approve")
    approver: str = Field(..., description="Username of approver")
    conditions: Optional[str] = Field(None, description="Approval conditions (e.g., 'Deploy to 10% canary first')")


class VerifyComplianceModel(BaseModel):
    """Request model for compliance verification"""
    change_id: str = Field(..., description="Change ID to verify")


class CheckRollbackModel(BaseModel):
    """Request model for checking rollback triggers"""
    change_id: str = Field(..., description="Change ID")
    current_metrics: Dict[str, Any] = Field(..., description="Current metrics after deployment")
    baseline_metrics: Dict[str, Any] = Field(..., description="Baseline metrics before deployment")


class ChangeResponseModel(BaseModel):
    """Response model for change request"""
    change_id: str
    title: str
    description: str
    requestor: str
    change_type: str
    risk_level: str
    status: str
    approvers_required: List[str]
    approval_sla_hours: int


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "L3_M4_Change_Management_Compliance",
        "version": "1.0.0",
        "offline_mode": is_offline_mode(),
        "database": db_path
    }


@app.post("/change/create", response_model=ChangeResponseModel)
def create_change_request(request: CreateChangeRequestModel):
    """
    Create new change request (Phase 1: Request & Classification).

    Automatically classifies change as Standard/Normal/Emergency
    and determines required approvers based on risk level.
    """
    try:
        logger.info(f"Creating change request: {request.title}")

        # Create change request
        change_request = workflow.create_change_request(
            title=request.title,
            description=request.description,
            requestor=request.requestor,
            technical_impact=request.technical_impact,
            compliance_impact=request.compliance_impact,
            business_impact=request.business_impact,
            affects_pii=request.affects_pii,
            affects_financial_data=request.affects_financial_data,
            affects_sox_controls=request.affects_sox_controls,
            affects_gdpr=request.affects_gdpr,
            affects_dpdpa=request.affects_dpdpa,
            is_emergency=request.is_emergency
        )

        # Get approval requirements
        approvers = ApprovalRouter.get_required_approvers(
            change_request.change_type,
            change_request.risk_level
        )

        approval_sla = ApprovalRouter.get_approval_sla_hours(
            change_request.change_type
        )

        return ChangeResponseModel(
            change_id=change_request.change_id,
            title=change_request.title,
            description=change_request.description,
            requestor=change_request.requestor,
            change_type=change_request.change_type.value,
            risk_level=change_request.risk_level.value,
            status=change_request.status.value,
            approvers_required=approvers,
            approval_sla_hours=approval_sla
        )

    except Exception as e:
        logger.error(f"Failed to create change request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/change/approve")
def approve_change(request: ApproveChangeModel):
    """
    Approve change request (Phase 3: Approval).

    Records approval in audit trail with timestamp and approver identity.
    """
    try:
        logger.info(f"Approving change {request.change_id} by {request.approver}")

        change_request = workflow.approve_change(
            change_id=request.change_id,
            approver=request.approver,
            conditions=request.conditions
        )

        return {
            "status": "approved",
            "change_id": change_request.change_id,
            "approver": change_request.approver,
            "approval_timestamp": change_request.approval_timestamp,
            "conditions": change_request.approval_conditions
        }

    except ValueError as e:
        logger.error(f"Change not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to approve change: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/change/{change_id}")
def get_change_details(change_id: str):
    """
    Get change request details.

    Returns complete change request with all metadata.
    """
    try:
        logger.info(f"Fetching change details for {change_id}")

        change_request = workflow._load_change_request(change_id)

        return {
            "change_id": change_request.change_id,
            "title": change_request.title,
            "description": change_request.description,
            "requestor": change_request.requestor,
            "change_type": change_request.change_type.value,
            "risk_level": change_request.risk_level.value,
            "status": change_request.status.value,
            "technical_impact": change_request.technical_impact,
            "compliance_impact": change_request.compliance_impact,
            "business_impact": change_request.business_impact,
            "affects_pii": change_request.affects_pii,
            "affects_financial_data": change_request.affects_financial_data,
            "affects_sox_controls": change_request.affects_sox_controls,
            "approver": change_request.approver,
            "approval_timestamp": change_request.approval_timestamp,
            "approval_conditions": change_request.approval_conditions,
            "created_timestamp": change_request.created_timestamp,
            "updated_timestamp": change_request.updated_timestamp
        }

    except ValueError as e:
        logger.error(f"Change not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch change details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/change/{change_id}/audit")
def get_change_audit_trail(change_id: str):
    """
    Get complete audit trail for a change.

    Returns immutable audit trail showing all events from
    request creation to closure.
    """
    try:
        logger.info(f"Fetching audit trail for {change_id}")

        audit_trail = audit_manager.get_change_audit_trail(change_id)

        return {
            "change_id": change_id,
            "audit_events_count": len(audit_trail),
            "audit_trail": audit_trail
        }

    except Exception as e:
        logger.error(f"Failed to fetch audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/verify")
def verify_compliance(request: VerifyComplianceModel):
    """
    Verify compliance controls (Phase 5: Verification).

    Runs compliance tests and returns pass/fail results.
    """
    try:
        logger.info(f"Verifying compliance for change {request.change_id}")

        # Load change request
        change_request = workflow._load_change_request(request.change_id)

        # Verify compliance
        offline = is_offline_mode()
        results = ComplianceVerifier.verify_compliance_controls(
            change_request,
            offline=offline
        )

        return {
            "change_id": request.change_id,
            "compliance_verification": results,
            "overall_status": results["overall_status"],
            "offline_mode": offline
        }

    except ValueError as e:
        logger.error(f"Change not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to verify compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rollback/check")
def check_rollback_triggers(request: CheckRollbackModel):
    """
    Check for rollback triggers (Phase 5: Verification).

    Compares current metrics against baseline to detect
    if automatic rollback should be triggered.
    """
    try:
        logger.info(f"Checking rollback triggers for change {request.change_id}")

        trigger = RollbackDetector.check_rollback_triggers(
            metrics=request.current_metrics,
            baseline_metrics=request.baseline_metrics
        )

        if trigger:
            # Execute rollback
            offline = is_offline_mode()
            rollback_result = RollbackDetector.execute_rollback(
                change_id=request.change_id,
                trigger=trigger,
                offline=offline
            )

            # Log rollback to audit trail
            audit_manager.log_change_event(
                change_id=request.change_id,
                event_type="rollback_executed",
                event_data=rollback_result,
                actor="system_automated"
            )

            return {
                "rollback_triggered": True,
                "trigger": trigger.value,
                "rollback_result": rollback_result
            }
        else:
            return {
                "rollback_triggered": False,
                "message": "No rollback triggers detected - deployment successful"
            }

    except ValueError as e:
        logger.error(f"Change not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to check rollback triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/approval/requirements")
def get_approval_requirements(
    change_type: str,
    risk_level: str
):
    """
    Get approval requirements for a given change type and risk level.

    Useful for understanding approval workflow before submitting change.
    """
    try:
        # Convert strings to enums
        change_type_enum = ChangeType(change_type.lower())
        risk_level_enum = RiskLevel(risk_level.lower())

        approvers = ApprovalRouter.get_required_approvers(
            change_type_enum,
            risk_level_enum
        )

        approval_sla = ApprovalRouter.get_approval_sla_hours(
            change_type_enum
        )

        return {
            "change_type": change_type,
            "risk_level": risk_level,
            "approvers_required": approvers,
            "approval_sla_hours": approval_sla,
            "sla_description": f"{'<1 day' if approval_sla < 24 else f'{approval_sla // 24} business days' if approval_sla < 72 else f'{approval_sla} hours'}"
        }

    except ValueError as e:
        logger.error(f"Invalid change_type or risk_level: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid change_type or risk_level. Valid values: change_type=[standard, normal, emergency], risk_level=[low, medium, high, critical]")
    except Exception as e:
        logger.error(f"Failed to get approval requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
