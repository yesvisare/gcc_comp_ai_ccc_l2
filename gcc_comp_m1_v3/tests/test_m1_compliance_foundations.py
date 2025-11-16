"""
Test suite for L3 M1.3: Regulatory Frameworks Deep Dive

Tests all major compliance analyzers and multi-framework orchestration.
"""

import pytest
from src.l3_m1_compliance_foundations import (
    GDPRAnalyzer,
    SOC2Analyzer,
    ISO27001Analyzer,
    HIPAAAnalyzer,
    MultiFrameworkAnalyzer,
    ComplianceReport,
    GapAnalysis
)


# Test fixtures

@pytest.fixture
def compliant_rag_architecture():
    """Fully compliant RAG architecture for testing."""
    return {
        "components": ["vector_db", "embedding_model", "llm", "api_gateway"],
        "data_flows": ["ingestion", "embedding", "storage", "retrieval", "generation"],
        "storage": {
            "type": "postgres",
            "encryption": "AES-256",
            "location": "EU-West-1",
            "tls_version": "TLS1.3",
            "key_management": True
        },
        "access_control": {
            "method": "RBAC",
            "roles": ["admin", "user", "auditor"],
            "mfa_required": True,
            "unique_user_ids": True,
            "least_privilege": True,
            "emergency_access": True,
            "automatic_logoff": True
        },
        "monitoring": {
            "audit_logs": True,
            "log_retention_days": 2555,
            "continuous_monitoring": True,
            "change_management": True,
            "malware_protection": True
        },
        "apis": ["erasure_api", "data_export", "consent_management", "delete_user_data"],
        "documentation": {
            "processing_records": True,
            "data_flow_diagram": True,
            "security_policy": True,
            "isms_scope": True,
            "risk_assessment": True,
            "statement_of_applicability": True,
            "incident_response_plan": True,
            "privacy_notice": True
        },
        "retention_policy": {
            "customer_data": "7_years",
            "health_records": "6_years"
        },
        "infrastructure": {
            "high_availability": True,
            "backup_strategy": True,
            "disaster_recovery": True,
            "business_continuity_plan": True,
            "facility_access_control": True,
            "device_security": True
        },
        "data_processing": {
            "input_validation": True,
            "error_handling": True,
            "field_filtering": True,
            "pii_detection": True
        },
        "backups": {
            "exclusion_markers": True
        },
        "incident_response": {
            "incident_plan": True,
            "reporting_procedure": True
        },
        "training": {
            "hipaa_training": True
        },
        "vendors": [
            {"name": "OpenAI", "baa_signed": True},
            {"name": "Pinecone", "baa_signed": True}
        ],
        "vector_db": {
            "supports_metadata_deletion": True
        },
        "automated_deletion": True
    }


@pytest.fixture
def minimal_rag_architecture():
    """Minimal RAG architecture with many gaps."""
    return {
        "components": ["vector_db", "llm"],
        "data_flows": ["ingestion", "retrieval"],
        "storage": {"type": "postgres"},
        "access_control": {},
        "monitoring": {},
        "apis": [],
        "documentation": {},
        "retention_policy": {},
        "infrastructure": {},
        "data_processing": {},
        "backups": {},
        "incident_response": {},
        "training": {},
        "vendors": [],
        "vector_db": {}
    }


# GDPR Analyzer Tests

def test_gdpr_analyzer_initialization():
    """Test GDPR analyzer initializes correctly."""
    analyzer = GDPRAnalyzer()
    assert len(analyzer.principles) == 7
    assert len(analyzer.data_subject_rights) == 8


def test_gdpr_compliant_architecture(compliant_rag_architecture):
    """Test GDPR analysis on compliant architecture."""
    analyzer = GDPRAnalyzer()
    gap_analysis = analyzer.analyze(compliant_rag_architecture)

    assert isinstance(gap_analysis, GapAnalysis)
    assert gap_analysis.compliance_score == 1.0
    assert gap_analysis.non_compliant_controls == 0
    assert gap_analysis.total_penalty_risk == 0


def test_gdpr_minimal_architecture(minimal_rag_architecture):
    """Test GDPR analysis identifies gaps in minimal architecture."""
    analyzer = GDPRAnalyzer()
    gap_analysis = analyzer.analyze(minimal_rag_architecture)

    assert gap_analysis.compliance_score < 1.0
    assert gap_analysis.non_compliant_controls > 0
    assert gap_analysis.total_penalty_risk > 0
    assert len(gap_analysis.gaps) > 0


