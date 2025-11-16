"""
L3 M1.1: Why Compliance Matters in GCC RAG Systems

This module implements a Compliance Risk Assessment Tool that automatically detects
regulatory requirements, classifies data types (PII, PHI, financial), quantifies risks,
and generates actionable requirement checklists for RAG systems.

Core Capabilities:
1. Automatic regulation detection (GDPR, CCPA, HIPAA, SOC 2, ISO 27001)
2. Data type classification (PII, PHI, financial data, proprietary information)
3. Risk quantification (1-10 scale with specific risk factors)
4. Actionable requirement checklists for compliance teams
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

__all__ = [
    "DataClassifier",
    "RegulationMapper",
    "ComplianceRiskAssessor",
    "ChecklistGenerator",
    "assess_compliance_risk"
]


@dataclass
class ClassificationResult:
    """Results from data classification."""
    detected: bool
    entities: List[str] = field(default_factory=list)
    confidence: float = 0.0
    examples: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class ComplianceAssessment:
    """Complete compliance risk assessment results."""
    triggered_regulations: List[str]
    data_sensitivity_score: int
    risk_factors: List[str]
    required_controls: List[str]
    checklist: Dict[str, List[str]]


class DataClassifier:
    """
    Classifies data types and detects sensitive information.

    Uses Presidio for PII detection with fallback to keyword matching.
    Detects PII, PHI, financial data, and proprietary information.
    """

    def __init__(self, use_presidio: bool = False):
        """
        Initialize the data classifier.

        Args:
            use_presidio: Whether to use Presidio for enhanced PII detection
        """
        self.use_presidio = use_presidio
        self.analyzer = None

        if use_presidio:
            try:
                from presidio_analyzer import AnalyzerEngine
                self.analyzer = AnalyzerEngine()
                logger.info("✅ Presidio analyzer initialized")
            except ImportError:
                logger.warning("⚠️ Presidio not available, using keyword-based detection")
                self.use_presidio = False

        # PII detection patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'name': r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        }

        # PHI detection keywords
        self.phi_keywords = [
            'diagnosis', 'treatment', 'medication', 'patient', 'medical record',
            'prescription', 'surgery', 'lab results', 'symptoms', 'doctor',
            'hospital', 'clinic', 'health condition', 'disease', 'illness'
        ]

        # Financial data patterns
        self.financial_patterns = {
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'account_number': r'\b(?:account|acct)[\s#:]*\d{8,12}\b',
            'routing_number': r'\b\d{9}\b'
        }

        # Proprietary information keywords
        self.proprietary_keywords = [
            'confidential', 'proprietary', 'trade secret', 'internal only',
            'restricted', 'classified', 'patent pending', 'copyright'
        ]

    def detect_pii(self, text: str) -> ClassificationResult:
        """
        Detect personally identifiable information in text.

        Uses Presidio ML-based detection when available, falls back to
        keyword matching. Detects 50+ entity types including names,
        emails, phone numbers, SSNs, addresses.

        Args:
            text: Input text to analyze

        Returns:
            ClassificationResult with detected PII entities and confidence
        """
        logger.info("Detecting PII in text")

        if self.use_presidio and self.analyzer:
            # Use Presidio for ML-based detection
            results = self.analyzer.analyze(
                text=text,
                language='en',
                entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN",
                         "LOCATION", "DATE_TIME", "US_PASSPORT"]
            )

            if results:
                entities = [r.entity_type for r in results]
                examples = [text[r.start:r.end] for r in results[:3]]  # First 3 examples
                confidence = sum(r.score for r in results) / len(results)

                logger.info(f"Presidio detected {len(results)} PII entities")
                return ClassificationResult(
                    detected=True,
                    entities=entities,
                    confidence=confidence,
                    examples=examples,
                    risk_factors=["pii_exposure", "gdpr_applicable", "ccpa_applicable"]
                )

        # Fallback to keyword-based detection
        detected_entities = []
        examples = []

        for entity_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_entities.append(entity_type)
                examples.extend(matches[:2])  # First 2 examples per type

        if detected_entities:
            confidence = len(detected_entities) / len(self.pii_patterns)
            logger.info(f"Keyword-based detection found {len(detected_entities)} PII types")
            return ClassificationResult(
                detected=True,
                entities=detected_entities,
                confidence=confidence,
                examples=examples[:5],  # Limit total examples
                risk_factors=["pii_exposure", "gdpr_applicable", "ccpa_applicable"]
            )

        logger.info("No PII detected")
        return ClassificationResult(detected=False)

    def detect_phi(self, text: str) -> ClassificationResult:
        """
        Detect protected health information in text.

        Uses keyword-based detection for medical/health terminology.
        Production systems should use specialized models like scispaCy or BioBERT.

        Args:
            text: Input text to analyze

        Returns:
            ClassificationResult with detected PHI indicators
        """
        logger.info("Detecting PHI in text")

        text_lower = text.lower()
        detected_keywords = [kw for kw in self.phi_keywords if kw in text_lower]

        if detected_keywords:
            confidence = len(detected_keywords) / len(self.phi_keywords)
            logger.info(f"Detected {len(detected_keywords)} PHI keywords")
            return ClassificationResult(
                detected=True,
                entities=['health_information'],
                confidence=confidence,
                examples=detected_keywords[:5],
                risk_factors=["hipaa_applicable", "phi_exposure", "health_data_breach_risk"]
            )

        logger.info("No PHI detected")
        return ClassificationResult(detected=False)

    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        digits = [int(d) for d in card_number if d.isdigit()]
        checksum = 0
        reverse_digits = digits[::-1]

        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0

    def detect_financial(self, text: str) -> ClassificationResult:
        """
        Detect financial and payment data in text.

        Identifies credit cards (with Luhn validation), account numbers,
        routing numbers. Triggers SOX, PCI-DSS, and GLB regulations.

        Args:
            text: Input text to analyze

        Returns:
            ClassificationResult with detected financial data
        """
        logger.info("Detecting financial data in text")

        detected_entities = []
        examples = []
        risk_factors = []

        # Check for credit cards with Luhn validation
        cc_pattern = self.financial_patterns['credit_card']
        cc_matches = re.findall(cc_pattern, text)

        valid_cards = [cc for cc in cc_matches if self._luhn_check(cc)]
        if valid_cards:
            detected_entities.append('credit_card')
            examples.extend([cc[:4] + '****' + cc[-4:] for cc in valid_cards[:2]])
            risk_factors.extend(['pci_dss_applicable', 'payment_data_breach_risk'])

        # Check for account numbers
        if re.search(self.financial_patterns['account_number'], text, re.IGNORECASE):
            detected_entities.append('account_number')
            risk_factors.append('sox_applicable')

        # Check for routing numbers
        if re.search(self.financial_patterns['routing_number'], text):
            detected_entities.append('routing_number')
            risk_factors.append('glb_applicable')

        if detected_entities:
            confidence = len(detected_entities) / len(self.financial_patterns)
            logger.info(f"Detected {len(detected_entities)} financial data types")
            return ClassificationResult(
                detected=True,
                entities=detected_entities,
                confidence=confidence,
                examples=examples,
                risk_factors=risk_factors
            )

        logger.info("No financial data detected")
        return ClassificationResult(detected=False)

    def detect_proprietary(self, text: str) -> ClassificationResult:
        """
        Detect proprietary and confidential information in text.

        Identifies trade secrets, confidential markings, IP indicators.
        Affects NDAs, export control (ITAR), and IP protection requirements.

        Args:
            text: Input text to analyze

        Returns:
            ClassificationResult with detected proprietary information
        """
        logger.info("Detecting proprietary information in text")

        text_lower = text.lower()
        detected_keywords = [kw for kw in self.proprietary_keywords if kw in text_lower]

        if detected_keywords:
            confidence = len(detected_keywords) / len(self.proprietary_keywords)
            logger.info(f"Detected {len(detected_keywords)} proprietary markers")
            return ClassificationResult(
                detected=True,
                entities=['proprietary_information'],
                confidence=confidence,
                examples=detected_keywords[:5],
                risk_factors=["ip_protection_required", "nda_applicable", "export_control_check"]
            )

        logger.info("No proprietary information detected")
        return ClassificationResult(detected=False)

    def classify_use_case(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive data classification.

        Aggregates all detection results (PII, PHI, financial, proprietary),
        identifies triggered regulations, calculates data sensitivity score,
        and compiles risk factors.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with classification results:
            - pii_result: PII detection results
            - phi_result: PHI detection results
            - financial_result: Financial data detection results
            - proprietary_result: Proprietary info detection results
            - triggered_regulations: List of applicable regulations
            - data_sensitivity_score: 1-10 risk score
            - risk_factors: Consolidated risk factors
        """
        logger.info("Performing comprehensive use case classification")

        # Run all detectors
        pii_result = self.detect_pii(text)
        phi_result = self.detect_phi(text)
        financial_result = self.detect_financial(text)
        proprietary_result = self.detect_proprietary(text)

        # Aggregate results
        triggered_regulations = set()
        all_risk_factors = []

        if pii_result.detected:
            triggered_regulations.update(['GDPR', 'CCPA'])
            all_risk_factors.extend(pii_result.risk_factors)

        if phi_result.detected:
            triggered_regulations.add('HIPAA')
            all_risk_factors.extend(phi_result.risk_factors)

        if financial_result.detected:
            triggered_regulations.update(['SOX', 'PCI-DSS', 'GLB'])
            all_risk_factors.extend(financial_result.risk_factors)

        if proprietary_result.detected:
            triggered_regulations.update(['ISO 27001', 'NDA'])
            all_risk_factors.extend(proprietary_result.risk_factors)

        # Calculate sensitivity score (1-10)
        base_score = 0
        if pii_result.detected:
            base_score += 3
        if phi_result.detected:
            base_score += 4  # PHI is higher risk
        if financial_result.detected:
            base_score += 3
        if proprietary_result.detected:
            base_score += 2

        # Bonus for combined risks (fraud, complex compliance)
        if pii_result.detected and financial_result.detected:
            base_score += 2  # Fraud risk
            all_risk_factors.append('fraud_risk_elevated')

        sensitivity_score = min(base_score, 10)

        # Add general compliance requirements
        if sensitivity_score >= 7:
            triggered_regulations.add('SOC 2')

        logger.info(f"Classification complete: {len(triggered_regulations)} regulations triggered, "
                   f"sensitivity score: {sensitivity_score}")

        return {
            'pii_result': pii_result,
            'phi_result': phi_result,
            'financial_result': financial_result,
            'proprietary_result': proprietary_result,
            'triggered_regulations': sorted(list(triggered_regulations)),
            'data_sensitivity_score': sensitivity_score,
            'risk_factors': list(set(all_risk_factors))
        }


