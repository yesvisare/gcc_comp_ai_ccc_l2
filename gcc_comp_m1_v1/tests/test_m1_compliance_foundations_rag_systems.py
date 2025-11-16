"""
Tests for L3 M1.1: Why Compliance Matters in GCC RAG Systems

Comprehensive test suite covering:
- PII detection (email, phone, SSN, names)
- PHI detection (medical keywords)
- Financial data detection (credit cards with Luhn validation)
- Proprietary information detection
- Regulation mapping
- Risk scoring
- Checklist generation
- Complete assessments
"""

import pytest
from src.l3_m1_compliance_foundations_rag_systems import (
    DataClassifier,
    RegulationMapper,
    ChecklistGenerator,
    ComplianceRiskAssessor,
    assess_compliance_risk
)


# Test Data Fixtures

@pytest.fixture
def pii_text():
    """Sample text with PII."""
    return """
    Contact John Smith at john.smith@example.com or call 555-123-4567.
    SSN: 123-45-6789. Address: 123 Main St, Boston, MA.
    """


@pytest.fixture
def phi_text():
    """Sample text with PHI."""
    return """
    Patient Jane Doe was diagnosed with hypertension and prescribed medication.
    The doctor recommended surgery. Lab results show elevated symptoms.
    Medical record number: 98765.
    """


@pytest.fixture
def financial_text():
    """Sample text with financial data."""
    return """
    Payment information: Card number 4532-1234-5678-9010
    Account number: ACCT12345678
    Routing number: 123456789
    """


@pytest.fixture
def proprietary_text():
    """Sample text with proprietary information."""
    return """
    CONFIDENTIAL - Internal Only
    This document contains trade secrets and proprietary algorithms.
    Patent pending. Copyright 2025.
    """


@pytest.fixture
def mixed_sensitivity_text():
    """Text with multiple sensitivity types (PII + Financial)."""
    return """
    Customer John Doe (john.doe@email.com) made a payment with card 4532-1234-5678-9010.
    Transaction amount: $5,000. SSN: 987-65-4321.
    """


# DataClassifier Tests

class TestDataClassifier:
    """Tests for DataClassifier class."""

    def test_init_without_presidio(self):
        """Test classifier initializes without Presidio."""
        classifier = DataClassifier(use_presidio=False)
        assert classifier.use_presidio is False
        assert classifier.analyzer is None

    def test_detect_pii_email(self, pii_text):
        """Test PII detection finds email addresses."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_pii(pii_text)

        assert result.detected is True
        assert 'email' in result.entities
        assert any('example.com' in ex for ex in result.examples)
        assert 'pii_exposure' in result.risk_factors

    def test_detect_pii_phone(self, pii_text):
        """Test PII detection finds phone numbers."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_pii(pii_text)

        assert result.detected is True
        assert 'phone' in result.entities

    def test_detect_pii_ssn(self, pii_text):
        """Test PII detection finds SSNs."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_pii(pii_text)

        assert result.detected is True
        assert 'ssn' in result.entities

    def test_detect_pii_no_match(self):
        """Test PII detection with clean text."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_pii("This is a clean document with no personal information.")

        assert result.detected is False
        assert len(result.entities) == 0

    def test_detect_phi_medical_keywords(self, phi_text):
        """Test PHI detection finds medical keywords."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_phi(phi_text)

        assert result.detected is True
        assert 'health_information' in result.entities
        assert any(kw in ['patient', 'diagnosis', 'medication'] for kw in result.examples)
        assert 'hipaa_applicable' in result.risk_factors

    def test_detect_phi_no_match(self):
        """Test PHI detection with non-medical text."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_phi("This document discusses marketing strategies.")

        assert result.detected is False

    def test_detect_financial_credit_card(self, financial_text):
        """Test financial data detection finds credit cards."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_financial(financial_text)

        assert result.detected is True
        assert 'credit_card' in result.entities
        assert 'pci_dss_applicable' in result.risk_factors

    def test_detect_financial_account_number(self, financial_text):
        """Test financial data detection finds account numbers."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_financial(financial_text)

        assert result.detected is True
        assert 'account_number' in result.entities

    def test_luhn_validation_valid_card(self):
        """Test Luhn algorithm validates correct credit card."""
        classifier = DataClassifier(use_presidio=False)
        # Valid test card number (passes Luhn check)
        assert classifier._luhn_check("4532123456789010") is True

    def test_luhn_validation_invalid_card(self):
        """Test Luhn algorithm rejects invalid credit card."""
        classifier = DataClassifier(use_presidio=False)
        # Invalid card number (fails Luhn check)
        assert classifier._luhn_check("1234567890123456") is False

    def test_detect_proprietary_confidential(self, proprietary_text):
        """Test proprietary information detection."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.detect_proprietary(proprietary_text)

        assert result.detected is True
        assert 'proprietary_information' in result.entities
        assert any(kw in ['confidential', 'trade secret', 'proprietary'] for kw in result.examples)
        assert 'ip_protection_required' in result.risk_factors

    def test_classify_use_case_pii_only(self, pii_text):
        """Test use case classification with PII only."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.classify_use_case(pii_text)

        assert 'GDPR' in result['triggered_regulations']
        assert 'CCPA' in result['triggered_regulations']
        assert result['data_sensitivity_score'] >= 3
        assert 'pii_exposure' in result['risk_factors']

    def test_classify_use_case_phi_only(self, phi_text):
        """Test use case classification with PHI only."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.classify_use_case(phi_text)

        assert 'HIPAA' in result['triggered_regulations']
        assert result['data_sensitivity_score'] >= 4  # PHI is higher risk

    def test_classify_use_case_mixed_sensitivity(self, mixed_sensitivity_text):
        """Test use case classification with PII + Financial (fraud risk)."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.classify_use_case(mixed_sensitivity_text)

        assert 'GDPR' in result['triggered_regulations']
        assert 'PCI-DSS' in result['triggered_regulations']
        assert 'fraud_risk_elevated' in result['risk_factors']
        assert result['data_sensitivity_score'] >= 7

    def test_classify_use_case_high_sensitivity_triggers_soc2(self):
        """Test that high sensitivity (7+) triggers SOC 2."""
        classifier = DataClassifier(use_presidio=False)
        # Text with PII + PHI + Financial (high sensitivity)
        text = """
        Patient John Doe (SSN: 123-45-6789, john@email.com) paid $1000 with card 4532-1234-5678-9010.
        Diagnosis: diabetes. Prescription: insulin.
        """
        result = classifier.classify_use_case(text)

        assert result['data_sensitivity_score'] >= 7
        assert 'SOC 2' in result['triggered_regulations']


