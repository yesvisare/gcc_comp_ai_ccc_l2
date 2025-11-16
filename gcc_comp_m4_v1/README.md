# L3 M4.1: Model Cards & AI Governance

Comprehensive AI governance framework for RAG systems implementing model card documentation, bias detection, human-in-the-loop workflows, and governance committee oversight. Aligned with NIST AI Risk Management Framework and EU AI Act requirements.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:** L3 M1-M3 (RAG fundamentals, evaluation, compliance)
**SERVICE:** LOCAL (No external AI APIs - fully offline operation)

## What You'll Build

A production-ready AI governance system that ensures responsible deployment of RAG systems through:

**Three-Pillar Governance Framework:**
- **Fairness:** Statistical bias detection across demographic groups (demographic parity, equalized odds)
- **Transparency:** Complete system documentation via 10-section model cards
- **Accountability:** Governance committee oversight with formal review processes

**Key Capabilities:**
- ✅ Generate standardized model cards (JSON and Markdown export)
- ✅ Detect retrieval bias across user demographics with statistical testing
- ✅ Route high-stakes queries to human reviewers automatically
- ✅ Track governance reviews with committee voting and approval workflows
- ✅ Log incidents with severity-based escalation
- ✅ Maintain audit trails for compliance (NIST AI RMF, EU AI Act, GDPR, DPDPA)

**Success Criteria:**
- Model card documents all 10 required sections
- Bias testing detects >10% quality disparities between groups
- High-risk queries (legal, HR, financial) route to human review
- Governance committee approves changes before deployment
- System operates entirely offline (no external API dependencies)

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI GOVERNANCE WORKFLOW                       │
└─────────────────────────────────────────────────────────────────┘

1. MODEL CARD GENERATION
   ┌────────────────────┐
   │ RAGModelCard       │  Documents system identity, components,
   │ - 10 sections      │  intended use, limitations, governance
   │ - JSON/Markdown    │
   └─────────┬──────────┘
             │
             ▼
2. BIAS DETECTION
   ┌────────────────────┐
   │ BiasDetector       │  Tests demographic parity across groups
   │ - Statistical      │  Flags >10% quality disparities
   │   testing          │
   └─────────┬──────────┘
             │
             ▼
3. HUMAN-IN-THE-LOOP
   ┌────────────────────┐
   │ HITLWorkflow       │  Classifies query risk (HIGH/LOW)
   │ - Risk keywords    │  Routes legal/HR/financial to reviewers
   │ - Review queue     │
   └─────────┬──────────┘
             │
             ▼
4. GOVERNANCE REVIEW
   ┌────────────────────┐
   │ GovernanceReviewer │  Committee votes on changes (75% threshold)
   │ - Committee voting │  Escalates incidents by severity
   │ - Incident tracking│  Maintains approval audit trails
   └────────────────────┘
```

## Quick Start

### 1. Clone and Setup
```bash
git clone <repo_url>
cd gcc_comp_m4_v1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Optional: Enable PostgreSQL or JIRA integrations
# Core governance features work offline without any configuration
```

### 4. Run Tests
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; pytest -q tests/

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
jupyter lab notebooks/L3_M4_Enterprise_Integration.ipynb
```

## API Endpoints

### Model Card Operations
- `POST /model-card/create` - Generate model card with 10 sections

### Bias Detection
- `POST /bias/test` - Run demographic parity test between two groups
- `GET /bias/summary` - Get summary of all bias tests

### Human-in-the-Loop
- `POST /hitl/classify` - Classify query risk and route if needed
- `GET /hitl/queue` - Get review queue status

### Governance
- `POST /governance/submit` - Submit change for committee review
- `POST /governance/vote/{review_id}` - Committee member casts vote
- `POST /governance/incident` - Report AI system incident
- `GET /governance/summary` - Get governance health metrics