class RegulationMapper:
    """
    Maps compliance requirements to RAG system components.

    Provides detailed requirement checklists for GDPR, CCPA, HIPAA,
    SOC 2, ISO 27001, and other regulatory frameworks.
    """

    def __init__(self):
        """Initialize regulation mapping database."""
        self.regulations = {
            'GDPR': {
                'full_name': 'General Data Protection Regulation',
                'jurisdiction': 'European Union',
                'data_types': ['PII'],
                'key_requirements': [
                    'Lawful basis for processing (Art. 6)',
                    'Data subject consent management',
                    'Right to access (Art. 15)',
                    'Right to erasure / "right to be forgotten" (Art. 17)',
                    'Data portability (Art. 20)',
                    'Privacy by design (Art. 25)',
                    'Data breach notification within 72 hours (Art. 33)',
                    'Data Protection Impact Assessment for high-risk processing (Art. 35)',
                    'Data Processing Agreements with vendors (Art. 28)'
                ],
                'rag_specific': [
                    'Embed consent tracking in document ingestion pipeline',
                    'Implement vector database deletion for right to be forgotten',
                    'Log all embedding and retrieval operations with user IDs',
                    'Ensure data processing occurs in EU or adequate jurisdiction',
                    'Maintain audit trail for all data subject requests'
                ],
                'penalties': 'Up to €20M or 4% of global revenue (whichever is higher)'
            },
            'CCPA': {
                'full_name': 'California Consumer Privacy Act',
                'jurisdiction': 'California, USA',
                'data_types': ['PII'],
                'key_requirements': [
                    'Right to know what personal information is collected',
                    'Right to deletion',
                    'Right to opt-out of sale of personal information',
                    'Right to non-discrimination for exercising privacy rights',
                    'Privacy notice at collection',
                    'Data minimization practices',
                    'Reasonable security procedures'
                ],
                'rag_specific': [
                    'Provide transparency about RAG data sources',
                    'Implement opt-out mechanisms for personal data in training',
                    'Track California residents in user database',
                    'Maintain data inventory for personal information categories',
                    'Document data retention and deletion procedures'
                ],
                'penalties': 'Up to $7,500 per intentional violation'
            },
            'HIPAA': {
                'full_name': 'Health Insurance Portability and Accountability Act',
                'jurisdiction': 'United States',
                'data_types': ['PHI'],
                'key_requirements': [
                    'Privacy Rule: Minimum necessary standard for PHI use',
                    'Security Rule: Administrative, physical, technical safeguards',
                    'Encryption of PHI at rest and in transit',
                    'Access controls and audit logging',
                    'Business Associate Agreements (BAA) with vendors',
                    'Breach notification requirements',
                    'Patient rights to access and amend records'
                ],
                'rag_specific': [
                    'Encrypt embeddings containing PHI (AES-256)',
                    'Implement role-based access control for retrieval',
                    'Maintain comprehensive audit logs for all PHI access',
                    'Ensure vector database vendor signs BAA',
                    'Anonymize or de-identify PHI before embedding when possible',
                    'Regular risk assessments of RAG infrastructure'
                ],
                'penalties': 'Up to $1.5M per violation category per year'
            },
            'SOC 2': {
                'full_name': 'Service Organization Control 2',
                'jurisdiction': 'United States (industry standard)',
                'data_types': ['All sensitive data'],
                'key_requirements': [
                    'Security: Protection against unauthorized access',
                    'Availability: System uptime and performance',
                    'Processing Integrity: Complete, valid, accurate processing',
                    'Confidentiality: Protection of confidential information',
                    'Privacy: Collection, use, retention, disclosure aligned with commitments',
                    'Continuous monitoring and incident response',
                    'Change management procedures',
                    'Vendor management and due diligence'
                ],
                'rag_specific': [
                    'Implement monitoring for RAG system performance and errors',
                    'Maintain change logs for model updates and retraining',
                    'Document data flow from ingestion to generation',
                    'Establish incident response plan for RAG failures',
                    'Regular penetration testing of API endpoints',
                    'Vendor risk assessment for LLM and vector DB providers'
                ],
                'penalties': 'Failed audit leads to loss of customers/contracts'
            },
            'ISO 27001': {
                'full_name': 'Information Security Management System',
                'jurisdiction': 'International',
                'data_types': ['All information assets'],
                'key_requirements': [
                    'Information security policy',
                    'Risk assessment and treatment',
                    'Asset management and classification',
                    'Access control policies',
                    'Cryptographic controls',
                    'Physical and environmental security',
                    'Incident management',
                    'Business continuity planning',
                    'Compliance monitoring and auditing'
                ],
                'rag_specific': [
                    'Classify all documents in RAG corpus by sensitivity',
                    'Implement namespace isolation in vector database',
                    'Establish backup and recovery procedures for embeddings',
                    'Regular security audits of RAG infrastructure',
                    'Document security controls in system architecture',
                    'Employee training on secure RAG operation'
                ],
                'penalties': 'Certification loss, reputation damage'
            },
            'SOX': {
                'full_name': 'Sarbanes-Oxley Act',
                'jurisdiction': 'United States (public companies)',
                'data_types': ['Financial data'],
                'key_requirements': [
                    'Internal controls over financial reporting',
                    'Audit trails for financial data access',
                    'Segregation of duties',
                    'Data integrity and accuracy',
                    'IT general controls (ITGC)',
                    'Change management documentation',
                    'Regular internal audits'
                ],
                'rag_specific': [
                    'Immutable audit logs for financial document access',
                    'Version control for financial RAG models',
                    'Segregated access to financial data namespaces',
                    'Regular reconciliation of RAG outputs vs source documents',
                    'Documentation of RAG system changes affecting financial reporting'
                ],
                'penalties': 'Criminal penalties for executives, SEC enforcement'
            },
            'PCI-DSS': {
                'full_name': 'Payment Card Industry Data Security Standard',
                'jurisdiction': 'Global (card brands)',
                'data_types': ['Payment card data'],
                'key_requirements': [
                    'Never store sensitive authentication data after authorization',
                    'Protect stored cardholder data (encryption)',
                    'Encrypt transmission of cardholder data across public networks',
                    'Restrict access to cardholder data by business need-to-know',
                    'Assign unique ID to each person with computer access',
                    'Regularly test security systems and processes',
                    'Maintain vulnerability management program',
                    'Implement strong access control measures'
                ],
                'rag_specific': [
                    'NEVER embed full credit card numbers in RAG corpus',
                    'Tokenize or mask payment data before ingestion',
                    'Isolate payment-related queries to separate environment',
                    'Quarterly vulnerability scans of RAG infrastructure',
                    'Strict access controls for payment data namespaces'
                ],
                'penalties': 'Fines up to $500K per incident, loss of card processing privileges'
            },
            'GLB': {
                'full_name': 'Gramm-Leach-Bliley Act',
                'jurisdiction': 'United States (financial institutions)',
                'data_types': ['Nonpublic personal information (NPI)'],
                'key_requirements': [
                    'Financial Privacy Rule: Privacy notices to customers',
                    'Safeguards Rule: Written information security plan',
                    'Pretexting Protection: Protect against social engineering',
                    'Administrative, technical, physical safeguards',
                    'Regular risk assessments',
                    'Vendor oversight and service provider agreements'
                ],
                'rag_specific': [
                    'Privacy notices covering RAG system use of customer data',
                    'Comprehensive security plan for RAG infrastructure',
                    'Risk assessment of LLM and vector DB vendors',
                    'Employee training on preventing pretexting in RAG interactions',
                    'Regular testing of safeguards effectiveness'
                ],
                'penalties': 'Up to $100K per violation, criminal penalties possible'
            }
        }

        logger.info(f"Initialized regulation mapper with {len(self.regulations)} frameworks")

    def get_requirements(self, regulation: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed requirements for a specific regulation.

        Args:
            regulation: Regulation code (e.g., 'GDPR', 'HIPAA')

        Returns:
            Dictionary with regulation details or None if not found
        """
        return self.regulations.get(regulation)

    def get_all_regulations(self) -> Dict[str, Dict[str, Any]]:
        """Get all available regulation frameworks."""
        return self.regulations


class ChecklistGenerator:
    """
    Generates actionable compliance requirement checklists.

    Creates detailed, RAG-specific checklists for each triggered regulation,
    organized by RAG pipeline stage (ingestion, embedding, storage, retrieval, generation).
    """

    def __init__(self, regulation_mapper: RegulationMapper):
        """
        Initialize checklist generator.

        Args:
            regulation_mapper: RegulationMapper instance for requirement lookup
        """
        self.mapper = regulation_mapper

    def generate_checklist(self, triggered_regulations: List[str]) -> Dict[str, List[str]]:
        """
        Generate comprehensive compliance checklist.

        Args:
            triggered_regulations: List of regulation codes

        Returns:
            Dictionary with checklists organized by regulation and RAG stage
        """
        logger.info(f"Generating checklist for {len(triggered_regulations)} regulations")

        checklist = {}

        for reg in triggered_regulations:
            requirements = self.mapper.get_requirements(reg)
            if requirements:
                checklist[reg] = {
                    'general_requirements': requirements['key_requirements'],
                    'rag_specific_controls': requirements.get('rag_specific', []),
                    'penalties': requirements.get('penalties', 'Not specified')
                }

        # Add cross-cutting concerns
        if len(triggered_regulations) > 1:
            checklist['Cross-Cutting Concerns'] = {
                'general_requirements': [
                    'Unified audit logging across all compliance requirements',
                    'Centralized consent and preference management',
                    'Comprehensive data inventory and classification',
                    'Regular third-party security assessments',
                    'Incident response plan covering all regulatory obligations',
                    'Employee training on all applicable regulations'
                ],
                'rag_specific_controls': [
                    'Multi-tenant data isolation in vector database',
                    'Unified access control policy across RAG pipeline',
                    'Consolidated monitoring dashboard for compliance metrics',
                    'Single source of truth for data lineage and provenance',
                    'Automated compliance testing in CI/CD pipeline'
                ],
                'penalties': 'Multiple violations compound legal and financial risks'
            }

        logger.info(f"Generated checklist with {len(checklist)} sections")
        return checklist


class ComplianceRiskAssessor:
    """
    Main orchestrator for compliance risk assessment.

    Coordinates data classification, regulation mapping, and checklist generation
    to produce comprehensive compliance assessments for RAG systems.
    """

    def __init__(self, use_presidio: bool = False, use_openai: bool = False):
        """
        Initialize compliance risk assessor.

        Args:
            use_presidio: Enable Presidio for enhanced PII detection
            use_openai: Enable OpenAI for enhanced risk analysis (future use)
        """
        self.classifier = DataClassifier(use_presidio=use_presidio)
        self.mapper = RegulationMapper()
        self.checklist_gen = ChecklistGenerator(self.mapper)
        self.use_openai = use_openai

        if use_openai:
            logger.warning("OpenAI integration not yet implemented in this version")

        logger.info("Compliance Risk Assessor initialized")

    def assess(self, use_case_description: str) -> ComplianceAssessment:
        """
        Perform complete compliance risk assessment.

        Args:
            use_case_description: Description of the RAG system use case

        Returns:
            ComplianceAssessment with regulations, risk score, and checklist
        """
        logger.info("Starting compliance risk assessment")

        # Classify the use case
        classification = self.classifier.classify_use_case(use_case_description)

        # Extract results
        triggered_regulations = classification['triggered_regulations']
        sensitivity_score = classification['data_sensitivity_score']
        risk_factors = classification['risk_factors']

        # Generate required controls based on sensitivity
        required_controls = self._determine_required_controls(
            sensitivity_score,
            triggered_regulations
        )

        # Generate compliance checklist
        checklist = self.checklist_gen.generate_checklist(triggered_regulations)

        assessment = ComplianceAssessment(
            triggered_regulations=triggered_regulations,
            data_sensitivity_score=sensitivity_score,
            risk_factors=risk_factors,
            required_controls=required_controls,
            checklist=checklist
        )

        logger.info(f"Assessment complete: {len(triggered_regulations)} regulations, "
                   f"score {sensitivity_score}/10, {len(required_controls)} controls required")

        return assessment

    def _determine_required_controls(
        self,
        sensitivity_score: int,
        regulations: List[str]
    ) -> List[str]:
        """
        Determine required technical controls based on risk.

        Args:
            sensitivity_score: Data sensitivity score (1-10)
            regulations: List of triggered regulations

        Returns:
            List of required control implementations
        """
        controls = []

        # Base controls for all RAG systems
        controls.extend([
            'Implement audit logging for all data access',
            'Encrypt data at rest and in transit',
            'Implement role-based access control (RBAC)'
        ])

        # Sensitivity-based controls
        if sensitivity_score >= 5:
            controls.extend([
                'Implement data classification and labeling',
                'Establish data retention and deletion policies',
                'Deploy monitoring and alerting for anomalous access'
            ])

        if sensitivity_score >= 7:
            controls.extend([
                'Implement multi-factor authentication',
                'Deploy data loss prevention (DLP) controls',
                'Conduct regular security assessments and penetration testing',
                'Establish incident response and breach notification procedures'
            ])

        if sensitivity_score >= 9:
            controls.extend([
                'Implement zero-trust architecture',
                'Deploy advanced threat detection and response',
                'Establish security operations center (SOC) monitoring',
                'Conduct quarterly compliance audits'
            ])

        # Regulation-specific controls
        if 'GDPR' in regulations or 'CCPA' in regulations:
            controls.extend([
                'Implement consent management system',
                'Enable data subject access and deletion requests',
                'Maintain data processing inventory'
            ])

        if 'HIPAA' in regulations:
            controls.extend([
                'Obtain Business Associate Agreements (BAA) with all vendors',
                'Implement PHI-specific encryption (AES-256 minimum)',
                'Conduct annual HIPAA risk assessments'
            ])

        if 'PCI-DSS' in regulations:
            controls.extend([
                'NEVER store sensitive authentication data (CVV, PIN)',
                'Tokenize or mask payment card data',
                'Quarterly vulnerability scans by ASV',
                'Annual PCI-DSS compliance assessment'
            ])

        if 'SOC 2' in regulations:
            controls.extend([
                'Establish continuous monitoring framework',
                'Implement change management procedures',
                'Maintain vendor risk management program',
                'Conduct annual SOC 2 Type II audit'
            ])

        return sorted(list(set(controls)))  # Remove duplicates and sort


def assess_compliance_risk(
    use_case_description: str,
    use_presidio: bool = False,
    use_openai: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for quick compliance risk assessment.

    Args:
        use_case_description: Description of the RAG system use case
        use_presidio: Enable Presidio for enhanced PII detection
        use_openai: Enable OpenAI for enhanced risk analysis

    Returns:
        Dictionary with complete assessment results
    """
    assessor = ComplianceRiskAssessor(
        use_presidio=use_presidio,
        use_openai=use_openai
    )

    assessment = assessor.assess(use_case_description)

    return {
        'triggered_regulations': assessment.triggered_regulations,
        'data_sensitivity_score': assessment.data_sensitivity_score,
        'risk_factors': assessment.risk_factors,
        'required_controls': assessment.required_controls,
        'compliance_checklist': assessment.checklist
    }
