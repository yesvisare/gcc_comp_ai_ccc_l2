"""
FastAPI application for L3 M3.4: Incident Response & Breach Notification

Provides REST API endpoints for incident detection, classification, response workflow,
and breach notification automation.

No external service dependencies - all processing is local.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
import logging
from datetime import datetime

from src.l3_m3_monitoring_reporting import (
    IncidentSeverity,
    ResponsePhase,
    IncidentType,
    Incident,
    NotificationRecord,
    IncidentClassifier,
    IncidentResponseWorkflow
)
from config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M3.4: Incident Response & Breach Notification API",
    description="Production-grade incident response and breach notification system for GCC compliance",
    version="1.0.0"
)

# Global incident response workflow instance
workflow = IncidentResponseWorkflow()

# Request/Response Models
class DetectIncidentRequest(BaseModel):
    """Request model for incident detection"""
    tenant_id: str = Field(..., description="Tenant ID (multi-tenant isolation)")
    incident_type: IncidentType = Field(..., description="Type of incident")
    description: str = Field(..., description="Human-readable description")
    detected_by: str = Field(..., description="User ID or system component")
    affected_users: List[str] = Field(..., description="List of affected user IDs")
    affected_data_types: List[str] = Field(..., description="Types of affected data (PII, financial, etc.)")
    data_sensitivity: Literal["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"] = Field(..., description="Data sensitivity level")
    service_impact: Literal["NONE", "PARTIAL", "FULL"] = Field(..., description="Service availability impact")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant-acme",
                "incident_type": "DATA_BREACH",
                "description": "Unauthorized access to customer PII database",
                "detected_by": "security-monitor",
                "affected_users": ["user-123", "user-456"],
                "affected_data_types": ["email", "phone_number", "address"],
                "data_sensitivity": "CONFIDENTIAL",
                "service_impact": "PARTIAL"
            }
        }


class ContainIncidentRequest(BaseModel):
    """Request model for incident containment"""
    incident_id: str = Field(..., description="Incident ID to contain")
    containment_actions: List[str] = Field(..., description="Actions taken to contain incident")


class InvestigateIncidentRequest(BaseModel):
    """Request model for incident investigation"""
    incident_id: str = Field(..., description="Incident ID to investigate")
    investigation_findings: str = Field(..., description="Summary of investigation results")


class EradicateIncidentRequest(BaseModel):
    """Request model for threat eradication"""
    incident_id: str = Field(..., description="Incident ID")
    eradication_actions: List[str] = Field(..., description="Actions taken to eradicate threat")


class RecoverIncidentRequest(BaseModel):
    """Request model for service recovery"""
    incident_id: str = Field(..., description="Incident ID")
    recovery_steps: List[str] = Field(..., description="Steps taken to recover services")


class CloseIncidentRequest(BaseModel):
    """Request model for closing incident with post-mortem"""
    incident_id: str = Field(..., description="Incident ID to close")
    lessons_learned: str = Field(..., description="Summary of lessons learned")
    preventive_measures: List[str] = Field(..., description="Actions to prevent recurrence")


class SendNotificationRequest(BaseModel):
    """Request model for breach notification"""
    incident_id: str = Field(..., description="Incident ID")
    recipient: str = Field(..., description="Email/contact for notification")
    notification_type: Literal["REGULATORY", "USER", "INTERNAL"] = Field(..., description="Type of notification")
    regulation: str = Field(default="GDPR", description="Applicable regulation")


# API Endpoints
@app.get("/")
def root():
    """Health check endpoint"""
    config = get_config()
    return {
        "status": "healthy",
        "module": "L3_M3_Monitoring_Reporting",
        "version": "1.0.0",
        "environment": config["environment"],
        "active_incidents": len([i for i in workflow.incidents.values() if i.status == "ACTIVE"]),
        "total_incidents": len(workflow.incidents),
        "total_notifications": len(workflow.notifications)
    }


@app.post("/incidents/detect", response_model=Dict[str, Any])
def detect_incident(request: DetectIncidentRequest):
    """
    Phase 1: Detect and classify incident.

    Automatically classifies severity based on impact and determines if
    regulatory notification is required (GDPR Article 33, DPDPA).

    Returns:
        Incident record with assigned ID, severity, and notification deadline
    """
    try:
        incident = workflow.detect_incident(
            tenant_id=request.tenant_id,
            incident_type=request.incident_type,
            description=request.description,
            detected_by=request.detected_by,
            affected_users=request.affected_users,
            affected_data_types=request.affected_data_types,
            data_sensitivity=request.data_sensitivity,
            service_impact=request.service_impact
        )

        return {
            "status": "success",
            "incident": incident.to_dict(),
            "message": f"Incident {incident.incident_id} detected with severity {incident.severity}"
        }

    except Exception as e:
        logger.error(f"Failed to detect incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/contain", response_model=Dict[str, Any])
def contain_incident(request: ContainIncidentRequest):
    """
    Phase 2: Contain incident to prevent further damage.

    Containment actions: disable accounts, revoke tokens, isolate tenant, etc.
    """
    try:
        result = workflow.contain_incident(
            incident_id=request.incident_id,
            containment_actions=request.containment_actions
        )
        return {"status": "success", "result": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Containment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/investigate", response_model=Dict[str, Any])
def investigate_incident(request: InvestigateIncidentRequest):
    """
    Phase 3: Investigate root cause and scope.

    Investigation tasks: analyze logs, interview users, identify attack vector.
    """
    try:
        result = workflow.investigate_incident(
            incident_id=request.incident_id,
            investigation_findings=request.investigation_findings
        )
        return {"status": "success", "result": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/eradicate", response_model=Dict[str, Any])
def eradicate_threat(request: EradicateIncidentRequest):
    """
    Phase 4: Eradicate root cause.

    Eradication actions: patch vulnerabilities, remove malware, reset credentials.
    """
    try:
        result = workflow.eradicate_threat(
            incident_id=request.incident_id,
            eradication_actions=request.eradication_actions
        )
        return {"status": "success", "result": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Eradication failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/recover", response_model=Dict[str, Any])
def recover_services(request: RecoverIncidentRequest):
    """
    Phase 5: Recover normal operations.

    Recovery steps: re-enable services, restore access, verify integrity.
    """
    try:
        result = workflow.recover_services(
            incident_id=request.incident_id,
            recovery_steps=request.recovery_steps
        )
        return {"status": "success", "result": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Recovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/close", response_model=Dict[str, Any])
def close_incident(request: CloseIncidentRequest):
    """
    Phase 6: Close incident with post-mortem.

    Post-mortem includes timeline, root cause, lessons learned, preventive measures.
    """
    try:
        result = workflow.close_with_post_mortem(
            incident_id=request.incident_id,
            lessons_learned=request.lessons_learned,
            preventive_measures=request.preventive_measures
        )
        return {"status": "success", "result": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to close incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/notify", response_model=Dict[str, Any])
def send_notification(request: SendNotificationRequest):
    """
    Send breach notification to authorities or users.

    GDPR Article 33: Notify DPA within 72 hours
    GDPR Article 34: Notify users if high risk
    """
    try:
        notification = workflow.send_breach_notification(
            incident_id=request.incident_id,
            recipient=request.recipient,
            notification_type=request.notification_type,
            regulation=request.regulation
        )

        return {
            "status": "success",
            "notification_id": notification.notification_id,
            "sent_at": notification.sent_at,
            "recipient": notification.recipient,
            "message": f"Notification sent to {notification.recipient}"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incidents/{incident_id}", response_model=Dict[str, Any])
def get_incident(incident_id: str):
    """
    Retrieve incident details by ID.
    """
    incident = workflow.get_incident(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return {
        "status": "success",
        "incident": incident.to_dict()
    }


@app.get("/incidents", response_model=Dict[str, Any])
def list_incidents(
    tenant_id: Optional[str] = None,
    severity: Optional[IncidentSeverity] = None,
    status: Optional[str] = None
):
    """
    List incidents with optional filters.

    Query params:
    - tenant_id: Filter by tenant (multi-tenant isolation)
    - severity: Filter by severity (P0, P1, P2, P3)
    - status: Filter by status (ACTIVE, CLOSED)
    """
    incidents = workflow.list_incidents(
        tenant_id=tenant_id,
        severity=severity,
        status=status
    )

    return {
        "status": "success",
        "count": len(incidents),
        "incidents": [i.to_dict() for i in incidents]
    }


@app.get("/notifications", response_model=Dict[str, Any])
def list_notifications():
    """
    List all breach notifications sent.
    """
    return {
        "status": "success",
        "count": len(workflow.notifications),
        "notifications": [
            {
                "notification_id": n.notification_id,
                "incident_id": n.incident_id,
                "recipient": n.recipient,
                "notification_type": n.notification_type,
                "sent_at": n.sent_at,
                "regulation": n.regulation,
                "acknowledgment_received": n.acknowledgment_received
            }
            for n in workflow.notifications
        ]
    }


@app.get("/health")
def health_check():
    """Extended health check with workflow statistics"""
    config = get_config()

    active_incidents = [i for i in workflow.incidents.values() if i.status == "ACTIVE"]
    p0_incidents = [i for i in active_incidents if i.severity == IncidentSeverity.P0]

    pending_notifications = [
        i for i in workflow.incidents.values()
        if i.notification_required and i.notification_deadline
        and datetime.fromisoformat(i.notification_deadline) > datetime.now(datetime.now().astimezone().tzinfo or None)
    ]

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config["environment"],
        "statistics": {
            "total_incidents": len(workflow.incidents),
            "active_incidents": len(active_incidents),
            "p0_critical_incidents": len(p0_incidents),
            "pending_notifications": len(pending_notifications),
            "total_notifications_sent": len(workflow.notifications)
        },
        "alerts": [
            f"⚠️ {len(p0_incidents)} P0 critical incidents active" if p0_incidents else None,
            f"⚠️ {len(pending_notifications)} notifications pending" if pending_notifications else None
        ]
    }
