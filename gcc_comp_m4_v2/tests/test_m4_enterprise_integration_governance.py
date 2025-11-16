"""
Tests for L3 M4.2: Vendor Risk Assessment

Comprehensive test suite covering all major functionality:
- VendorRiskAssessment (5 category evaluations)
- DPAValidator (12-clause validation)
- SubprocessorRegistry (tracking and risk inheritance)
- ContinuousMonitor (quarterly reviews and expiry tracking)
- Helper functions (ROI, multi-jurisdiction compliance)
"""
import pytest
from datetime import datetime, timedelta
from src.l3_m4_enterprise_integration_governance import (
    VendorRiskAssessment,
    VendorProfile,
    DPAValidator,
    SubprocessorRegistry,
    ContinuousMonitor,
    RiskLevel,
    calculate_roi,
    multi_jurisdiction_compliance_check,
    assess_vendor
)


# Fixtures
@pytest.fixture
def excellent_vendor_profile():
    """Profile for a high-quality vendor (should score 90+)."""
    return VendorProfile(
        name="ExcellentVendor Inc",
        soc2_date=datetime.now() - timedelta(days=180),
        iso27001_certified=True,
        penetration_testing=True,
        breach_count=0,
        gdpr_compliant=True,
        dpa_available=True,
        data_deletion_automated=True,
        sla_guarantee=99.9,
        actual_uptime=99.95,
        data_center_locations=["US", "EU", "India"],
        subprocessors=[{"name": "SubVendor A", "location": "EU", "has_dpa": True}]
    )


@pytest.fixture
def poor_vendor_profile():
    """Profile for a low-quality vendor (should score <50)."""
    return VendorProfile(
        name="PoorVendor LLC",
        soc2_date=None,
        iso27001_certified=False,
        penetration_testing=False,
        breach_count=3,
        gdpr_compliant=False,
        dpa_available=False,
        data_deletion_automated=False,
        sla_guarantee=95.0,
        actual_uptime=94.5,
        data_center_locations=[],
        subprocessors=[]
    )


@pytest.fixture
def sample_dpa_text():
    """Sample DPA text with most essential clauses."""
    return """
    Data Processing Agreement

    1. Processing Scope: This agreement defines the scope of data processing activities.
    2. Purpose Limitation: Data shall be processed only for the lawful purpose specified.
    3. Data Security: The processor shall implement appropriate security measures to protect data.
    4. Subprocessor Approval: Any sub-processor must receive prior written approval.
    5. Data Subject Rights: The processor shall assist with data subject access requests.
    6. Breach Notification: The processor shall notify the controller within 72 hours of any breach.
    7. Data Location: Data shall be stored in approved geographic locations only.
    8. Cross-Border Transfer: International transfers shall comply with Standard Contractual Clauses.
    9. Audit Rights: The controller has the right to audit the processor's compliance.
    10. Data Deletion: Data shall be deleted or returned upon termination.
    11. Liability: The processor shall indemnify the controller for damages.
    12. Termination: This agreement may be terminated with 30 days notice.
    """


