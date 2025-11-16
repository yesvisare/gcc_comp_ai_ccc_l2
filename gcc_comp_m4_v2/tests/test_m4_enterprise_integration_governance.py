"""
Tests for L3 M4.2: Vendor Risk Assessment

Tests ALL major functions from the vendor risk assessment framework.
All tests run offline (no external API dependencies).
"""

import pytest
import os
from datetime import datetime, timedelta
from src.l3_m4_enterprise_integration_governance import VendorRiskAssessment


@pytest.fixture
def assessor():
    """Fixture to create fresh VendorRiskAssessment instance for each test"""
    return VendorRiskAssessment()


@pytest.fixture
def low_risk_vendor_inputs():
    """Fixture for low-risk vendor inputs (OpenAI-like)"""
    return {
        'soc2_date': datetime.now() - timedelta(days=180),  # 6 months ago
        'iso27001': True,
        'pentest_date': datetime.now() - timedelta(days=90),  # 3 months ago
        'breaches_count': 0,
        'gdpr_compliant': True,
        'dpa_available': True,
        'data_policy_score': 3,
        'deletion_process': 'automated_verified',
        'access_controls': 'strong',
        'certifications': ['soc2', 'iso27001'],
        'audit_date': datetime.now() - timedelta(days=150),
        'notification_process': 'proactive',
        'violations_count': 0,
        'sla_guarantee': 99.9,
        'actual_uptime_12m': 99.95,
        'support_response_time': '<1h',
        'dr_plan': 'tested_annually',
        'dc_locations': ['US', 'EU', 'Asia'],
        'dc_selectable': True,
        'subproc_locations': ['US', 'EU'],
        'sccs_available': True,
        'localization_support': 'full'
    }


@pytest.fixture
def high_risk_vendor_inputs():
    """Fixture for high-risk vendor inputs"""
    return {
        'soc2_date': datetime.now() - timedelta(days=900),  # 30 months ago (expired)
        'iso27001': False,
        'pentest_date': datetime.now() - timedelta(days=540),  # 18 months ago
        'breaches_count': 3,
        'gdpr_compliant': False,
        'dpa_available': False,
        'data_policy_score': 0,
        'deletion_process': 'unclear',
        'access_controls': 'weak',
        'certifications': [],
        'audit_date': datetime.now() - timedelta(days=900),
        'notification_process': 'reactive',
        'violations_count': 2,
        'sla_guarantee': 99.0,
        'actual_uptime_12m': 98.5,
        'support_response_time': '24h',
        'dr_plan': 'none',
        'dc_locations': ['US'],
        'dc_selectable': False,
        'subproc_locations': [],
        'sccs_available': False,
        'localization_support': 'none'
    }


class TestSecurityEvaluation:
    """Test suite for security evaluation (30% weight)"""

    def test_security_perfect_score(self, assessor, low_risk_vendor_inputs):
        """Test security evaluation with perfect inputs"""
        score, findings = assessor.evaluate_security('TestVendor', low_risk_vendor_inputs)

        assert score == 100.0, "Perfect security inputs should score 100"
        assert len(findings) > 0, "Should have positive findings"
        assert any('✓' in finding for finding in findings), "Should have positive indicators"

    def test_security_no_certifications(self, assessor):
        """Test security evaluation with no certifications"""
        inputs = {
            'soc2_date': None,
            'iso27001': False,
            'pentest_date': None,
            'breaches_count': 0
        }
        score, findings = assessor.evaluate_security('TestVendor', inputs)

        assert score == 30.0, "Only breach-free score (30 points)"
        assert any('✗' in finding for finding in findings), "Should have negative findings"

    def test_security_with_breaches(self, assessor, low_risk_vendor_inputs):
        """Test security evaluation penalizes breaches correctly"""
        low_risk_vendor_inputs['breaches_count'] = 2
        score, findings = assessor.evaluate_security('TestVendor', low_risk_vendor_inputs)

        # Perfect score is 100, minus 20 for 2 breaches = 80
        assert score == 80.0, "Should deduct 10 points per breach"
        assert any('breach' in finding.lower() for finding in findings), "Should mention breaches"


