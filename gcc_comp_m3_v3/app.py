"""
FastAPI application for L3 M3.3: Audit Logging & SIEM Integration

Provides REST API for:
- Logging RAG audit events
- Querying audit trail
- Verifying hash chain integrity
- Managing retention policies
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from src.l3_m3_monitoring_reporting_compliance import (
    AuditEventType,
    DataClassification,
    CorrelationContext,
    create_audit_logger,
)
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="L3 M3.3: Audit Logging & SIEM Integration",
    description="Production API for RAG system audit logging with SIEM integration",
    version="1.0.0"
)

# Global audit logger instance
audit_logger = None


@app.on_event("startup")
async def startup_event():
    """Initialize audit logger on startup."""
    global audit_logger
    try:
        config = get_config()
        audit_logger = create_audit_logger(config)

        # Initialize PostgreSQL schema
        if audit_logger.postgres_store:
            try:
                audit_logger.postgres_store.create_schema()
                logger.info("Audit logging system initialized successfully")
            except Exception as e:
                logger.warning(f"Schema already exists or creation failed: {e}")

    except Exception as e:
        logger.error(f"Failed to initialize audit logger: {e}")
        # Continue anyway - app can still serve health checks


# Request/Response Models

class AuditEventRequest(BaseModel):
    """Request model for logging audit events."""
    event_type: str = Field(..., description="Event type (RAG_QUERY, RAG_RETRIEVAL, etc.)")
    user_id: str = Field(..., description="User identifier")
    user_role: str = Field(..., description="User role (analyst, engineer, admin)")
    user_department: str = Field(..., description="User department")
    data: Dict[str, Any] = Field(..., description="Event-specific data")
    tenant_id: str = Field(default="default", description="Tenant/department ID")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    data_classification: str = Field(default="INTERNAL", description="Data classification level")
    compliance_flags: List[str] = Field(default=[], description="Compliance flags (SOX_RELEVANT, PII, etc.)")


class AuditEventResponse(BaseModel):
    """Response model for logged events."""
    event_id: str
    timestamp: str
    event_type: str
    correlation_id: str
    current_hash: str
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    postgres_enabled: bool
    s3_enabled: bool
    siem_enabled: bool
    siem_platform: Optional[str]


class QueryAuditRequest(BaseModel):
    """Request model for querying audit logs."""
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = 100


# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns system status and configuration.
    """
    config = get_config()

    return HealthResponse(
        status="healthy",
        service="audit_logging_siem",
        version="1.0.0",
        postgres_enabled=audit_logger is not None and audit_logger.postgres_store is not None,
        s3_enabled=audit_logger is not None and audit_logger.s3_store is not None,
        siem_enabled=audit_logger is not None and audit_logger.siem_integrator is not None,
        siem_platform=config.get("siem_platform") if config.get("siem_enabled") else None
    )