### Demo
- `GET /demo/full-workflow` - See complete governance workflow example

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_ENABLED` | No | `false` | Enable PostgreSQL for persistent audit logging |
| `POSTGRES_URL` | If POSTGRES enabled | - | PostgreSQL connection string |
| `JIRA_ENABLED` | No | `false` | Enable JIRA for incident tracking |
| `JIRA_URL` | If JIRA enabled | - | JIRA instance URL |
| `JIRA_TOKEN` | If JIRA enabled | - | JIRA API token |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `NOTEBOOK_MODE` | No | `false` | Suppress logs in Jupyter notebooks |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Governance as Theater** | Documentation created but not enforced; model cards ignored, bias findings unaddressed, committees rubber-stamp decisions | Ensure decision authority: Give committee veto power, include executives, make critical bias block deployments, tie updates to deployment pipelines |
| **Stale Documentation** | Model cards become outdated as systems evolve; version mismatch between system and documentation | Automate updates: Tie model card regeneration to deployment pipelines, enforce version matching (block deploy if card version ≠ system version), quarterly reviews |
| **Bias Testing Without Remediation** | Bias detected (>20% disparity between groups) but no owner, timeline, or action plan to fix | Assign ownership: Each bias finding gets owner and deadline, critical bias (>20%) pauses deployment, track remediation in governance reviews |
| **Human-in-the-Loop Bypassed Under Pressure** | Review requirements abandoned when query queues back up during peak load | Enforce technically: Code-level blocks prevent auto-response for HIGH-risk queries, establish SLAs for review (e.g., 4-hour response), plan capacity for peak loads |
| **Committee Without Authority** | Advisory-only governance cannot block risky deployments; recommendations ignored | Grant decision power: Include executives with veto authority, establish formal appeals process, document escalation paths to CEO/Board level |

## Decision Card

### When to Implement Full Governance

- **High-stakes decisions:** HR (hiring, termination, promotions), legal advice, financial recommendations, medical/health guidance
- **Regulatory requirements:** EU AI Act high-risk classification, FDA/SEC oversight, GDPR/DPDPA data protection mandates
- **Large scale deployment:** 1000+ users, 50+ business units, multinational operations
- **Sensitive data:** PII, financial records, health information, legal documents
- **Parent company mandates:** Corporate governance policies require AI oversight

### When to Use Lightweight Governance

- **Medium-stakes operational decisions:** Internal process questions, knowledge base lookups
- **Moderate scale:** 100-1000 users, limited to single business unit or region
- **Wrong answers are inconvenient but contained:** No legal/financial liability, impact limited
- **No specific AI regulations:** General corporate policies sufficient

### When to Skip Formal Governance

- **Low-stakes informational queries:** "What are office hours?", "Where is the cafeteria?"
- **Very small scale:** <100 users, single team, pilot project
- **Research/proof-of-concept phase:** Pre-production experimentation
- **Existing domain governance covers AI:** Already have HR/Legal review processes that include AI

### Trade-offs

**Cost:**
- **Small GCC** (500 employees, 10 tenants): ₹9.2L annually ($11K USD) - Governance specialist 50%, tooling ₹1L
- **Medium GCC** (2000 employees, 30 tenants): ₹70L annually ($84K USD) - Governance team 2 FTE, committee time ₹25L, tooling ₹5L
- **Large GCC** (5000 employees, 50+ tenants): ₹2.5Cr annually ($300K USD) - Governance team 5 FTE, executive committee time ₹50L, enterprise tooling ₹15L

**ROI Justification:** Preventing single regulatory fine (GDPR €20M, SOX $5M, DPDPA ₹250Cr, EU AI Act €30M) provides 10-100× return on governance investment.

**Latency:**
- Model card generation: <1 second (local JSON/Markdown)
- Bias testing: 2-5 seconds for 1000 samples (pandas/scipy statistical tests)
- Human review: 5-30 minutes depending on queue (blocking for HIGH-risk queries)
- Governance approval: 1-2 weeks for quarterly committee reviews

**Complexity:**
- **Technical:** Low - Standard Python libraries, no external APIs
- **Organizational:** High - Requires committee coordination, cross-functional alignment, executive buy-in
- **Operational:** Medium - Quarterly reviews, bias testing each release, incident tracking

## Regulatory Context

### NIST AI Risk Management Framework

Four core functions implemented:

1. **GOVERN:** Governance committee, model cards, approval workflows
2. **MAP:** Bias detection identifies risks across demographics
3. **MEASURE:** Statistical testing, performance metrics
4. **MANAGE:** Human-in-the-loop, incident escalation, remediation tracking

### EU AI Act Risk Classification

**High-Risk Systems** (This module targets these):
- HR decisions (hiring, termination, promotions)
- Legal systems (case research, contract analysis)
- Credit scoring and financial decisions

**Requirements for High-Risk:**
- ✅ Model card documentation
- ✅ Bias assessment and testing
- ✅ Human oversight capabilities
- ✅ Audit trail logging

**Other Risk Levels:**
- **Unacceptable risk:** Banned (social scoring, real-time biometric surveillance)
- **Limited risk:** Transparency required (chatbots must disclose AI)
- **Minimal risk:** No regulation (informational queries)

### GDPR & DPDPA Compliance

- **Transparency:** Model cards document data sources, processing methods
- **Accountability:** Governance committee provides oversight
- **Right to explanation:** Audit logs enable query traceability
- **Data minimization:** Out-of-scope uses prevent mission creep

## Model Card Structure (10 Sections)

1. **Model Details:** Identity, version, owner, contact
2. **Components:** Embedding model, vector database, LLM, retrieval method, reranker
3. **Intended Use:** Primary use cases, out-of-scope uses (liability protection), target users
4. **Training & Data:** Data sources, volume, preprocessing, known gaps
5. **Performance:** Metrics (precision@5, recall@10), test methodology
6. **Ethical Considerations:** Fairness testing results, bias mitigation steps, privacy measures
7. **Limitations:** Known failure modes, edge cases, quality degradation scenarios
8. **Recommendations:** Usage guidelines, monitoring requirements, human review triggers
9. **Governance:** Review committee, cadence, incident escalation, approval authority
10. **Change Log:** Version history with timestamps and authors

## Bias Detection Categories

### Data Bias
- **Cause:** Document collection over-represents certain departments, regions, or languages
- **Example:** 80% of documents from North America, 20% from Asia-Pacific → retrieval favors NA queries
- **Mitigation:** Balanced data collection, stratified sampling, regional coverage audits

### Retrieval Bias
- **Cause:** Semantic search embeddings favor particular document structures or writing styles
- **Example:** Technical docs rank higher than policy docs even for policy queries
- **Mitigation:** Hybrid search (semantic + keyword), reranking, query reformulation

### Generation Bias
- **Cause:** LLM training data imbalances produce culturally inappropriate or stereotyped outputs
- **Example:** Assumes all engineers are male, all nurses are female
- **Mitigation:** Fine-tuning on balanced data, output filters, human review for sensitive topics

## Troubleshooting

### Module Works Offline
This governance module requires **no external AI service APIs**. It uses only:
- Standard Python libraries (json, datetime, typing)
- pandas and scipy for statistical analysis (local computation)
- Optional PostgreSQL for persistent logging
- Optional JIRA for incident tracking

If you see "service disabled" warnings, this is expected - the core governance features work offline.

### Import Errors
If you see `ModuleNotFoundError: No module named 'src.l3_m4_enterprise_integration'`, ensure:
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD

# Linux/Mac
export PYTHONPATH=$PWD
```