class TestPrivacyEvaluation:
    """Test suite for privacy evaluation (25% weight)"""

    def test_privacy_perfect_score(self, assessor, low_risk_vendor_inputs):
        """Test privacy evaluation with perfect inputs"""
        score, findings = assessor.evaluate_privacy('TestVendor', low_risk_vendor_inputs)

        assert score == 100.0, "Perfect privacy inputs should score 100"
        assert any('GDPR compliant' in finding for finding in findings)

    def test_privacy_no_dpa(self, assessor):
        """Test privacy evaluation without DPA"""
        inputs = {
            'gdpr_compliant': True,
            'dpa_available': False,
            'data_policy_score': 2,
            'deletion_process': 'manual',
            'access_controls': 'basic'
        }
        score, findings = assessor.evaluate_privacy('TestVendor', inputs)

        # Should score: 20 (GDPR no DPA) + 30 (good policy) + 10 (manual deletion) + 5 (basic access) = 65
        assert score == 65.0, "Should score 65 without DPA"
        assert any('no DPA' in finding for finding in findings)

    def test_privacy_no_gdpr(self, assessor):
        """Test privacy evaluation without GDPR compliance"""
        inputs = {
            'gdpr_compliant': False,
            'dpa_available': False,
            'data_policy_score': 1,
            'deletion_process': 'unclear',
            'access_controls': 'weak'
        }
        score, findings = assessor.evaluate_privacy('TestVendor', inputs)

        # Should score: 0 (no GDPR) + 15 (basic policy) + 0 (unclear deletion) + 0 (weak access) = 15
        assert score == 15.0, "Should score low without GDPR"


class TestComplianceEvaluation:
    """Test suite for compliance evaluation (20% weight)"""

    def test_compliance_with_certifications(self, assessor):
        """Test compliance evaluation with multiple certifications"""
        inputs = {
            'certifications': ['hipaa_baa', 'pci_dss', 'fedramp'],
            'audit_date': datetime.now() - timedelta(days=90),
            'notification_process': 'proactive',
            'violations_count': 0
        }
        score, findings = assessor.evaluate_compliance('TestVendor', inputs)

        # Should score: 40 (certs) + 30 (recent audit) + 20 (proactive) + 10 (no violations) = 100
        assert score == 100.0, "Should score 100 with all certifications"
        assert any('HIPAA BAA' in finding for finding in findings)
        assert any('PCI-DSS' in finding for finding in findings)
        assert any('FedRAMP' in finding for finding in findings)

    def test_compliance_no_certifications(self, assessor):
        """Test compliance evaluation without certifications"""
        inputs = {
            'certifications': [],
            'audit_date': datetime.now() - timedelta(days=150),
            'notification_process': 'on_request',
            'violations_count': 0
        }
        score, findings = assessor.evaluate_compliance('TestVendor', inputs)

        # Should score: 0 (no certs) + 30 (recent audit) + 10 (on_request) + 10 (no violations) = 50
        assert score == 50.0, "Should score 50 without certifications"

    def test_compliance_with_violations(self, assessor, low_risk_vendor_inputs):
        """Test compliance evaluation penalizes violations"""
        low_risk_vendor_inputs['violations_count'] = 2
        score, findings = assessor.evaluate_compliance('TestVendor', low_risk_vendor_inputs)

        # Should deduct 20 points for 2 violations
        assert score < 100.0, "Should penalize violations"
        assert any('violation' in finding.lower() for finding in findings)