def test_gdpr_article_17_erasure():
    """Test Article 17 erasure check specifically."""
    analyzer = GDPRAnalyzer()

    # Missing erasure
    rag_with_gap = {
        "apis": [],
        "vector_db": {},
        "backups": {}
    }
    check = analyzer._check_article_17_erasure(rag_with_gap)
    assert not check.compliant
    assert check.penalty_risk_eur == 10000000

    # Complete erasure
    rag_compliant = {
        "apis": ["erasure_api"],
        "vector_db": {"supports_metadata_deletion": True},
        "backups": {"exclusion_markers": True}
    }
    check = analyzer._check_article_17_erasure(rag_compliant)
    assert check.compliant


# SOC 2 Analyzer Tests

def test_soc2_analyzer_initialization():
    """Test SOC 2 analyzer initializes correctly."""
    analyzer = SOC2Analyzer()
    assert len(analyzer.trust_service_criteria) == 5


def test_soc2_compliant_architecture(compliant_rag_architecture):
    """Test SOC 2 analysis on compliant architecture."""
    analyzer = SOC2Analyzer()
    gap_analysis = analyzer.analyze(compliant_rag_architecture)

    assert isinstance(gap_analysis, GapAnalysis)
    assert gap_analysis.compliance_score == 1.0
    assert gap_analysis.non_compliant_controls == 0


def test_soc2_minimal_architecture(minimal_rag_architecture):
    """Test SOC 2 analysis identifies gaps."""
    analyzer = SOC2Analyzer()
    gap_analysis = analyzer.analyze(minimal_rag_architecture)

    assert gap_analysis.compliance_score < 1.0
    assert gap_analysis.non_compliant_controls > 0
    assert len(gap_analysis.gaps) > 0


def test_soc2_security_tsc():
    """Test Security TSC check (required)."""
    analyzer = SOC2Analyzer()

    # Missing security controls
    rag_with_gap = {
        "access_control": {},
        "monitoring": {}
    }
    check = analyzer._check_security_tsc(rag_with_gap)
    assert not check.compliant

    # Complete security controls
    rag_compliant = {
        "access_control": {"method": "RBAC", "mfa_required": True},
        "monitoring": {"audit_logs": True}
    }
    check = analyzer._check_security_tsc(rag_compliant)
    assert check.compliant


# ISO 27001 Analyzer Tests

def test_iso27001_analyzer_initialization():
    """Test ISO 27001 analyzer initializes correctly."""
    analyzer = ISO27001Analyzer()
    assert len(analyzer.control_categories) == 14


def test_iso27001_compliant_architecture(compliant_rag_architecture):
    """Test ISO 27001 analysis on compliant architecture."""
    analyzer = ISO27001Analyzer()
    gap_analysis = analyzer.analyze(compliant_rag_architecture)

    assert isinstance(gap_analysis, GapAnalysis)
    assert gap_analysis.compliance_score == 1.0
    assert gap_analysis.non_compliant_controls == 0


def test_iso27001_minimal_architecture(minimal_rag_architecture):
    """Test ISO 27001 analysis identifies gaps."""
    analyzer = ISO27001Analyzer()
    gap_analysis = analyzer.analyze(minimal_rag_architecture)

    assert gap_analysis.compliance_score < 1.0
    assert gap_analysis.non_compliant_controls > 0


def test_iso27001_isms_documentation():
    """Test ISMS documentation check."""
    analyzer = ISO27001Analyzer()

    # Missing ISMS docs
    rag_with_gap = {
        "documentation": {}
    }
    check = analyzer._check_isms_documentation(rag_with_gap)
    assert not check.compliant
    assert check.effort_hours == 80  # High effort for documentation

    # Complete ISMS docs
    rag_compliant = {
        "documentation": {
            "isms_scope": True,
            "security_policy": True,
            "risk_assessment": True,
            "statement_of_applicability": True
        }
    }
    check = analyzer._check_isms_documentation(rag_compliant)
    assert check.compliant


# HIPAA Analyzer Tests

def test_hipaa_analyzer_initialization():
    """Test HIPAA analyzer initializes correctly."""
    analyzer = HIPAAAnalyzer()
    assert len(analyzer.safeguard_categories) == 3


def test_hipaa_compliant_architecture(compliant_rag_architecture):
    """Test HIPAA analysis on compliant architecture."""
    analyzer = HIPAAAnalyzer()
    gap_analysis = analyzer.analyze(compliant_rag_architecture)

    assert isinstance(gap_analysis, GapAnalysis)
    assert gap_analysis.compliance_score == 1.0
    assert gap_analysis.non_compliant_controls == 0


