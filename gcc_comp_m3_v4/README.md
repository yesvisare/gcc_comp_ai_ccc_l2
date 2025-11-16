# L3 M3.4: Incident Response & Breach Notification

A production-ready incident response and breach notification system for GCC compliance environments, featuring 4-tier incident classification, 6-phase response workflow, and automated GDPR/DPDPA breach notification.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:** L3 M3.1-M3.3 (Compliance Monitoring, Automated Testing, Audit Logging)
**Service:** None (local processing only - no external API dependencies)

## What You'll Build

Build a comprehensive incident response system that automates the detection, classification, containment, and notification workflow for security and compliance incidents in multi-tenant RAG environments.

**Key Capabilities:**
- **4-Tier Incident Classification:** Automatically classify incidents as P0 (Critical), P1 (High), P2 (Medium), or P3 (Low) based on impact assessment
- **6-Phase Response Workflow:** Structured workflow from Detection → Containment → Investigation → Eradication → Recovery → Post-Mortem
- **Automated Breach Notification:** GDPR Article 33/34 and DPDPA-compliant breach notification with 72-hour deadline tracking
- **Multi-Tenant Isolation:** Separate incident tracking and notification for each tenant in GCC environments
- **Regulatory Compliance:** Built-in support for GDPR, DPDPA, HIPAA, CCPA breach notification requirements
- **Complete Audit Trail:** Every incident phase logged with timestamps, actions, and outcomes

**Success Criteria:**
- Detect and classify incidents in real-time with 100% accuracy
- Complete containment within 15 minutes for P0 incidents
- Meet GDPR 72-hour notification deadline for all data breaches
- Maintain complete audit trail for regulatory compliance
- Support concurrent incident handling across multiple tenants

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                  INCIDENT DETECTION                          │
│  (SIEM, Monitoring, User Reports) → Severity Classification │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│               CLASSIFICATION ENGINE                          │
│  Inputs: User count, Data sensitivity, Service impact       │
│  Output: P0/P1/P2/P3 + Notification requirement            │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              6-PHASE RESPONSE WORKFLOW                       │
│                                                              │
│  1. DETECTION     → Log incident, assign ID, set deadline   │
│  2. CONTAINMENT   → Disable accounts, block IPs, isolate    │
│  3. INVESTIGATION → Analyze logs, identify root cause       │
│  4. ERADICATION   → Patch vulnerabilities, remove threat    │
│  5. RECOVERY      → Restore services, verify integrity      │
│  6. POST-MORTEM   → Document lessons, preventive measures   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           BREACH NOTIFICATION (if required)                  │
│                                                              │
│  GDPR Article 33  → DPA within 72 hours                     │
│  GDPR Article 34  → Users if high risk                      │
│  DPDPA            → Authority + Users within 72 hours       │
│  HIPAA            → HHS + Users within 60 days              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone and Setup
```bash
git clone <repo_url>
cd gcc_comp_m3_v4
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (optional - works with defaults)
```

### 4. Run Tests
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; pytest -v tests/

# Or use script
./scripts/run_tests.ps1
```

### 5. Start API
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; uvicorn app:app --reload

# Or use script
./scripts/run_api.ps1
```

### 6. Explore Notebook
```bash
jupyter lab notebooks/L3_M3_Monitoring_Reporting.ipynb
```

## API Usage Examples

### Detect Incident (Phase 1)
```bash
curl -X POST http://localhost:8000/incidents/detect \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-acme",
    "incident_type": "DATA_BREACH",
    "description": "Unauthorized database access detected",
    "detected_by": "security-monitor",
    "affected_users": ["user-123", "user-456"],
    "affected_data_types": ["email", "phone_number"],
    "data_sensitivity": "CONFIDENTIAL",
    "service_impact": "PARTIAL"
  }'
```

Response:
```json
{
  "status": "success",
  "incident": {
    "incident_id": "INC-tena-a1b2c3d4",
    "severity": "P1_HIGH",
    "notification_required": true,
    "notification_deadline": "2025-11-19T13:35:00Z"
  }
}
```

### Contain Incident (Phase 2)
```bash
curl -X POST http://localhost:8000/incidents/contain \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-tena-a1b2c3d4",
    "containment_actions": [
      "Blocked IP 203.0.113.45",
      "Disabled user accounts",
      "Revoked API tokens"
    ]
  }'
```

### Send Breach Notification
```bash
curl -X POST http://localhost:8000/incidents/notify \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-tena-a1b2c3d4",
    "recipient": "dpa@example.eu",
    "notification_type": "REGULATORY",
    "regulation": "GDPR"
  }'
```