@app.post("/audit/log", response_model=AuditEventResponse)
async def log_audit_event(request: AuditEventRequest):
    """
    Log an audit event.

    Creates immutable audit log entry with:
    - Cryptographic hash chaining
    - PostgreSQL storage
    - Optional S3 archival
    - Optional SIEM streaming

    Args:
        request: Audit event details

    Returns:
        Created event with ID and hash

    Raises:
        HTTPException: If logging fails
    """
    if not audit_logger:
        raise HTTPException(
            status_code=503,
            detail="Audit logger not initialized - check database configuration"
        )

    try:
        # Parse event type
        try:
            event_type = AuditEventType[request.event_type]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type: {request.event_type}. "
                       f"Valid types: {[e.name for e in AuditEventType]}"
            )

        # Parse data classification
        try:
            data_classification = DataClassification[request.data_classification]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_classification: {request.data_classification}. "
                       f"Valid types: {[c.name for c in DataClassification]}"
            )

        # Create correlation context
        context = CorrelationContext(
            tenant_id=request.tenant_id,
            correlation_id=request.correlation_id
        )

        # Log event
        event = audit_logger.log_event(
            event_type=event_type,
            context=context,
            user_id=request.user_id,
            user_role=request.user_role,
            user_department=request.user_department,
            data=request.data,
            data_classification=data_classification,
            compliance_flags=request.compliance_flags
        )

        return AuditEventResponse(
            event_id=event.event_id,
            timestamp=event.timestamp,
            event_type=event.event_type.value,
            correlation_id=event.context.correlation_id,
            current_hash=event.current_hash,
            status="logged"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        raise HTTPException(status_code=500, detail=f"Logging failed: {str(e)}")


@app.post("/audit/query")
async def query_audit_logs(request: QueryAuditRequest):
    """
    Query audit logs.

    Supports filtering by:
    - Tenant ID
    - Correlation ID
    - User ID
    - Event type
    - Time range

    Args:
        request: Query parameters

    Returns:
        List of matching audit events

    Raises:
        HTTPException: If query fails
    """
    if not audit_logger or not audit_logger.postgres_store:
        raise HTTPException(
            status_code=503,
            detail="Audit query not available - PostgreSQL not configured"
        )

    try:
        # Build SQL query
        conditions = []
        params = []

        if request.tenant_id:
            conditions.append("tenant_id = %s")
            params.append(request.tenant_id)

        if request.correlation_id:
            conditions.append("correlation_id = %s")
            params.append(request.correlation_id)

        if request.user_id:
            conditions.append("user_id = %s")
            params.append(request.user_id)

        if request.event_type:
            conditions.append("event_type = %s")
            params.append(request.event_type)

        if request.start_time:
            conditions.append("timestamp >= %s")
            params.append(request.start_time)

        if request.end_time:
            conditions.append("timestamp <= %s")
            params.append(request.end_time)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query_sql = f"""
        SELECT event_id, timestamp, event_type, tenant_id, correlation_id,
               user_id, user_role, user_department, data, data_classification,
               compliance_flags, current_hash
        FROM audit_logs
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT %s
        """
        params.append(request.limit)

        # Execute query
        if not audit_logger.postgres_store._conn:
            audit_logger.postgres_store.connect()

        cursor = audit_logger.postgres_store._conn.cursor()
        cursor.execute(query_sql, params)

        # Format results
        results = []
        for row in cursor.fetchall():
            results.append({
                "event_id": str(row[0]),
                "timestamp": row[1].isoformat(),
                "event_type": row[2],
                "tenant_id": row[3],
                "correlation_id": row[4],
                "user_id": row[5],
                "user_role": row[6],
                "user_department": row[7],
                "data": row[8],
                "data_classification": row[9],
                "compliance_flags": row[10],
                "current_hash": row[11]
            })

        return {
            "count": len(results),
            "events": results,
            "query": {
                "tenant_id": request.tenant_id,
                "correlation_id": request.correlation_id,
                "user_id": request.user_id,
                "event_type": request.event_type,
                "limit": request.limit
            }
        }

    except Exception as e:
        logger.error(f"Failed to query audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/audit/verify/{tenant_id}")
async def verify_hash_chain(tenant_id: str):
    """
    Verify hash chain integrity for a tenant.

    Checks that each event's current_hash matches the next event's previous_hash,
    ensuring no tampering has occurred.

    Args:
        tenant_id: Tenant identifier

    Returns:
        Verification result with any broken links

    Raises:
        HTTPException: If verification fails
    """
    if not audit_logger or not audit_logger.postgres_store:
        raise HTTPException(
            status_code=503,
            detail="Hash verification not available - PostgreSQL not configured"
        )

    try:
        # Get all events for tenant in chronological order
        query_sql = """
        SELECT event_id, timestamp, current_hash, previous_hash
        FROM audit_logs
        WHERE tenant_id = %s
        ORDER BY timestamp ASC
        """

        if not audit_logger.postgres_store._conn:
            audit_logger.postgres_store.connect()

        cursor = audit_logger.postgres_store._conn.cursor()
        cursor.execute(query_sql, (tenant_id,))
        events = cursor.fetchall()

        if not events:
            return {
                "tenant_id": tenant_id,
                "status": "no_events",
                "message": "No events found for tenant"
            }

        # Verify chain
        broken_links = []
        for i in range(1, len(events)):
            prev_event = events[i - 1]
            curr_event = events[i]

            prev_hash = prev_event[2]  # current_hash
            curr_prev_hash = curr_event[3]  # previous_hash

            if prev_hash != curr_prev_hash:
                broken_links.append({
                    "position": i,
                    "prev_event_id": str(prev_event[0]),
                    "curr_event_id": str(curr_event[0]),
                    "expected_hash": prev_hash,
                    "actual_hash": curr_prev_hash
                })

        if broken_links:
            return {
                "tenant_id": tenant_id,
                "status": "chain_broken",
                "total_events": len(events),
                "broken_links": broken_links,
                "message": f"Found {len(broken_links)} broken hash links - possible tampering!"
            }
        else:
            return {
                "tenant_id": tenant_id,
                "status": "chain_valid",
                "total_events": len(events),
                "message": "Hash chain integrity verified - no tampering detected"
            }

    except Exception as e:
        logger.error(f"Failed to verify hash chain: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/audit/stats/{tenant_id}")
async def get_audit_statistics(tenant_id: str):
    """
    Get audit log statistics for a tenant.

    Returns:
    - Total event count
    - Events by type
    - Events by user
    - Events by department
    - Time range

    Args:
        tenant_id: Tenant identifier

    Returns:
        Statistics summary
    """
    if not audit_logger or not audit_logger.postgres_store:
        raise HTTPException(
            status_code=503,
            detail="Statistics not available - PostgreSQL not configured"
        )

    try:
        if not audit_logger.postgres_store._conn:
            audit_logger.postgres_store.connect()

        cursor = audit_logger.postgres_store._conn.cursor()

        # Total count
        cursor.execute(
            "SELECT COUNT(*) FROM audit_logs WHERE tenant_id = %s",
            (tenant_id,)
        )
        total_count = cursor.fetchone()[0]

        # Events by type
        cursor.execute(
            """
            SELECT event_type, COUNT(*)
            FROM audit_logs
            WHERE tenant_id = %s
            GROUP BY event_type
            """,
            (tenant_id,)
        )
        by_type = {row[0]: row[1] for row in cursor.fetchall()}

        # Top users
        cursor.execute(
            """
            SELECT user_id, COUNT(*)
            FROM audit_logs
            WHERE tenant_id = %s
            GROUP BY user_id
            ORDER BY COUNT(*) DESC
            LIMIT 10
            """,
            (tenant_id,)
        )
        top_users = {row[0]: row[1] for row in cursor.fetchall()}

        # Time range
        cursor.execute(
            """
            SELECT MIN(timestamp), MAX(timestamp)
            FROM audit_logs
            WHERE tenant_id = %s
            """,
            (tenant_id,)
        )
        time_range = cursor.fetchone()

        return {
            "tenant_id": tenant_id,
            "total_events": total_count,
            "events_by_type": by_type,
            "top_users": top_users,
            "time_range": {
                "earliest": time_range[0].isoformat() if time_range[0] else None,
                "latest": time_range[1].isoformat() if time_range[1] else None
            }
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