# VendorRiskAssessment Tests
class TestVendorRiskAssessment:
    """Test suite for VendorRiskAssessment class."""

    def test_excellent_vendor_scores_high(self, excellent_vendor_profile):
        """Test that excellent vendor achieves high score."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.calculate_overall_score()
        assert score >= 85, f"Expected score >= 85, got {score}"

    def test_poor_vendor_scores_low(self, poor_vendor_profile):
        """Test that poor vendor achieves low score."""
        assessment = VendorRiskAssessment(poor_vendor_profile)
        score = assessment.calculate_overall_score()
        assert score < 50, f"Expected score < 50, got {score}"

    def test_security_evaluation(self, excellent_vendor_profile):
        """Test security category evaluation."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.evaluate_security()
        assert 0 <= score <= 100
        assert score >= 60  # Should score high

    def test_security_breach_penalty(self):
        """Test that security breaches reduce score."""
        profile = VendorProfile(
            name="Breached Vendor",
            breach_count=2,
            soc2_date=datetime.now(),
            iso27001_certified=True,
            penetration_testing=True
        )
        assessment = VendorRiskAssessment(profile)
        score = assessment.evaluate_security()
        assert score < 70  # Breaches should reduce score

    def test_privacy_evaluation(self, excellent_vendor_profile):
        """Test privacy category evaluation."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.evaluate_privacy()
        assert 0 <= score <= 100
        assert score >= 80  # GDPR + DPA should score high

    def test_compliance_evaluation(self, excellent_vendor_profile):
        """Test compliance category evaluation."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.evaluate_compliance()
        assert 0 <= score <= 100

    def test_reliability_evaluation(self, excellent_vendor_profile):
        """Test reliability category evaluation."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.evaluate_reliability()
        assert 0 <= score <= 100
        assert score >= 70  # High SLA should score well

    def test_data_residency_evaluation(self, excellent_vendor_profile):
        """Test data residency category evaluation."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        score = assessment.evaluate_data_residency()
        assert 0 <= score <= 100
        assert score >= 80  # Multiple locations should score well

    def test_risk_level_classification(self):
        """Test risk level determination from scores."""
        profile = VendorProfile(name="Test")
        assessment = VendorRiskAssessment(profile)

        assert assessment.get_risk_level(95) == RiskLevel.LOW
        assert assessment.get_risk_level(80) == RiskLevel.MEDIUM
        assert assessment.get_risk_level(60) == RiskLevel.HIGH
        assert assessment.get_risk_level(40) == RiskLevel.CRITICAL

    def test_detailed_report_structure(self, excellent_vendor_profile):
        """Test that detailed report has correct structure."""
        assessment = VendorRiskAssessment(excellent_vendor_profile)
        report = assessment.get_detailed_report()

        assert "vendor_name" in report
        assert "overall_score" in report
        assert "risk_level" in report
        assert "category_scores" in report
        assert "weights" in report
        assert "recommendation" in report
        assert "assessment_date" in report

        # Check all 5 categories present
        assert len(report["category_scores"]) == 5
        assert "security" in report["category_scores"]
        assert "privacy" in report["category_scores"]
        assert "compliance" in report["category_scores"]
        assert "reliability" in report["category_scores"]
        assert "data_residency" in report["category_scores"]


# DPAValidator Tests
class TestDPAValidator:
    """Test suite for DPAValidator class."""

    def test_validate_complete_dpa(self, sample_dpa_text):
        """Test validation of complete DPA."""
        validator = DPAValidator()
        result = validator.validate_dpa(sample_dpa_text)

        assert "clause_results" in result
        assert "coverage_percentage" in result
        assert "passed" in result
        assert "missing_clauses" in result

        # Should have high coverage
        assert result["coverage_percentage"] >= 90

    def test_validate_incomplete_dpa(self):
        """Test validation of incomplete DPA."""
        validator = DPAValidator()
        incomplete_dpa = "This DPA only mentions data security measures."
        result = validator.validate_dpa(incomplete_dpa)

        assert result["coverage_percentage"] < 50
        assert not result["passed"]
        assert len(result["missing_clauses"]) > 5

    def test_essential_clauses_count(self):
        """Test that validator checks all 12 essential clauses."""
        validator = DPAValidator()
        assert len(validator.ESSENTIAL_CLAUSES) == 12

    def test_empty_dpa(self):
        """Test validation of empty DPA."""
        validator = DPAValidator()
        result = validator.validate_dpa("")

        assert result["coverage_percentage"] == 0
        assert len(result["missing_clauses"]) == 12


