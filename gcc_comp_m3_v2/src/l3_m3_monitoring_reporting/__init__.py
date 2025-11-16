"""
L3 M3.2: Automated Compliance Testing

This module implements automated compliance testing using Open Policy Agent (OPA)
and optional Presidio for PII detection in RAG systems. It provides policy-as-code
functionality for GDPR, DPDPA, SOX, and SOC 2 compliance validation.

The module supports:
- PII detection (SSN, email, credit card, phone patterns)
- Policy evaluation with OPA/Rego
- Redaction quality validation
- Compliance test automation
- CI/CD integration for regression prevention
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "PIIDetector",
    "OPAPolicyEngine",
    "PresidioPIIDetector",
    "ComplianceValidator",
    "contains_pii",
    "redaction_quality_sufficient",
    "check_compliance",
    "evaluate_policy",
    "run_compliance_tests"
]


class PIIType(Enum):
    """Types of PII patterns detected."""
    SSN = "ssn"
    EMAIL = "email"
    CREDIT_CARD = "credit_card"
    PHONE = "phone"
    NONE = "none"


@dataclass
class PIIDetectionResult:
    """Result of PII detection."""
    has_pii: bool
    pii_types: List[PIIType]
    violations: List[str]
    redacted: bool


@dataclass
class ComplianceResult:
    """Result of compliance validation."""
    allowed: bool
    violations: List[str]
    policy_decisions: Dict[str, Any]
    test_coverage: Optional[Dict[str, float]] = None


class PIIDetector:
    """
    Regex-based PII detector using patterns from OPA Rego policies.

    Detects:
    - SSN: xxx-xx-xxxx format
    - Email: standard email patterns
    - Credit Card: 16-digit patterns with optional dashes/spaces
    - Phone: US phone number formats
    """

    # Regex patterns matching Rego policy definitions
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    CREDIT_CARD_PATTERN = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    PHONE_PATTERN = r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
    REDACTED_MARKER = r'\[REDACTED\]'

    def __init__(self):
        """Initialize PII detector with compiled regex patterns."""
        self.patterns = {
            PIIType.SSN: re.compile(self.SSN_PATTERN),
            PIIType.EMAIL: re.compile(self.EMAIL_PATTERN),
            PIIType.CREDIT_CARD: re.compile(self.CREDIT_CARD_PATTERN),
            PIIType.PHONE: re.compile(self.PHONE_PATTERN)
        }
        logger.info("Initialized PIIDetector with 4 pattern types")

    def detect(self, text: str) -> PIIDetectionResult:
        """
        Detect PII in text using regex patterns.

        Args:
            text: Input text to scan for PII

        Returns:
            PIIDetectionResult with detected PII types and violations
        """
        if not text:
            return PIIDetectionResult(
                has_pii=False,
                pii_types=[],
                violations=[],
                redacted=False
            )

        detected_types = []
        violations = []

        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_types.append(pii_type)
                violations.append(
                    f"Found {pii_type.value}: {len(matches)} instance(s) - "
                    f"GDPR Article 17, DPDPA Section 12 violation"
                )
                logger.warning(f"Detected {pii_type.value} in text (count: {len(matches)})")

        # Check if text has redaction markers
        redacted = bool(re.search(self.REDACTED_MARKER, text))

        return PIIDetectionResult(
            has_pii=len(detected_types) > 0,
            pii_types=detected_types,
            violations=violations,
            redacted=redacted
        )

    def check_redaction_quality(self, text: str) -> Tuple[bool, List[str]]:
        """
        Verify redaction quality per policy requirements.

        Args:
            text: Text to check for proper redaction

        Returns:
            Tuple of (is_sufficient, violation_messages)
        """
        detection = self.detect(text)

        if not detection.has_pii:
            return True, []

        if not detection.redacted:
            return False, [
                "PII found without [REDACTED] markers - redaction required"
            ]

        # Check if redaction markers are present for all PII instances
        violations = []
        for pii_type in detection.pii_types:
            pattern = self.patterns[pii_type]
            if pattern.search(text):
                violations.append(
                    f"Unredacted {pii_type.value} found alongside [REDACTED] markers - "
                    f"incomplete redaction"
                )

        return len(violations) == 0, violations


class PresidioPIIDetector:
    """
    Optional Presidio-based PII detector for enhanced detection.

    Requires: presidio-analyzer, presidio-anonymizer packages
    Falls back to regex-based detection if Presidio unavailable.
    """

    def __init__(self, fallback_to_regex: bool = True):
        """
        Initialize Presidio detector.

        Args:
            fallback_to_regex: Use regex detector if Presidio unavailable
        """
        self.presidio_available = False
        self.analyzer = None
        self.fallback = PIIDetector() if fallback_to_regex else None

        try:
            from presidio_analyzer import AnalyzerEngine
            self.analyzer = AnalyzerEngine()
            self.presidio_available = True
            logger.info("✓ Presidio analyzer initialized")
        except ImportError:
            logger.warning(
                "⚠️ Presidio not available - install with: "
                "pip install presidio-analyzer presidio-anonymizer"
            )
            if not fallback_to_regex:
                raise

    def detect(self, text: str) -> PIIDetectionResult:
        """
        Detect PII using Presidio or fallback to regex.

        Args:
            text: Input text to scan

        Returns:
            PIIDetectionResult
        """
        if not self.presidio_available:
            if self.fallback:
                logger.info("Using regex fallback for PII detection")
                return self.fallback.detect(text)
            else:
                raise RuntimeError("Presidio not available and fallback disabled")

        # Use Presidio analyzer
        results = self.analyzer.analyze(text=text, language='en')

        detected_types = []
        violations = []

        # Map Presidio entity types to our PIIType enum
        type_mapping = {
            'US_SSN': PIIType.SSN,
            'EMAIL_ADDRESS': PIIType.EMAIL,
            'CREDIT_CARD': PIIType.CREDIT_CARD,
            'PHONE_NUMBER': PIIType.PHONE
        }

        for result in results:
            pii_type = type_mapping.get(result.entity_type)
            if pii_type and pii_type not in detected_types:
                detected_types.append(pii_type)
                violations.append(
                    f"Found {pii_type.value} (Presidio score: {result.score:.2f}) - "
                    f"compliance violation"
                )

        redacted = '[REDACTED]' in text

        return PIIDetectionResult(
            has_pii=len(detected_types) > 0,
            pii_types=detected_types,
            violations=violations,
            redacted=redacted
        )


class OPAPolicyEngine:
    """
    Wrapper for Open Policy Agent (OPA) policy evaluation.

    Simulates OPA policy decisions based on Rego policy logic.
    In production, this would call actual OPA binary via subprocess.
    """

    def __init__(self, policy_path: Optional[str] = None):
        """
        Initialize OPA policy engine.

        Args:
            policy_path: Path to .rego policy files (optional)
        """
        self.policy_path = policy_path
        self.pii_detector = PIIDetector()
        logger.info(f"Initialized OPAPolicyEngine (policy_path: {policy_path})")

    def evaluate_pii_policy(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate PII detection policy (simulates Rego policy).

        Policy logic from script:
        - Default deny: allow_embedding = false
        - Deny if contains_pii(text) and not redacted
        - Allow if redaction_quality_sufficient(text)

        Args:
            input_data: Input with 'operation', 'text', 'pii_redacted' fields

        Returns:
            Policy decision with allow/deny and violations
        """
        operation = input_data.get('operation', 'unknown')
        text = input_data.get('text', '')
        pii_redacted = input_data.get('pii_redacted', False)

        logger.info(f"Evaluating PII policy for operation: {operation}")

        # Run PII detection
        detection = self.pii_detector.detect(text)

        # Default deny principle
        allow = False
        violations = []

        if not detection.has_pii:
            # No PII found - allow
            allow = True
            logger.info("✓ No PII detected - operation allowed")
        elif pii_redacted or detection.redacted:
            # Check redaction quality
            quality_ok, quality_violations = self.pii_detector.check_redaction_quality(text)
            if quality_ok:
                allow = True
                logger.info("✓ PII properly redacted - operation allowed")
            else:
                violations.extend(quality_violations)
                logger.warning(f"✗ Insufficient redaction quality: {quality_violations}")
        else:
            # PII found without redaction - deny
            violations.extend(detection.violations)
            logger.warning(f"✗ Unredacted PII found - operation denied")

        return {
            'allow': allow,
            'violations': violations,
            'pii_detected': detection.has_pii,
            'pii_types': [t.value for t in detection.pii_types],
            'policy': 'ragcompliance.pii'
        }

    def evaluate(self, input_data: Dict[str, Any], policy: str = 'pii') -> Dict[str, Any]:
        """
        Evaluate policy against input data.

        Args:
            input_data: Input data for policy evaluation
            policy: Policy name to evaluate ('pii', 'access', 'audit', 'retention')

        Returns:
            Policy decision
        """
        if policy == 'pii':
            return self.evaluate_pii_policy(input_data)
        else:
            # Placeholder for other policies (access control, audit, retention)
            logger.warning(f"Policy '{policy}' not implemented - defaulting to deny")
            return {
                'allow': False,
                'violations': [f"Policy '{policy}' not implemented"],
                'policy': f'ragcompliance.{policy}'
            }


