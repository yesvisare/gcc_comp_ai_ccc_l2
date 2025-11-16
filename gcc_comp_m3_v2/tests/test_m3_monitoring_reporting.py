"""
Tests for L3 M3.2: Automated Compliance Testing

Test suite implementing the test pyramid from script:
- Unit Tests (70%): PII Detection tests
- Integration Tests (20%): Policy integration
- End-to-End Tests (10%): Full workflow validation

Target coverage: 95%+ per script specification
"""

import pytest
from src.l3_m3_monitoring_reporting import (
    PIIDetector,
    OPAPolicyEngine,
    ComplianceValidator,
    contains_pii,
    redaction_quality_sufficient,
    check_compliance,
    evaluate_policy,
    run_compliance_tests,
    PIIType
)


# Unit Tests: PII Detection (70% of test suite)

class TestPIIDetection:
    """Unit tests for PII detection patterns."""

    def test_ssn_detection(self):
        """Test SSN pattern detection."""
        detector = PIIDetector()
        result = detector.detect("User SSN: 123-45-6789")

        assert result.has_pii is True
        assert PIIType.SSN in result.pii_types
        assert len(result.violations) > 0

    def test_email_detection(self):
        """Test email pattern detection."""
        detector = PIIDetector()
        result = detector.detect("Contact: john.doe@example.com")

        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types

    def test_credit_card_detection(self):
        """Test credit card pattern detection."""
        detector = PIIDetector()
        result = detector.detect("Card: 4532-1234-5678-9010")

        assert result.has_pii is True
        assert PIIType.CREDIT_CARD in result.pii_types

    def test_phone_detection(self):
        """Test phone number pattern detection."""
        detector = PIIDetector()
        result = detector.detect("Call: (555) 123-4567")

        assert result.has_pii is True
        assert PIIType.PHONE in result.pii_types

    def test_multiple_pii_types(self):
        """Test detection of multiple PII types."""
        detector = PIIDetector()
        text = "SSN: 123-45-6789, Email: test@example.com, Phone: 555-123-4567"
        result = detector.detect(text)

        assert result.has_pii is True
        assert len(result.pii_types) >= 2
        assert PIIType.SSN in result.pii_types
        assert PIIType.EMAIL in result.pii_types

    def test_no_pii_clean_text(self):
        """Test clean text without PII."""
        detector = PIIDetector()
        result = detector.detect("This is a clean document about compliance policies.")

        assert result.has_pii is False
        assert len(result.pii_types) == 0
        assert len(result.violations) == 0

    def test_empty_text(self):
        """Test empty text handling."""
        detector = PIIDetector()
        result = detector.detect("")

        assert result.has_pii is False
        assert len(result.pii_types) == 0

    def test_redacted_marker_detection(self):
        """Test detection of [REDACTED] markers."""
        detector = PIIDetector()
        result = detector.detect("SSN: [REDACTED]")

        assert result.redacted is True

    def test_redaction_quality_full(self):
        """Test fully redacted text quality."""
        detector = PIIDetector()
        text = "SSN: [REDACTED], Email: [REDACTED]"
        is_sufficient, violations = detector.check_redaction_quality(text)

        assert is_sufficient is True
        assert len(violations) == 0

    def test_redaction_quality_partial(self):
        """Test partially redacted text (should fail)."""
        detector = PIIDetector()
        text = "SSN: [REDACTED], but Email: real@example.com"
        is_sufficient, violations = detector.check_redaction_quality(text)

        assert is_sufficient is False
        assert len(violations) > 0

    def test_redaction_quality_none(self):
        """Test unredacted PII (should fail)."""
        detector = PIIDetector()
        text = "SSN: 123-45-6789"
        is_sufficient, violations = detector.check_redaction_quality(text)

        assert is_sufficient is False


# Integration Tests: OPA Policy Evaluation (20% of test suite)

class TestOPAPolicyEngine:
    """Integration tests for OPA policy engine."""

    def test_pii_policy_deny_unredacted(self):
        """Test policy denies unredacted PII."""
        engine = OPAPolicyEngine()
        decision = engine.evaluate_pii_policy({
            'operation': 'embed',
            'text': 'SSN: 123-45-6789',
            'pii_redacted': False
        })

        assert decision['allow'] is False
        assert len(decision['violations']) > 0
        assert decision['pii_detected'] is True

    def test_pii_policy_allow_redacted(self):
        """Test policy allows redacted PII."""
        engine = OPAPolicyEngine()
        decision = engine.evaluate_pii_policy({
            'operation': 'embed',
            'text': 'SSN: [REDACTED]',
            'pii_redacted': True
        })

        assert decision['allow'] is True

    def test_pii_policy_allow_clean(self):
        """Test policy allows clean text."""
        engine = OPAPolicyEngine()
        decision = engine.evaluate_pii_policy({
            'operation': 'query',
            'text': 'What is the compliance policy?',
            'pii_redacted': False
        })

        assert decision['allow'] is True
        assert decision['pii_detected'] is False

    def test_default_deny_principle(self):
        """Test default deny principle for unknown policy."""
        engine = OPAPolicyEngine()
        decision = engine.evaluate(
            input_data={'operation': 'unknown', 'text': 'test'},
            policy='nonexistent'
        )

        assert decision['allow'] is False