### Tests Failing
Run tests with verbose output to see which assertions fail:
```bash
pytest -v tests/
```

Common issues:
- Path not set (use `$env:PYTHONPATH=$PWD`)
- Missing dependencies (run `pip install -r requirements.txt`)
- Floating point precision (tests use `pytest.approx` for tolerance)

### API Won't Start
Check for port conflicts:
```bash
# Use different port
uvicorn app:app --reload --port 8001
```

Verify dependencies installed:
```bash
pip list | grep fastapi
pip list | grep pydantic
```

## Implementation Sequence

**Phase 1: Documentation** (Weeks 1-2)
- Define governance committee structure
- Create initial model card template
- Document all 10 sections

**Phase 2: Bias Testing** (Week 3)
- Implement BiasDetector with statistical tests
- Run baseline tests across demographics
- Set disparity threshold (recommend 10%)

**Phase 3: Human-in-the-Loop** (Weeks 4-5)
- Define high-risk keywords (legal, HR, financial)
- Build review queue and routing logic
- Establish SLAs for reviewer response time

**Phase 4: Governance Committee** (Week 6)
- Formalize committee membership (Security, Legal, Privacy, Product, Engineering)
- Set approval threshold (recommend 75%)
- Create incident escalation process

**Phase 5: Continuous Governance** (Ongoing)
- Quarterly model card updates
- Bias testing each release
- Committee reviews major changes
- Incident tracking and remediation