# SubprocessorRegistry Tests
class TestSubprocessorRegistry:
    """Test suite for SubprocessorRegistry class."""

    def test_register_subprocessor(self):
        """Test subprocessor registration."""
        registry = SubprocessorRegistry()
        registry.register_subprocessor(
            vendor_name="Vendor A",
            subprocessor_name="Subprocessor X",
            location="US",
            has_dpa=True
        )

        subprocessors = registry.get_subprocessors("Vendor A")
        assert len(subprocessors) == 1
        assert subprocessors[0]["name"] == "Subprocessor X"
        assert subprocessors[0]["location"] == "US"
        assert subprocessors[0]["has_dpa"] is True

    def test_multiple_subprocessors(self):
        """Test registering multiple subprocessors."""
        registry = SubprocessorRegistry()

        for i in range(3):
            registry.register_subprocessor(
                vendor_name="Vendor A",
                subprocessor_name=f"Subprocessor {i}",
                location="US",
                has_dpa=True
            )

        subprocessors = registry.get_subprocessors("Vendor A")
        assert len(subprocessors) == 3

    def test_risk_inheritance_no_subprocessors(self):
        """Test risk inheritance check with no subprocessors."""
        registry = SubprocessorRegistry()
        result = registry.check_risk_inheritance("Vendor A")

        assert not result["has_subprocessors"]
        assert not result["risk_inherited"]
        assert len(result["issues"]) == 0

    def test_risk_inheritance_with_issues(self):
        """Test risk inheritance detection."""
        registry = SubprocessorRegistry()
        registry.register_subprocessor(
            vendor_name="Vendor A",
            subprocessor_name="Risky Subprocessor",
            location="Unknown",
            has_dpa=False  # Missing DPA
        )

        result = registry.check_risk_inheritance("Vendor A")

        assert result["has_subprocessors"]
        assert result["risk_inherited"]
        assert len(result["issues"]) > 0

    def test_risk_inheritance_clean(self):
        """Test risk inheritance with clean subprocessors."""
        registry = SubprocessorRegistry()
        registry.register_subprocessor(
            vendor_name="Vendor A",
            subprocessor_name="Clean Subprocessor",
            location="EU",
            has_dpa=True
        )

        result = registry.check_risk_inheritance("Vendor A")

        assert result["has_subprocessors"]
        assert not result["risk_inherited"]
        assert len(result["issues"]) == 0


# ContinuousMonitor Tests
class TestContinuousMonitor:
    """Test suite for ContinuousMonitor class."""

    def test_schedule_review(self):
        """Test review scheduling."""
        monitor = ContinuousMonitor()
        monitor.schedule_review("Vendor A")

        assert "Vendor A" in monitor.monitoring_schedule
        scheduled_date = monitor.monitoring_schedule["Vendor A"]
        assert scheduled_date > datetime.now()

    def test_get_due_reviews(self):
        """Test getting reviews that are due."""
        monitor = ContinuousMonitor()

        # Schedule review in the past (overdue)
        past_date = datetime.now() - timedelta(days=1)
        monitor.schedule_review("Vendor A", past_date)

        # Schedule review in the future
        future_date = datetime.now() + timedelta(days=30)
        monitor.schedule_review("Vendor B", future_date)

        due_reviews = monitor.get_due_reviews()

        assert "Vendor A" in due_reviews
        assert "Vendor B" not in due_reviews

    def test_certification_expiry_warning(self):
        """Test certification expiry warning."""
        monitor = ContinuousMonitor()

        # SOC 2 expiring in 60 days
        soc2_date = datetime.now() - timedelta(days=305)
        profile = VendorProfile(
            name="Vendor A",
            soc2_date=soc2_date
        )

        result = monitor.check_certification_expiry(profile, warning_days=90)

        assert result["has_warnings"]
        assert len(result["warnings"]) > 0

    def test_certification_expired(self):
        """Test expired certification detection."""
        monitor = ContinuousMonitor()

        # SOC 2 expired 30 days ago
        soc2_date = datetime.now() - timedelta(days=395)
        profile = VendorProfile(
            name="Vendor A",
            soc2_date=soc2_date
        )

        result = monitor.check_certification_expiry(profile)

        assert result["has_warnings"]
        assert any("EXPIRED" in w for w in result["warnings"])