class TestReliabilityEvaluation:
    """Test suite for reliability evaluation (15% weight)"""

    def test_reliability_perfect_score(self, assessor, low_risk_vendor_inputs):
        """Test reliability evaluation with perfect inputs"""
        score, findings = assessor.evaluate_reliability('TestVendor', low_risk_vendor_inputs)

        assert score == 100.0, "Perfect reliability inputs should score 100"
        assert any('99.9' in finding for finding in findings)

    def test_reliability_missed_sla(self, assessor):
        """Test reliability evaluation when vendor misses SLA"""
        inputs = {
            'sla_guarantee': 99.9,
            'actual_uptime_12m': 98.0,
            'support_response_time': '8h',
            'dr_plan': 'none'
        }
        score, findings = assessor.evaluate_reliability('TestVendor', inputs)

        # Should score: 40 (strong SLA) + 0 (missed SLA) + 0 (slow support) + 0 (no DR) = 40
        assert score == 40.0, "Should score low when missing SLA"
        assert any('missed SLA' in finding for finding in findings)

    def test_reliability_weak_sla(self, assessor):
        """Test reliability evaluation with weak SLA"""
        inputs = {
            'sla_guarantee': 99.0,
            'actual_uptime_12m': 99.1,
            'support_response_time': '24h',
            'dr_plan': 'documented'
        }
        score, findings = assessor.evaluate_reliability('TestVendor', inputs)

        # Should score: 0 (weak SLA) + 30 (met SLA) + 0 (slow support) + 5 (documented DR) = 35
        assert score == 35.0, "Should score low with weak SLA"


class TestDataResidencyEvaluation:
    """Test suite for data residency evaluation (10% weight)"""

    def test_data_residency_perfect_score(self, assessor, low_risk_vendor_inputs):
        """Test data residency evaluation with perfect inputs"""
        score, findings = assessor.evaluate_data_residency('TestVendor', low_risk_vendor_inputs)

        assert score == 100.0, "Perfect data residency inputs should score 100"
        assert any('customer-selectable' in finding.lower() for finding in findings)

    def test_data_residency_no_disclosure(self, assessor):
        """Test data residency evaluation without location disclosure"""
        inputs = {
            'dc_locations': [],
            'dc_selectable': False,
            'subproc_locations': [],
            'sccs_available': False,
            'localization_support': 'none'
        }
        score, findings = assessor.evaluate_data_residency('TestVendor', inputs)

        assert score == 0.0, "Should score 0 without location disclosure"
        assert any('unknown' in finding.lower() for finding in findings)

    def test_data_residency_with_sccs(self, assessor):
        """Test data residency evaluation with SCCs"""
        inputs = {
            'dc_locations': ['US', 'EU'],
            'dc_selectable': False,
            'subproc_locations': ['US', 'EU'],
            'sccs_available': True,
            'localization_support': 'partial'
        }
        score, findings = assessor.evaluate_data_residency('TestVendor', inputs)

        # Should score: 20 (fixed DC with EU) + 30 (subproc disclosed) + 20 (SCCs) + 5 (partial local) = 75
        assert score == 75.0, "Should score 75 with SCCs"
        assert any('SCCs' in finding or 'Contractual Clauses' in finding for finding in findings)