## Cost Analysis for GCCs

### Small GCC (500 employees, 10 tenants)
- **Annual Cost:** ₹9.2L ($11K USD)
- **Breakdown:** Governance specialist 50% FTE (₹8L), tooling ₹1L, committee time ₹0.2L
- **Justified by:** Avoiding single DPDPA fine (₹250Cr max)

### Medium GCC (2000 employees, 30 tenants)
- **Annual Cost:** ₹70L ($84K USD)
- **Breakdown:** Governance team 2 FTE (₹40L), committee time ₹25L, tooling ₹5L
- **Justified by:** Avoiding GDPR fine (€20M = ₹180Cr) or SOX penalty ($5M = ₹42Cr)

### Large GCC (5000 employees, 50+ tenants)
- **Annual Cost:** ₹2.5Cr ($300K USD)
- **Breakdown:** Governance team 5 FTE (₹1.5Cr), executive committee ₹50L, enterprise tools ₹15L, audits ₹35L
- **Justified by:** Avoiding EU AI Act fine (€30M = ₹270Cr) or reputational damage

**ROI:** Preventing single major regulatory fine provides 10-100× return on governance investment.

## Learning Objectives

After completing this module, you will:

1. **Understand AI governance principles:** NIST AI RMF four functions (Govern, Map, Measure, Manage), EU AI Act risk classification, responsible AI pillars (fairness, transparency, accountability)

2. **Create comprehensive model cards:** Document all 10 sections (model details, components, intended use, training data, performance, ethical considerations, limitations, recommendations, governance, change log)

3. **Implement bias detection:** Test demographic parity and equalized odds across user groups, flag disparities >10%, use pandas/scipy for statistical significance testing

4. **Design human-in-the-loop workflows:** Classify query risk based on keywords (legal, termination, investment), route HIGH-risk queries to human review queue, maintain audit trails

5. **Build governance review processes:** Establish committee oversight (Security, Legal, Privacy, Product, Engineering), implement voting workflows with approval thresholds, track incidents with severity-based escalation

## Next Module

**L3 M4.2:** Security & Privacy Controls - PII detection, access controls, encryption, compliance with GDPR/DPDPA

## License

MIT License - See LICENSE file for details

## Contributing

This module is part of the TechVoyageHub L3 Production RAG Engineering track. For questions or improvements, contact the AI Engineering team.

---

**Key Insight:** "Out-of-scope uses protect from liability" - Documenting explicit non-approved applications in model cards defends against misuse claims and prevents scope creep.

**Critical Success Factor:** Governance requires decision authority. Advisory-only committees fail - ensure executives with veto power participate, and critical bias findings block deployments.