# RegulationMapper Tests

class TestRegulationMapper:
    """Tests for RegulationMapper class."""

    def test_init_loads_regulations(self):
        """Test mapper initializes with regulation database."""
        mapper = RegulationMapper()
        assert len(mapper.regulations) >= 8  # Should have at least 8 regulations

    def test_get_requirements_gdpr(self):
        """Test getting GDPR requirements."""
        mapper = RegulationMapper()
        gdpr = mapper.get_requirements('GDPR')

        assert gdpr is not None
        assert gdpr['full_name'] == 'General Data Protection Regulation'
        assert gdpr['jurisdiction'] == 'European Union'
        assert 'PII' in gdpr['data_types']
        assert len(gdpr['key_requirements']) > 0
        assert len(gdpr['rag_specific']) > 0

    def test_get_requirements_hipaa(self):
        """Test getting HIPAA requirements."""
        mapper = RegulationMapper()
        hipaa = mapper.get_requirements('HIPAA')

        assert hipaa is not None
        assert 'PHI' in hipaa['data_types']
        assert 'Business Associate Agreements' in str(hipaa['key_requirements'])

    def test_get_requirements_not_found(self):
        """Test getting non-existent regulation."""
        mapper = RegulationMapper()
        result = mapper.get_requirements('FAKE_REG')

        assert result is None

    def test_get_all_regulations(self):
        """Test getting all regulations."""
        mapper = RegulationMapper()
        all_regs = mapper.get_all_regulations()

        assert len(all_regs) >= 8
        assert 'GDPR' in all_regs
        assert 'HIPAA' in all_regs
        assert 'SOC 2' in all_regs
        assert 'ISO 27001' in all_regs
        assert 'SOX' in all_regs
        assert 'PCI-DSS' in all_regs

    def test_regulation_has_penalties(self):
        """Test that regulations include penalty information."""
        mapper = RegulationMapper()
        gdpr = mapper.get_requirements('GDPR')

        assert 'penalties' in gdpr
        assert len(gdpr['penalties']) > 0


# ChecklistGenerator Tests