class TestOverallRiskCalculation:
    """Test suite for overall risk calculation"""

    def test_overall_risk_low_risk_vendor(self, assessor, low_risk_vendor_inputs):
        """Test overall risk calculation for low-risk vendor"""
        result = assessor.calculate_overall_risk('OpenAI', low_risk_vendor_inputs)

        assert result['overall_score'] >= 90.0, "Should score as low risk"
        assert result['risk_level'] == "LOW RISK"
        assert 'APPROVED' in result['recommendation']
        assert 'vendor' in result
        assert 'assessment_date' in result
        assert 'category_scores' in result

    def test_overall_risk_high_risk_vendor(self, assessor, high_risk_vendor_inputs):
        """Test overall risk calculation for high-risk vendor"""
        result = assessor.calculate_overall_risk('RiskyVendor', high_risk_vendor_inputs)

        assert result['overall_score'] < 50.0, "Should score as critical/high risk"
        assert result['risk_level'] in ["CRITICAL RISK", "HIGH RISK"]
        assert len(result['findings']) == 5, "Should have findings for all 5 categories"

    def test_overall_risk_weighted_calculation(self, assessor):
        """Test that weighted average is calculated correctly"""
        # Create inputs with perfect privacy (25% weight) but zero everything else
        inputs = {
            'soc2_date': None, 'iso27001': False, 'pentest_date': None, 'breaches_count': 10,  # Security: 0
            'gdpr_compliant': True, 'dpa_available': True, 'data_policy_score': 3,  # Privacy: 100
            'deletion_process': 'automated_verified', 'access_controls': 'strong',
            'certifications': [], 'audit_date': None, 'notification_process': 'reactive', 'violations_count': 5,  # Compliance: low
            'sla_guarantee': 90.0, 'actual_uptime_12m': 89.0, 'support_response_time': '48h', 'dr_plan': 'none',  # Reliability: 0
            'dc_locations': [], 'dc_selectable': False, 'subproc_locations': [],  # Data Residency: 0
            'sccs_available': False, 'localization_support': 'none'
        }

        result = assessor.calculate_overall_risk('TestVendor', inputs)

        # Privacy is 100 with 25% weight = 25 points contribution
        # Should be roughly 25-30 points overall (some compliance/other points)
        assert 20.0 <= result['overall_score'] <= 40.0, "Should reflect weighted calculation"

    def test_vendor_storage(self, assessor, low_risk_vendor_inputs):
        """Test that assessments are stored correctly"""
        assessor.calculate_overall_risk('Vendor1', low_risk_vendor_inputs)
        assessor.calculate_overall_risk('Vendor2', low_risk_vendor_inputs)

        assert len(assessor.vendors) == 2, "Should store both vendor assessments"
        assert 'Vendor1' in assessor.vendors
        assert 'Vendor2' in assessor.vendors


class TestReportGeneration:
    """Test suite for report generation"""

    def test_generate_report_empty(self, assessor):
        """Test report generation with no assessments"""
        report = assessor.generate_report()

        assert 'error' in report, "Should return error when no assessments"

    def test_generate_report_dict(self, assessor, low_risk_vendor_inputs):
        """Test report generation in dict format"""
        assessor.calculate_overall_risk('Vendor1', low_risk_vendor_inputs)
        assessor.calculate_overall_risk('Vendor2', low_risk_vendor_inputs)

        report = assessor.generate_report(output_format='dict')

        assert isinstance(report, list), "Should return list of dicts"
        assert len(report) == 2, "Should include both vendors"
        assert 'Vendor' in report[0]
        assert 'Overall Score' in report[0]

    def test_generate_report_dataframe(self, assessor, low_risk_vendor_inputs):
        """Test report generation in dataframe format"""
        assessor.calculate_overall_risk('Vendor1', low_risk_vendor_inputs)

        report = assessor.generate_report(output_format='dataframe')

        assert hasattr(report, 'shape'), "Should return pandas DataFrame"
        assert len(report) == 1, "Should have 1 row"
        assert 'Vendor' in report.columns

    def test_report_sorting(self, assessor, low_risk_vendor_inputs, high_risk_vendor_inputs):
        """Test that report sorts vendors by risk score"""
        assessor.calculate_overall_risk('LowRiskVendor', low_risk_vendor_inputs)
        assessor.calculate_overall_risk('HighRiskVendor', high_risk_vendor_inputs)

        report = assessor.generate_report(output_format='dict')

        # Should be sorted descending by score (lowest risk first)
        assert report[0]['Overall Score'] > report[1]['Overall Score']
        assert report[0]['Vendor'] == 'LowRiskVendor'


class TestCategoryWeights:
    """Test suite for category weights"""

    def test_weights_sum_to_one(self, assessor):
        """Test that category weights sum to 1.0"""
        total_weight = sum(assessor.WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001, "Weights should sum to 1.0"

    def test_security_highest_weight(self, assessor):
        """Test that security has highest weight (30%)"""
        assert assessor.WEIGHTS['security'] == 0.30
        assert assessor.WEIGHTS['security'] > assessor.WEIGHTS['privacy']
        assert assessor.WEIGHTS['security'] > assessor.WEIGHTS['compliance']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