def test_hipaa_minimal_architecture(minimal_rag_architecture):
    """Test HIPAA analysis identifies gaps."""
    analyzer = HIPAAAnalyzer()
    gap_analysis = analyzer.analyze(minimal_rag_architecture)

    assert gap_analysis.compliance_score < 1.0
    assert gap_analysis.non_compliant_controls > 0
    assert gap_analysis.total_penalty_risk > 0


def test_hipaa_baa_requirements():
    """Test BAA requirements check."""
    analyzer = HIPAAAnalyzer()

    # Missing BAAs
    rag_with_gap = {
        "vendors": [
            {"name": "OpenAI", "baa_signed": False},
            {"name": "Pinecone", "baa_signed": False}
        ]
    }
    check = analyzer._check_baa_requirements(rag_with_gap)
    assert not check.compliant
    assert "OpenAI" in check.gap_description

    # Complete BAAs
    rag_compliant = {
        "vendors": [
            {"name": "OpenAI", "baa_signed": True},
            {"name": "Pinecone", "baa_signed": True}
        ]
    }
    check = analyzer._check_baa_requirements(rag_compliant)
    assert check.compliant


# Multi-Framework Analyzer Tests

def test_multi_framework_analyzer_initialization():
    """Test multi-framework analyzer initializes all sub-analyzers."""
    analyzer = MultiFrameworkAnalyzer()
    assert analyzer.gdpr_analyzer is not None
    assert analyzer.soc2_analyzer is not None
    assert analyzer.iso27001_analyzer is not None
    assert analyzer.hipaa_analyzer is not None


def test_multi_framework_all_compliant(compliant_rag_architecture):
    """Test multi-framework analysis on fully compliant architecture."""
    analyzer = MultiFrameworkAnalyzer()
    report = analyzer.analyze_all_frameworks(compliant_rag_architecture)

    assert isinstance(report, ComplianceReport)
    assert report.overall_score == 1.0
    assert report.gdpr_score == 1.0
    assert report.soc2_score == 1.0
    assert report.iso27001_score == 1.0
    assert report.hipaa_score == 1.0
    assert report.audit_ready is True


def test_multi_framework_minimal(minimal_rag_architecture):
    """Test multi-framework analysis on minimal architecture."""
    analyzer = MultiFrameworkAnalyzer()
    report = analyzer.analyze_all_frameworks(minimal_rag_architecture)

    assert report.overall_score < 1.0
    assert report.audit_ready is False
    assert len(report.gap_analyses) == 4  # All 4 frameworks
    assert len(report.remediation_plans) == 4


def test_multi_framework_selective_frameworks(compliant_rag_architecture):
    """Test multi-framework analysis with selective frameworks."""
    analyzer = MultiFrameworkAnalyzer()
    report = analyzer.analyze_all_frameworks(
        compliant_rag_architecture,
        frameworks=["GDPR", "HIPAA"]
    )

    assert len(report.gap_analyses) == 2
    assert "GDPR" in report.gap_analyses
    assert "HIPAA" in report.gap_analyses
    assert "SOC2" not in report.gap_analyses
    assert "ISO27001" not in report.gap_analyses


def test_overlapping_controls_identification(compliant_rag_architecture):
    """Test overlapping controls identification."""
    analyzer = MultiFrameworkAnalyzer()
    overlapping = analyzer._identify_overlapping_controls(compliant_rag_architecture)

    assert len(overlapping) > 0
    assert any("Encryption" in control for control in overlapping)
    assert any("Audit logging" in control for control in overlapping)
    assert any("Access control" in control for control in overlapping)


def test_unique_controls_calculation():
    """Test unique controls calculation after deduplication."""
    analyzer = MultiFrameworkAnalyzer()

    # Mock gap analyses
    gap_analyses = {
        "GDPR": GapAnalysis(
            total_controls_checked=7,
            compliant_controls=7,
            non_compliant_controls=0,
            compliance_score=1.0,
            gaps=[],
            prioritized_gaps=[],
            total_remediation_hours=0,
            total_penalty_risk=0
        ),
        "SOC2": GapAnalysis(
            total_controls_checked=6,
            compliant_controls=6,
            non_compliant_controls=0,
            compliance_score=1.0,
            gaps=[],
            prioritized_gaps=[],
            total_remediation_hours=0,
            total_penalty_risk=0
        )
    }

    unique_controls = analyzer._calculate_unique_controls(gap_analyses)

    # Total: 13 controls, with 40% overlap = 60% unique = ~8 controls
    assert unique_controls < 13
    assert unique_controls >= 7