### List Incidents
```bash
# All incidents
curl http://localhost:8000/incidents

# Filter by tenant
curl http://localhost:8000/incidents?tenant_id=tenant-acme

# Filter by severity
curl http://localhost:8000/incidents?severity=P0_CRITICAL

# Filter by status
curl http://localhost:8000/incidents?status=ACTIVE
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Environment name (development, staging, production) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `DEFAULT_TENANT_ID` | No | `tenant-default` | Default tenant ID for single-tenant deployments |
| `NOTIFICATION_EMAIL_FROM` | No | `compliance@example.com` | From address for notifications |
| `DPA_EMAIL` | No | `dpa@example.com` | Data Protection Authority email |
| `GDPR_NOTIFICATION_HOURS` | No | `72` | GDPR notification deadline in hours |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Incident classified incorrectly** | Classification logic doesn't match your risk tolerance | Adjust thresholds in `IncidentClassifier.classify_incident()` - modify user count limits, data sensitivity mappings |
| **Notification deadline missed** | Incident detected but notification sent after 72 hours | Implement automated alerting when incident created with `notification_required=true`. Monitor `notification_deadline` field |
| **Multi-tenant isolation breach** | Incident visible across tenants | Always filter by `tenant_id` when querying incidents. Use `/incidents?tenant_id=X` endpoint |
| **Missing incident phases** | Workflow jumped from Detection to Recovery | Follow 6-phase workflow in order. Each phase updates `current_phase` field. Don't skip phases |
| **Notification content incomplete** | Regulatory authority rejects notification | Review `_generate_notification_content()` method. Ensure all required fields per regulation (GDPR Article 33: nature, categories, approximate number, consequences, measures) |
| **High P0 incident volume** | Too many incidents classified as critical | Tighten P0 criteria in classification logic. Consider increasing thresholds (1000 → 2000 users) |
| **Tests failing on Windows** | Path separator issues | Use `$env:PYTHONPATH=$PWD` in PowerShell. Ensure forward slashes in import paths |
| **Import errors for src module** | PYTHONPATH not set | Run `$env:PYTHONPATH=$PWD` before tests/API. Or use provided PowerShell scripts |
| **Post-mortem not closing incident** | Incident status still "ACTIVE" | Call `close_with_post_mortem()` endpoint. This sets `status="CLOSED"` and `resolution_time` |
| **Cannot retrieve incident by ID** | Incident ID format mismatch | Use full ID from detection response (e.g., `INC-tena-a1b2c3d4`). Check `/incidents/{incident_id}` endpoint |

## Decision Card

**When to use this module:**
- You're building a GCC RAG system handling regulated data (GDPR, HIPAA, DPDPA)
- You need automated incident classification and response workflow
- You're required to notify regulators within 72 hours of data breaches
- You manage multiple tenants with separate incident tracking requirements
- You need audit trail of all incident response actions for compliance
- You want structured workflow enforcement (detection → containment → ... → post-mortem)

**When NOT to use:**
- Your RAG system doesn't handle regulated/sensitive data (use simpler error logging)
- You're in proof-of-concept phase with no production users
- You have <10 users and no regulatory requirements
- You need real-time automated remediation (this module requires human-in-loop for containment/eradication)
- Your incidents are purely operational (not security/compliance-related)

**Trade-offs:**
- **Complexity:** Adds 6-phase workflow overhead vs. simple error handling. Benefit: Complete audit trail, regulatory compliance.
- **Response time:** Human approval required for each phase vs. fully automated remediation. Benefit: Prevents automated actions that worsen incidents.
- **Storage:** Every incident logged permanently vs. rotating logs. Benefit: Complete historical record for audits.
- **Notification overhead:** Must send regulatory notifications for P0/P1 data breaches. Benefit: Avoid regulatory fines (GDPR €20M or 4% revenue).

**Cost considerations:**
- No external API costs (all local processing)
- Storage costs for incident records (~1KB per incident, 10K incidents = 10MB)
- Notification costs (email/postage for user notifications)
- Potential savings: Avoid GDPR fines (€20M), HIPAA fines ($1.8M), CCPA fines ($7,500/violation)

## Troubleshooting

### No External Services Required
This module operates entirely with local processing - no external API keys needed. All incident classification, workflow management, and notification generation happens in-memory or via your database.

### Import Errors
If you see `ModuleNotFoundError: No module named 'src.l3_m3_monitoring_reporting'`, ensure:
```bash
$env:PYTHONPATH=$PWD  # Windows PowerShell
export PYTHONPATH=$PWD  # Linux/Mac
```

### Tests Failing
Run tests with verbose output:
```bash
pytest -v tests/
```

Common test failures:
- **Timezone mismatches:** Tests use UTC timestamps. Ensure system timezone doesn't interfere.
- **Notification deadline assertion fails:** Timing-sensitive test - deadline should be ~72 hours from now.

### API Not Starting
Check for port conflicts:
```bash
# Change port if 8000 is in use
uvicorn app:app --reload --port 8001
```

### Incident Classification Not as Expected
Review classification logic in `IncidentClassifier.classify_incident()`:
```python
# P0 criteria (line 127-133 in __init__.py)
if incident_type in [IncidentType.DATA_BREACH, IncidentType.PII_EXPOSURE]:
    if affected_users_count > 1000 or data_sensitivity in ["CONFIDENTIAL", "RESTRICTED"]:
        return IncidentSeverity.P0