# Helper Functions Tests
class TestHelperFunctions:
    """Test suite for helper functions."""

    def test_calculate_roi_small_scale(self):
        """Test ROI calculation for small vendor count."""
        result = calculate_roi(vendor_count=10)

        assert result["vendor_count"] == 10
        assert result["manual_cost_lakhs"] > 0
        assert result["automated_cost_lakhs"] > 0
        assert "annual_savings_lakhs" in result
        assert "roi_percentage" in result

    def test_calculate_roi_large_scale(self):
        """Test ROI calculation for large vendor count."""
        result = calculate_roi(vendor_count=50)

        # Should show significant savings at scale
        assert result["annual_savings_lakhs"] > 0
        assert result["roi_percentage"] > 0

    def test_multi_jurisdiction_compliance_all_pass(self, excellent_vendor_profile):
        """Test multi-jurisdiction compliance when all pass."""
        result = multi_jurisdiction_compliance_check(
            vendor_profile=excellent_vendor_profile,
            jurisdictions=["GDPR", "CCPA"]
        )

        assert "overall_compliant" in result
        assert "jurisdiction_results" in result
        assert result["overall_compliant"] is True

    def test_multi_jurisdiction_compliance_dpdpa_fail(self):
        """Test DPDPA compliance failure (no India DC)."""
        profile = VendorProfile(
            name="Vendor A",
            gdpr_compliant=True,
            dpa_available=True,
            data_deletion_automated=True,
            data_center_locations=["US", "EU"]  # No India
        )

        result = multi_jurisdiction_compliance_check(
            vendor_profile=profile,
            jurisdictions=["GDPR", "DPDPA"]
        )

        assert not result["overall_compliant"]
        assert not result["jurisdiction_results"]["DPDPA"]["compliant"]

    def test_assess_vendor_comprehensive(self, excellent_vendor_profile):
        """Test comprehensive vendor assessment function."""
        vendor_data = {
            "name": excellent_vendor_profile.name,
            "soc2_date": excellent_vendor_profile.soc2_date,
            "iso27001_certified": excellent_vendor_profile.iso27001_certified,
            "penetration_testing": excellent_vendor_profile.penetration_testing,
            "breach_count": excellent_vendor_profile.breach_count,
            "gdpr_compliant": excellent_vendor_profile.gdpr_compliant,
            "dpa_available": excellent_vendor_profile.dpa_available,
            "data_deletion_automated": excellent_vendor_profile.data_deletion_automated,
            "sla_guarantee": excellent_vendor_profile.sla_guarantee,
            "actual_uptime": excellent_vendor_profile.actual_uptime,
            "data_center_locations": excellent_vendor_profile.data_center_locations,
            "subprocessors": excellent_vendor_profile.subprocessors,
            "dpa_text": "Sample DPA with security, breach notification, and data deletion clauses"
        }

        result = assess_vendor(
            vendor_data=vendor_data,
            include_subprocessors=True,
            jurisdictions=["GDPR", "DPDPA"]
        )

        assert "risk_assessment" in result
        assert "dpa_validation" in result
        assert "subprocessor_analysis" in result
        assert "jurisdiction_compliance" in result
        assert "certification_status" in result
        assert "timestamp" in result


# Edge Cases and Error Handling
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_vendor_profile_minimal(self):
        """Test vendor profile with minimal data."""
        profile = VendorProfile(name="Minimal Vendor")
        assessment = VendorRiskAssessment(profile)
        score = assessment.calculate_overall_score()

        assert 0 <= score <= 100
        assert score < 30  # Should score very low

    def test_perfect_vendor_score(self):
        """Test that perfect vendor achieves near-perfect score."""
        profile = VendorProfile(
            name="Perfect Vendor",
            soc2_date=datetime.now() - timedelta(days=90),
            iso27001_certified=True,
            penetration_testing=True,
            breach_count=0,
            gdpr_compliant=True,
            dpa_available=True,
            data_deletion_automated=True,
            sla_guarantee=99.99,
            actual_uptime=99.99,
            data_center_locations=["US", "EU", "India", "Singapore"],
            subprocessors=[{"name": "Sub", "location": "EU", "has_dpa": True}]
        )

        assessment = VendorRiskAssessment(profile)
        score = assessment.calculate_overall_score()

        assert score >= 90  # Should achieve "Low Risk" status

    def test_empty_jurisdiction_list(self, excellent_vendor_profile):
        """Test with empty jurisdiction list."""
        result = multi_jurisdiction_compliance_check(
            vendor_profile=excellent_vendor_profile,
            jurisdictions=[]
        )

        assert result["overall_compliant"] is True
        assert len(result["jurisdiction_results"]) == 0