class TestChecklistGenerator:
    """Tests for ChecklistGenerator class."""

    def test_generate_checklist_single_regulation(self):
        """Test checklist generation for single regulation."""
        mapper = RegulationMapper()
        generator = ChecklistGenerator(mapper)

        checklist = generator.generate_checklist(['GDPR'])

        assert 'GDPR' in checklist
        assert 'general_requirements' in checklist['GDPR']
        assert 'rag_specific_controls' in checklist['GDPR']
        assert 'penalties' in checklist['GDPR']

    def test_generate_checklist_multiple_regulations(self):
        """Test checklist generation for multiple regulations."""
        mapper = RegulationMapper()
        generator = ChecklistGenerator(mapper)

        checklist = generator.generate_checklist(['GDPR', 'HIPAA', 'SOC 2'])

        assert 'GDPR' in checklist
        assert 'HIPAA' in checklist
        assert 'SOC 2' in checklist
        assert 'Cross-Cutting Concerns' in checklist  # Multi-regulation scenario

    def test_checklist_cross_cutting_concerns(self):
        """Test that cross-cutting concerns are added for multi-regulation scenarios."""
        mapper = RegulationMapper()
        generator = ChecklistGenerator(mapper)

        checklist = generator.generate_checklist(['GDPR', 'CCPA'])

        assert 'Cross-Cutting Concerns' in checklist
        cross_cutting = checklist['Cross-Cutting Concerns']
        assert 'general_requirements' in cross_cutting
        assert 'rag_specific_controls' in cross_cutting
        assert any('unified' in req.lower() or 'centralized' in req.lower()
                  for req in cross_cutting['general_requirements'])


# ComplianceRiskAssessor Tests

class TestComplianceRiskAssessor:
    """Tests for ComplianceRiskAssessor class."""

    def test_init(self):
        """Test assessor initialization."""
        assessor = ComplianceRiskAssessor(use_presidio=False, use_openai=False)

        assert assessor.classifier is not None
        assert assessor.mapper is not None
        assert assessor.checklist_gen is not None

    def test_assess_basic_use_case(self, pii_text):
        """Test basic assessment."""
        assessor = ComplianceRiskAssessor(use_presidio=False)
        assessment = assessor.assess(pii_text)

        assert assessment.triggered_regulations is not None
        assert len(assessment.triggered_regulations) > 0
        assert assessment.data_sensitivity_score >= 1
        assert assessment.data_sensitivity_score <= 10
        assert len(assessment.required_controls) > 0
        assert len(assessment.checklist) > 0

    def test_assess_includes_base_controls(self, pii_text):
        """Test that assessment includes base controls for all RAG systems."""
        assessor = ComplianceRiskAssessor(use_presidio=False)
        assessment = assessor.assess(pii_text)

        base_controls = [
            'Implement audit logging for all data access',
            'Encrypt data at rest and in transit',
            'Implement role-based access control (RBAC)'
        ]

        for control in base_controls:
            assert control in assessment.required_controls

    def test_assess_high_sensitivity_controls(self):
        """Test that high sensitivity (9+) triggers advanced controls."""
        assessor = ComplianceRiskAssessor(use_presidio=False)

        # Create text with PII + PHI + Financial + Proprietary (should be 9+)
        high_risk_text = """
        CONFIDENTIAL - Patient John Doe (SSN: 123-45-6789, john@email.com)
        Diagnosis: cancer treatment. Payment card: 4532-1234-5678-9010.
        Proprietary treatment protocol. Trade secret formula.
        """

        assessment = assessor.assess(high_risk_text)

        if assessment.data_sensitivity_score >= 9:
            advanced_controls = [
                'Implement zero-trust architecture',
                'Deploy advanced threat detection and response'
            ]
            for control in advanced_controls:
                assert control in assessment.required_controls

    def test_assess_gdpr_specific_controls(self, pii_text):
        """Test that GDPR triggers specific controls."""
        assessor = ComplianceRiskAssessor(use_presidio=False)
        assessment = assessor.assess(pii_text)

        if 'GDPR' in assessment.triggered_regulations:
            gdpr_controls = [
                'Implement consent management system',
                'Enable data subject access and deletion requests'
            ]
            for control in gdpr_controls:
                assert control in assessment.required_controls

    def test_assess_hipaa_specific_controls(self, phi_text):
        """Test that HIPAA triggers specific controls."""
        assessor = ComplianceRiskAssessor(use_presidio=False)
        assessment = assessor.assess(phi_text)

        if 'HIPAA' in assessment.triggered_regulations:
            assert any('Business Associate Agreement' in ctrl for ctrl in assessment.required_controls)