```

Adjust thresholds based on your organization's risk tolerance.

## Architecture

### Core Components

**1. IncidentClassifier** (src/l3_m3_monitoring_reporting/__init__.py:78-156)
- Classifies incidents into 4 severity tiers (P0-P3)
- Determines notification requirements based on GDPR/DPDPA
- Input: Incident type, user count, data sensitivity, service impact
- Output: Severity level + notification deadline

**2. IncidentResponseWorkflow** (src/l3_m3_monitoring_reporting/__init__.py:159-579)
- Manages 6-phase incident response lifecycle
- Enforces workflow order (can't skip phases)
- Tracks incident state changes
- Generates regulatory notifications

**3. FastAPI Application** (app.py)
- REST API endpoints for all workflow phases
- Request validation via Pydantic models
- Multi-tenant query filtering
- Health check with incident statistics

**4. Test Suite** (tests/test_m3_monitoring_reporting.py)
- 30+ test cases covering all workflows
- Classification logic validation
- Multi-tenant isolation tests
- End-to-end workflow tests

### Data Models

**Incident:** Core incident record
```python
{
  "incident_id": "INC-tena-a1b2c3d4",
  "tenant_id": "tenant-acme",
  "severity": "P1_HIGH",
  "incident_type": "DATA_BREACH",
  "description": "...",
  "detected_at": "2025-11-16T13:35:00Z",
  "detected_by": "security-monitor",
  "affected_users": ["user-123", ...],
  "affected_data_types": ["email", "phone"],
  "current_phase": "containment",
  "notification_required": true,
  "notification_deadline": "2025-11-19T13:35:00Z",
  "status": "ACTIVE"
}
```

**NotificationRecord:** Breach notification tracking
```python
{
  "notification_id": "NOT-a1b2c3d4",
  "incident_id": "INC-tena-a1b2c3d4",
  "recipient": "dpa@example.eu",
  "notification_type": "REGULATORY",
  "sent_at": "2025-11-16T14:00:00Z",
  "regulation": "GDPR",
  "notification_content": "...",
  "acknowledgment_received": false
}
```

## Testing

Run full test suite:
```bash
pytest -v tests/
```

Run specific test class:
```bash
pytest tests/test_m3_monitoring_reporting.py::TestIncidentClassifier -v
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html tests/
```

## Production Deployment Checklist

- [ ] Configure `DPA_EMAIL` for your jurisdiction (EU DPA, DPDPA authority, etc.)
- [ ] Set `NOTIFICATION_EMAIL_FROM` to your compliance team email
- [ ] Adjust classification thresholds in `IncidentClassifier` to match risk tolerance
- [ ] Integrate with your SIEM/monitoring system for automated incident detection
- [ ] Set up PagerDuty/Slack alerts for P0 incidents
- [ ] Configure database persistence (currently in-memory - add PostgreSQL/MongoDB)
- [ ] Implement email/SMS integration for breach notifications
- [ ] Train incident response team on 6-phase workflow
- [ ] Schedule quarterly incident response drills
- [ ] Review and update notification templates per legal requirements

## Regulatory Compliance Notes

**GDPR (EU):**
- Article 33: Notify DPA within 72 hours of becoming aware of breach
- Article 34: Notify users if high risk to rights and freedoms
- Fines: Up to €20M or 4% of global revenue

**DPDPA (India):**
- Notify Data Protection Board within reasonable time (typically 72 hours)
- Notify affected users
- Fines: Up to ₹250 crore

**HIPAA (US Healthcare):**
- Notify HHS within 60 days if 500+ individuals affected
- Notify media if 500+ in same state
- Fines: $100-$50,000 per violation

**CCPA (California):**
- No specific deadline, but "without unreasonable delay"
- Fines: $100-$750 per consumer per incident

## Next Module
**L3 M4.1:** Security Hardening & Penetration Testing - Implementing security controls and running automated penetration tests for RAG systems

## Contributing
This module follows TechVoyageHub PractaThon™ standards. See contributing guidelines for code style, testing requirements, and PR process.

## License
MIT License - See LICENSE file for details

## Support
- Documentation: See `/docs` in repository
- Issues: GitHub Issues
- Questions: Discussion forum