def test_remediation_plan_generation(minimal_rag_architecture):
    """Test remediation plan generation."""
    analyzer = MultiFrameworkAnalyzer()
    report = analyzer.analyze_all_frameworks(minimal_rag_architecture)

    # Check GDPR remediation plan
    gdpr_plan = report.remediation_plans.get("GDPR")
    assert gdpr_plan is not None
    assert gdpr_plan.timeline_weeks > 0
    assert gdpr_plan.estimated_cost_inr > 0
    assert len(gdpr_plan.quick_wins) >= 0
    assert len(gdpr_plan.priority_gaps) > 0


def test_gap_prioritization():
    """Test gap prioritization by penalty risk and effort."""
    analyzer = GDPRAnalyzer()
    minimal_rag = {
        "apis": [],
        "vector_db": {},
        "backups": {},
        "storage": {},
        "access_control": {},
        "monitoring": {},
        "documentation": {},
        "retention_policy": {},
        "data_processing": {}
    }

    gap_analysis = analyzer.analyze(minimal_rag)

    # Gaps should be prioritized (highest penalty risk first for GDPR)
    if len(gap_analysis.prioritized_gaps) > 1:
        first_gap = gap_analysis.prioritized_gaps[0]
        second_gap = gap_analysis.prioritized_gaps[1]

        # First gap should have higher or equal risk×effort score
        first_score = first_gap.penalty_risk_eur * first_gap.effort_hours
        second_score = second_gap.penalty_risk_eur * second_gap.effort_hours
        assert first_score >= second_score


def test_audit_readiness_threshold():
    """Test audit readiness requires 90%+ compliance."""
    analyzer = MultiFrameworkAnalyzer()

    # Create architecture with 95% compliance
    high_compliance_rag = {
        "components": ["vector_db", "llm"],
        "data_flows": ["ingestion", "retrieval"],
        "storage": {
            "type": "postgres",
            "encryption": "AES-256",
            "tls_version": "TLS1.3"
        },
        "access_control": {
            "method": "RBAC",
            "mfa_required": True,
            "unique_user_ids": True
        },
        "monitoring": {
            "audit_logs": True,
            "log_retention_days": 2555
        },
        "apis": ["erasure_api", "data_export"],
        "documentation": {
            "processing_records": True,
            "security_policy": True,
            "isms_scope": True,
            "risk_assessment": True,
            "statement_of_applicability": True
        },
        "retention_policy": {"customer_data": "7_years"},
        "infrastructure": {
            "high_availability": True,
            "backup_strategy": True,
            "business_continuity_plan": True,
            "facility_access_control": True
        },
        "data_processing": {
            "input_validation": True,
            "error_handling": True
        },
        "backups": {"exclusion_markers": True},
        "incident_response": {
            "incident_plan": True,
            "reporting_procedure": True
        },
        "training": {"hipaa_training": True},
        "vendors": [{"name": "OpenAI", "baa_signed": True}],
        "vector_db": {"supports_metadata_deletion": True}
    }

    report = analyzer.analyze_all_frameworks(high_compliance_rag)

    # With high compliance across all frameworks, should be audit ready
    if report.overall_score >= 0.90:
        assert report.audit_ready is True
    else:
        assert report.audit_ready is False


# Edge Cases and Error Handling

def test_empty_rag_architecture():
    """Test analyzers handle empty architecture gracefully."""
    analyzer = GDPRAnalyzer()
    gap_analysis = analyzer.analyze({})

    assert gap_analysis.compliance_score == 0.0
    assert gap_analysis.non_compliant_controls > 0


def test_partial_rag_architecture():
    """Test analyzers handle partial architecture."""
    analyzer = SOC2Analyzer()
    partial_rag = {
        "storage": {"encryption": "AES-256"},
        "access_control": {"method": "RBAC"}
    }

    gap_analysis = analyzer.analyze(partial_rag)

    # Should identify some gaps but not fail
    assert isinstance(gap_analysis, GapAnalysis)
    assert gap_analysis.compliance_score >= 0.0
    assert gap_analysis.compliance_score <= 1.0


def test_invalid_framework_name():
    """Test multi-framework analyzer handles invalid framework names."""
    analyzer = MultiFrameworkAnalyzer()

    # Should only process valid frameworks
    report = analyzer.analyze_all_frameworks(
        {},
        frameworks=["GDPR", "INVALID_FRAMEWORK"]
    )

    # Should only include GDPR in results
    assert "GDPR" in report.gap_analyses
    assert "INVALID_FRAMEWORK" not in report.gap_analyses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