# End-to-End Tests: Full Workflow (10% of test suite)

class TestComplianceValidator:
    """End-to-end tests for compliance validation workflow."""

    def test_e2e_embedding_workflow_clean(self):
        """Test end-to-end embedding workflow with clean text."""
        validator = ComplianceValidator()
        result = validator.validate(
            operation='embed',
            text='Financial regulations require proper documentation.'
        )

        assert result.allowed is True
        assert len(result.violations) == 0

    def test_e2e_embedding_workflow_pii(self):
        """Test end-to-end embedding workflow with PII."""
        validator = ComplianceValidator()
        result = validator.validate(
            operation='embed',
            text='Customer SSN is 123-45-6789'
        )

        assert result.allowed is False
        assert len(result.violations) > 0

    def test_e2e_query_workflow(self):
        """Test end-to-end query workflow."""
        validator = ComplianceValidator()
        result = validator.validate(
            operation='query',
            text='What are the GDPR requirements?'
        )

        assert result.allowed is True

    def test_e2e_test_coverage_tracking(self):
        """Test coverage tracking across multiple validations."""
        validator = ComplianceValidator()

        # Run multiple validations
        validator.validate('embed', 'Clean text')
        validator.validate('embed', 'SSN: 123-45-6789')
        validator.validate('query', 'Query text')

        coverage = validator.get_test_coverage()

        assert coverage['total_tests'] == 3
        assert coverage['coverage_pct'] >= 0


# Public API Tests

class TestPublicAPI:
    """Tests for public API functions."""

    def test_contains_pii_function(self):
        """Test contains_pii helper function."""
        assert contains_pii("SSN: 123-45-6789") is True
        assert contains_pii("Clean text") is False

    def test_redaction_quality_function(self):
        """Test redaction_quality_sufficient helper function."""
        assert redaction_quality_sufficient("SSN: [REDACTED]") is True
        assert redaction_quality_sufficient("SSN: 123-45-6789") is False

    def test_check_compliance_function(self):
        """Test check_compliance helper function."""
        result = check_compliance('embed', 'Clean text')
        assert result.allowed is True

        result = check_compliance('embed', 'SSN: 123-45-6789')
        assert result.allowed is False

    def test_evaluate_policy_function(self):
        """Test evaluate_policy helper function."""
        decision = evaluate_policy(
            input_data={'operation': 'embed', 'text': 'test', 'pii_redacted': False},
            policy='pii'
        )

        assert 'allow' in decision
        assert 'violations' in decision


# Regression Tests

class TestRegressionSuite:
    """Regression tests for control persistence."""

    def test_run_compliance_tests_function(self):
        """Test automated compliance test suite execution."""
        results = run_compliance_tests()

        assert results['total_tests'] > 0
        assert 'passed' in results
        assert 'failed' in results
        assert 'pass_rate' in results
        assert results['pass_rate'] >= 0

    def test_ssn_pattern_regression(self):
        """Regression test for SSN pattern detection."""
        # Ensure SSN pattern continues to work
        test_cases = [
            "123-45-6789",
            "987-65-4321",
            "111-22-3333"
        ]

        for ssn in test_cases:
            assert contains_pii(f"SSN: {ssn}") is True

    def test_email_pattern_regression(self):
        """Regression test for email pattern detection."""
        test_cases = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test123@test-domain.org"
        ]

        for email in test_cases:
            assert contains_pii(f"Email: {email}") is True

    def test_policy_decision_consistency(self):
        """Regression test for consistent policy decisions."""
        validator = ComplianceValidator()

        # Same input should produce same result
        text = "SSN: 123-45-6789"
        result1 = validator.validate('embed', text)
        result2 = validator.validate('embed', text)

        assert result1.allowed == result2.allowed
        assert len(result1.violations) == len(result2.violations)


# Performance Tests (Optional)

class TestPerformance:
    """Performance tests for compliance checks."""

    def test_pii_detection_performance(self):
        """Test PII detection performance with large text."""
        detector = PIIDetector()
        large_text = "Clean text " * 1000  # 10k+ characters

        result = detector.detect(large_text)
        # Should complete quickly
        assert result.has_pii is False

    def test_batch_validation_performance(self):
        """Test batch validation performance."""
        validator = ComplianceValidator()
        test_texts = [
            "Clean text sample",
            "Another clean document",
            "Policy compliance guide"
        ] * 10  # 30 validations

        for text in test_texts:
            validator.validate('embed', text)

        coverage = validator.get_test_coverage()
        assert coverage['total_tests'] == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