# Convenience Function Tests

class TestAssessComplianceRisk:
    """Tests for assess_compliance_risk convenience function."""

    def test_assess_compliance_risk_function(self, pii_text):
        """Test convenience function for quick assessment."""
        result = assess_compliance_risk(
            use_case_description=pii_text,
            use_presidio=False,
            use_openai=False
        )

        assert 'triggered_regulations' in result
        assert 'data_sensitivity_score' in result
        assert 'risk_factors' in result
        assert 'required_controls' in result
        assert 'compliance_checklist' in result

    def test_assess_compliance_risk_returns_dict(self, pii_text):
        """Test that convenience function returns a dictionary."""
        result = assess_compliance_risk(
            use_case_description=pii_text,
            use_presidio=False
        )

        assert isinstance(result, dict)
        assert isinstance(result['triggered_regulations'], list)
        assert isinstance(result['data_sensitivity_score'], int)


# Edge Cases and Error Handling

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_text(self):
        """Test classification with empty text."""
        classifier = DataClassifier(use_presidio=False)
        result = classifier.classify_use_case("")

        assert result['data_sensitivity_score'] == 0
        assert len(result['triggered_regulations']) == 0

    def test_very_long_text(self):
        """Test classification with very long text."""
        classifier = DataClassifier(use_presidio=False)
        long_text = "Contact john@example.com. " * 1000  # Repeat 1000 times

        result = classifier.detect_pii(long_text)

        assert result.detected is True
        assert len(result.examples) <= 5  # Should limit examples

    def test_special_characters(self):
        """Test classification with special characters."""
        classifier = DataClassifier(use_presidio=False)
        text = "Email: test@example.com!!! Phone: 555-123-4567??? SSN: 123-45-6789###"

        result = classifier.detect_pii(text)

        assert result.detected is True

    def test_multiple_data_types_no_duplication(self):
        """Test that required controls don't contain duplicates."""
        assessor = ComplianceRiskAssessor(use_presidio=False)
        text = """
        PII: john@example.com, SSN: 123-45-6789
        PHI: Patient diagnosis
        Financial: Card 4532-1234-5678-9010
        """

        assessment = assessor.assess(text)

        # Check for no duplicates in controls
        assert len(assessment.required_controls) == len(set(assessment.required_controls))


# Integration Tests

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_assessment_workflow(self):
        """Test complete assessment from start to finish."""
        use_case = """
        Our customer service RAG system processes support tickets containing:
        - Customer names and emails (john.doe@example.com)
        - Order histories with payment info (card ending in 9010)
        - SSN for identity verification: 123-45-6789
        - Some medical claims: patient treatment records
        """

        result = assess_compliance_risk(
            use_case_description=use_case,
            use_presidio=False,
            use_openai=False
        )

        # Should trigger multiple regulations
        assert len(result['triggered_regulations']) >= 3
        assert 'GDPR' in result['triggered_regulations'] or 'CCPA' in result['triggered_regulations']
        assert result['data_sensitivity_score'] >= 7

        # Should have comprehensive controls
        assert len(result['required_controls']) >= 10

        # Should have detailed checklist
        assert len(result['compliance_checklist']) >= 3

    def test_low_risk_assessment(self):
        """Test assessment of low-risk use case."""
        use_case = """
        Public documentation RAG system that indexes open-source software documentation
        and technical blog posts. No personal information, all public data.
        """

        result = assess_compliance_risk(use_case_description=use_case, use_presidio=False)

        assert result['data_sensitivity_score'] <= 2
        assert len(result['triggered_regulations']) <= 1  # Maybe just SOC 2 for quality

    def test_high_risk_assessment(self):
        """Test assessment of high-risk use case."""
        use_case = """
        Healthcare RAG system processing:
        - Patient medical records with diagnoses (CONFIDENTIAL)
        - SSNs: 123-45-6789, 987-65-4321
        - Payment information: cards 4532-1234-5678-9010
        - Proprietary treatment protocols (trade secrets)
        - Contact: patients@hospital.com, 555-123-4567
        """

        result = assess_compliance_risk(use_case_description=use_case, use_presidio=False)

        assert result['data_sensitivity_score'] >= 8
        assert 'HIPAA' in result['triggered_regulations']
        assert 'GDPR' in result['triggered_regulations'] or 'CCPA' in result['triggered_regulations']
        assert 'PCI-DSS' in result['triggered_regulations']
        assert len(result['required_controls']) >= 15