class ComplianceValidator:
    """
    High-level compliance validator integrating all checks.

    Coordinates:
    - PII detection (Presidio or regex)
    - OPA policy evaluation
    - Test coverage tracking
    """

    def __init__(self, use_presidio: bool = False, opa_policy_path: Optional[str] = None):
        """
        Initialize compliance validator.

        Args:
            use_presidio: Use Presidio for PII detection (requires installation)
            opa_policy_path: Path to OPA policy files
        """
        self.pii_detector = (
            PresidioPIIDetector() if use_presidio else PIIDetector()
        )
        self.opa_engine = OPAPolicyEngine(policy_path=opa_policy_path)
        self.test_results = []
        logger.info(
            f"Initialized ComplianceValidator "
            f"(presidio={use_presidio}, opa_path={opa_policy_path})"
        )

    def validate(
        self,
        operation: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Validate operation for compliance.

        Args:
            operation: Operation type ('embed', 'query', 'store', etc.)
            text: Text content to validate
            metadata: Optional metadata for validation

        Returns:
            ComplianceResult with allow/deny decision
        """
        logger.info(f"Validating {operation} operation (text length: {len(text)})")

        input_data = {
            'operation': operation,
            'text': text,
            'pii_redacted': metadata.get('pii_redacted', False) if metadata else False
        }

        # Evaluate policy
        decision = self.opa_engine.evaluate(input_data, policy='pii')

        # Track test result
        self.test_results.append({
            'operation': operation,
            'allowed': decision['allow'],
            'violations': len(decision['violations'])
        })

        return ComplianceResult(
            allowed=decision['allow'],
            violations=decision['violations'],
            policy_decisions={'pii': decision}
        )

    def get_test_coverage(self) -> Dict[str, float]:
        """
        Calculate test coverage metrics.

        Returns:
            Coverage statistics based on test results
        """
        if not self.test_results:
            return {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'coverage_pct': 0.0
            }

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['allowed'] or r['violations'] == 0)

        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'coverage_pct': (passed / total * 100) if total > 0 else 0.0
        }


# Public API functions

def contains_pii(text: str) -> bool:
    """
    Check if text contains PII using regex patterns.

    Args:
        text: Text to check

    Returns:
        True if PII detected, False otherwise
    """
    detector = PIIDetector()
    result = detector.detect(text)
    return result.has_pii


def redaction_quality_sufficient(text: str) -> bool:
    """
    Verify redaction quality meets policy requirements.

    Args:
        text: Text to check

    Returns:
        True if redaction quality is sufficient, False otherwise
    """
    detector = PIIDetector()
    is_sufficient, _ = detector.check_redaction_quality(text)
    return is_sufficient


def check_compliance(
    operation: str,
    text: str,
    use_presidio: bool = False
) -> ComplianceResult:
    """
    Check compliance for an operation.

    Args:
        operation: Operation type ('embed', 'query', etc.)
        text: Text content to validate
        use_presidio: Use Presidio for enhanced detection

    Returns:
        ComplianceResult
    """
    validator = ComplianceValidator(use_presidio=use_presidio)
    return validator.validate(operation, text)


def evaluate_policy(
    input_data: Dict[str, Any],
    policy: str = 'pii'
) -> Dict[str, Any]:
    """
    Evaluate OPA policy against input data.

    Args:
        input_data: Input for policy evaluation
        policy: Policy name to evaluate

    Returns:
        Policy decision
    """
    engine = OPAPolicyEngine()
    return engine.evaluate(input_data, policy=policy)


def run_compliance_tests() -> Dict[str, Any]:
    """
    Run comprehensive compliance test suite.

    Implements test pyramid from script:
    - 15-20 PII Detection tests
    - 15-20 Access Control tests (placeholder)
    - 10-15 Audit Logging tests (placeholder)
    - 10-12 Data Retention tests (placeholder)
    - 5-10 Regression tests

    Returns:
        Test results summary
    """
    logger.info("Running compliance test suite...")

    validator = ComplianceValidator()
    test_cases = [
        # PII Detection tests (15-20)
        {
            'name': 'test_pii_blocking_ssn',
            'operation': 'embed',
            'text': 'User SSN is 123-45-6789',
            'expected_allow': False
        },
        {
            'name': 'test_pii_blocking_email',
            'operation': 'embed',
            'text': 'Contact: john.doe@example.com',
            'expected_allow': False
        },
        {
            'name': 'test_pii_blocking_credit_card',
            'operation': 'embed',
            'text': 'Card: 4532-1234-5678-9010',
            'expected_allow': False
        },
        {
            'name': 'test_pii_blocking_phone',
            'operation': 'embed',
            'text': 'Call me at (555) 123-4567',
            'expected_allow': False
        },
        {
            'name': 'test_redacted_pii_allowed',
            'operation': 'embed',
            'text': 'User SSN is [REDACTED]',
            'expected_allow': True
        },
        {
            'name': 'test_no_pii_allowed',
            'operation': 'embed',
            'text': 'This is a clean document about policy compliance',
            'expected_allow': True
        },
        {
            'name': 'test_multiple_pii_types',
            'operation': 'query',
            'text': 'SSN: 123-45-6789, Email: test@example.com',
            'expected_allow': False
        },
        {
            'name': 'test_partial_redaction_denied',
            'operation': 'store',
            'text': 'SSN [REDACTED] but email test@example.com',
            'expected_allow': False
        },
        {
            'name': 'test_full_redaction_allowed',
            'operation': 'store',
            'text': 'SSN [REDACTED] and email [REDACTED]',
            'expected_allow': True
        },
        {
            'name': 'test_edge_case_empty_text',
            'operation': 'embed',
            'text': '',
            'expected_allow': True
        }
    ]

    results = []
    passed = 0
    failed = 0

    for test_case in test_cases:
        try:
            result = validator.validate(
                operation=test_case['operation'],
                text=test_case['text']
            )

            test_passed = result.allowed == test_case['expected_allow']
            if test_passed:
                passed += 1
            else:
                failed += 1

            results.append({
                'name': test_case['name'],
                'passed': test_passed,
                'expected': test_case['expected_allow'],
                'actual': result.allowed,
                'violations': result.violations
            })

            status = '✓' if test_passed else '✗'
            logger.info(f"{status} {test_case['name']}")

        except Exception as e:
            failed += 1
            results.append({
                'name': test_case['name'],
                'passed': False,
                'error': str(e)
            })
            logger.error(f"✗ {test_case['name']}: {e}")

    coverage = validator.get_test_coverage()

    summary = {
        'total_tests': len(test_cases),
        'passed': passed,
        'failed': failed,
        'pass_rate': (passed / len(test_cases) * 100) if test_cases else 0,
        'coverage': coverage,
        'results': results[:5]  # Show first 5 for brevity
    }

    logger.info(
        f"Test suite completed: {passed}/{len(test_cases)} passed "
        f"({summary['pass_rate']:.1f}%)"
    )

    return summary
