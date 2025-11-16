"""
L3 M4.2: Vendor Risk Assessment

This module implements a comprehensive vendor risk assessment framework for GCC compliance.
It provides weighted evaluation across 5 categories: Security, Privacy, Compliance,
Reliability, and Data Residency, with automated DPA validation and subprocessor tracking.

Based on the augmented script:
https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M4_2_VendorRiskAssessment.md
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "VendorRiskAssessment",
    "DPAValidator",
    "SubprocessorRegistry",
    "ContinuousMonitor",
    "RiskLevel",
    "calculate_roi",
    "multi_jurisdiction_compliance_check",
    "assess_vendor",
]


class RiskLevel(Enum):
    """Risk level classification based on assessment scores."""
    LOW = "Low Risk (Approved)"
    MEDIUM = "Medium Risk (Approved with Conditions)"
    HIGH = "High Risk (Additional Controls Required)"
    CRITICAL = "Critical Risk (Rejected)"


@dataclass
class VendorProfile:
    """Vendor profile data structure."""
    name: str
    soc2_date: Optional[datetime] = None
    iso27001_certified: bool = False
    penetration_testing: bool = False
    breach_count: int = 0
    gdpr_compliant: bool = False
    dpa_available: bool = False
    data_deletion_automated: bool = False
    sla_guarantee: float = 0.0
    actual_uptime: float = 0.0
    data_center_locations: List[str] = None
    subprocessors: List[str] = None

    def __post_init__(self):
        if self.data_center_locations is None:
            self.data_center_locations = []
        if self.subprocessors is None:
            self.subprocessors = []


class VendorRiskAssessment:
    """
    Main vendor risk assessment engine implementing weighted 5-category evaluation.

    Categories and weights:
    - Security: 30%
    - Privacy: 25%
    - Compliance: 20%
    - Reliability: 15%
    - Data Residency: 10%
    """

    WEIGHTS = {
        'security': 0.30,
        'privacy': 0.25,
        'compliance': 0.20,
        'reliability': 0.15,
        'data_residency': 0.10
    }

    def __init__(self, vendor_profile: VendorProfile):
        """
        Initialize assessment for a vendor.

        Args:
            vendor_profile: VendorProfile object with vendor details
        """
        self.vendor = vendor_profile
        self.scores = {}
        logger.info(f"Initialized risk assessment for vendor: {vendor_profile.name}")

    def evaluate_security(self) -> float:
        """
        Evaluate security posture (max 100 points).

        Criteria:
        - SOC 2 Type II recency: 0-30 points
        - ISO 27001 certification: 0-20 points
        - Annual penetration testing: 0-20 points
        - Breach history deductions: max -30 points

        Returns:
            Security score (0-100)
        """
        score = 0.0

        # SOC 2 Type II recency (0-30 points)
        if self.vendor.soc2_date:
            days_old = (datetime.now() - self.vendor.soc2_date).days
            if days_old <= 365:
                score += 30
            elif days_old <= 730:
                score += 20
            else:
                score += 10
                logger.warning(f"SOC 2 report older than 2 years for {self.vendor.name}")

        # ISO 27001 certification (0-20 points)
        if self.vendor.iso27001_certified:
            score += 20

        # Annual penetration testing (0-20 points)
        if self.vendor.penetration_testing:
            score += 20

        # Breach history deductions (max -30 points)
        breach_penalty = min(self.vendor.breach_count * 10, 30)
        score -= breach_penalty

        if breach_penalty > 0:
            logger.warning(f"Security score reduced by {breach_penalty} points due to {self.vendor.breach_count} breaches")

        # Ensure score is within bounds
        score = max(0, min(100, score))

        self.scores['security'] = score
        logger.info(f"Security score for {self.vendor.name}: {score}/100")
        return score

    def evaluate_privacy(self) -> float:
        """
        Evaluate privacy practices (max 100 points).

        Criteria:
        - GDPR compliance with DPA: 0-40 points
        - Data handling transparency: 0-30 points
        - Automated deletion process: 0-20 points
        - Access control strength: 0-10 points

        Returns:
            Privacy score (0-100)
        """
        score = 0.0

        # GDPR compliance with DPA (0-40 points)
        if self.vendor.gdpr_compliant and self.vendor.dpa_available:
            score += 40
        elif self.vendor.gdpr_compliant:
            score += 20

        # Data handling transparency (assumed 30 points if GDPR compliant)
        if self.vendor.gdpr_compliant:
            score += 30

        # Automated deletion process (0-20 points)
        if self.vendor.data_deletion_automated:
            score += 20
        else:
            logger.info(f"Manual deletion process detected for {self.vendor.name}")

        # Access control strength (assumed 10 points if DPA available)
        if self.vendor.dpa_available:
            score += 10

        self.scores['privacy'] = score
        logger.info(f"Privacy score for {self.vendor.name}: {score}/100")
        return score

    def evaluate_compliance(self) -> float:
        """
        Evaluate compliance standing (max 100 points).

        Criteria:
        - Industry certifications: 0-15 points
        - Audit report recency: 0-30 points
        - Proactive compliance notifications: 0-20 points
        - Regulatory violation history: ±10 points

        Returns:
            Compliance score (0-100)
        """
        score = 0.0

        # Industry certifications (simplified - using ISO 27001 as proxy)
        if self.vendor.iso27001_certified:
            score += 15

        # Audit report recency (using SOC 2 as proxy)
        if self.vendor.soc2_date:
            days_old = (datetime.now() - self.vendor.soc2_date).days
            if days_old <= 365:
                score += 30
            elif days_old <= 730:
                score += 15

        # Proactive compliance notifications (assumed 20 points if GDPR compliant)
        if self.vendor.gdpr_compliant:
            score += 20

        # Regulatory violation history (assumed clean if no breaches)
        if self.vendor.breach_count == 0:
            score += 10
        else:
            score -= 10

        # Base compliance score for having DPA
        if self.vendor.dpa_available:
            score += 25

        score = max(0, min(100, score))
        self.scores['compliance'] = score
        logger.info(f"Compliance score for {self.vendor.name}: {score}/100")
        return score

    def evaluate_reliability(self) -> float:
        """
        Evaluate reliability metrics (max 100 points).

        Criteria:
        - SLA guarantees: 0-40 points
        - Actual uptime vs commitment: 0-30 points
        - Support response times: 0-20 points
        - Disaster recovery testing: 0-10 points

        Returns:
            Reliability score (0-100)
        """
        score = 0.0

        # SLA guarantees (0-40 points)
        if self.vendor.sla_guarantee >= 99.9:
            score += 40
        elif self.vendor.sla_guarantee >= 99.5:
            score += 30
        elif self.vendor.sla_guarantee >= 99.0:
            score += 20
        else:
            logger.warning(f"Low SLA guarantee for {self.vendor.name}: {self.vendor.sla_guarantee}%")

        # Actual uptime performance (0-30 points)
        if self.vendor.actual_uptime >= self.vendor.sla_guarantee:
            score += 30
        elif self.vendor.actual_uptime >= (self.vendor.sla_guarantee - 0.5):
            score += 20
        elif self.vendor.actual_uptime >= (self.vendor.sla_guarantee - 1.0):
            score += 10
        else:
            logger.warning(f"Poor uptime performance for {self.vendor.name}: {self.vendor.actual_uptime}%")

        # Support response times (assumed 20 points if SLA is good)
        if self.vendor.sla_guarantee >= 99.5:
            score += 20

        # Disaster recovery testing (assumed 10 points if ISO certified)
        if self.vendor.iso27001_certified:
            score += 10

        self.scores['reliability'] = score
        logger.info(f"Reliability score for {self.vendor.name}: {score}/100")
        return score

    def evaluate_data_residency(self) -> float:
        """
        Evaluate data residency controls (max 100 points).

        Criteria:
        - Geographic data center selectability: 0-40 points
        - Subprocessor location transparency: 0-30 points
        - Standard Contractual Clauses: 0-20 points
        - Data localization capabilities: 0-10 points

        Returns:
            Data residency score (0-100)
        """
        score = 0.0

        # Geographic data center selectability (0-40 points)
        if len(self.vendor.data_center_locations) >= 3:
            score += 40
        elif len(self.vendor.data_center_locations) >= 2:
            score += 30
        elif len(self.vendor.data_center_locations) >= 1:
            score += 20

        # Subprocessor location transparency (0-30 points)
        if len(self.vendor.subprocessors) > 0:
            score += 30
        else:
            logger.warning(f"No subprocessor information for {self.vendor.name}")

        # Standard Contractual Clauses (0-20 points)
        if self.vendor.dpa_available and self.vendor.gdpr_compliant:
            score += 20

        # Data localization capabilities (0-10 points)
        if len(self.vendor.data_center_locations) >= 2:
            score += 10

        self.scores['data_residency'] = score
        logger.info(f"Data residency score for {self.vendor.name}: {score}/100")
        return score

    def calculate_overall_score(self) -> float:
        """
        Calculate weighted overall risk score.

        Returns:
            Overall score (0-100)
        """
        # Evaluate all categories
        self.evaluate_security()
        self.evaluate_privacy()
        self.evaluate_compliance()
        self.evaluate_reliability()
        self.evaluate_data_residency()

        # Calculate weighted sum
        overall = (
            self.scores['security'] * self.WEIGHTS['security'] +
            self.scores['privacy'] * self.WEIGHTS['privacy'] +
            self.scores['compliance'] * self.WEIGHTS['compliance'] +
            self.scores['reliability'] * self.WEIGHTS['reliability'] +
            self.scores['data_residency'] * self.WEIGHTS['data_residency']
        )

        logger.info(f"Overall score for {self.vendor.name}: {overall:.2f}/100")
        return overall

    def get_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score.

        Args:
            score: Overall assessment score

        Returns:
            RiskLevel enum value
        """
        if score >= 90:
            return RiskLevel.LOW
        elif score >= 70:
            return RiskLevel.MEDIUM
        elif score >= 50:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def get_detailed_report(self) -> Dict[str, Any]:
        """
        Generate detailed assessment report.

        Returns:
            Dictionary with complete assessment details
        """
        overall_score = self.calculate_overall_score()
        risk_level = self.get_risk_level(overall_score)

        return {
            "vendor_name": self.vendor.name,
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level.value,
            "category_scores": {
                "security": round(self.scores['security'], 2),
                "privacy": round(self.scores['privacy'], 2),
                "compliance": round(self.scores['compliance'], 2),
                "reliability": round(self.scores['reliability'], 2),
                "data_residency": round(self.scores['data_residency'], 2)
            },
            "weights": self.WEIGHTS,
            "recommendation": self._get_recommendation(risk_level),
            "assessment_date": datetime.now().isoformat()
        }

    def _get_recommendation(self, risk_level: RiskLevel) -> str:
        """Get recommendation based on risk level."""
        recommendations = {
            RiskLevel.LOW: "Approved for use. Proceed with standard onboarding.",
            RiskLevel.MEDIUM: "Approved with conditions. Implement additional monitoring controls.",
            RiskLevel.HIGH: "Additional controls required. Legal and security review needed.",
            RiskLevel.CRITICAL: "Rejected. Do not proceed with this vendor."
        }
        return recommendations[risk_level]


class DPAValidator:
    """
    Data Processing Agreement (DPA) validator for 12 essential clauses.
    """

    ESSENTIAL_CLAUSES = [
        "processing_scope",
        "purpose_limitation",
        "data_security",
        "subprocessor_approval",
        "data_subject_rights",
        "breach_notification",
        "data_location",
        "cross_border_transfer",
        "audit_rights",
        "data_deletion",
        "liability",
        "termination"
    ]

    def __init__(self):
        """Initialize DPA validator."""
        logger.info("Initialized DPA validator")

    def validate_dpa(self, dpa_text: str) -> Dict[str, Any]:
        """
        Validate DPA against 12 essential clauses.

        Args:
            dpa_text: Full DPA text to validate

        Returns:
            Validation results with clause coverage
        """
        logger.info("Starting DPA validation")

        # Simple keyword-based validation (production would use NLP)
        results = {}
        clause_keywords = {
            "processing_scope": ["processing", "scope", "data processing"],
            "purpose_limitation": ["purpose", "limitation", "lawful purpose"],
            "data_security": ["security", "protect", "safeguard"],
            "subprocessor_approval": ["subprocessor", "sub-processor", "third party"],
            "data_subject_rights": ["data subject", "rights", "access"],
            "breach_notification": ["breach", "notification", "notify"],
            "data_location": ["location", "residency", "storage"],
            "cross_border_transfer": ["cross-border", "transfer", "international"],
            "audit_rights": ["audit", "inspection", "right to audit"],
            "data_deletion": ["deletion", "erasure", "destroy"],
            "liability": ["liability", "indemnity", "damages"],
            "termination": ["termination", "cessation", "end of agreement"]
        }

        dpa_lower = dpa_text.lower()

        for clause, keywords in clause_keywords.items():
            found = any(keyword in dpa_lower for keyword in keywords)
            results[clause] = {
                "present": found,
                "status": "✓" if found else "✗"
            }

            if not found:
                logger.warning(f"Missing DPA clause: {clause}")

        coverage = sum(1 for r in results.values() if r["present"]) / len(self.ESSENTIAL_CLAUSES) * 100

        return {
            "clause_results": results,
            "coverage_percentage": round(coverage, 2),
            "passed": coverage >= 100.0,
            "missing_clauses": [c for c, r in results.items() if not r["present"]]
        }


class SubprocessorRegistry:
    """
    Subprocessor management and risk inheritance tracking.
    """

    def __init__(self):
        """Initialize subprocessor registry."""
        self.registry: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("Initialized subprocessor registry")

    def register_subprocessor(
        self,
        vendor_name: str,
        subprocessor_name: str,
        location: str,
        has_dpa: bool = False
    ) -> None:
        """
        Register a subprocessor for a vendor.

        Args:
            vendor_name: Primary vendor name
            subprocessor_name: Subprocessor company name
            location: Geographic location
            has_dpa: Whether subprocessor has equivalent DPA
        """
        if vendor_name not in self.registry:
            self.registry[vendor_name] = []

        subprocessor = {
            "name": subprocessor_name,
            "location": location,
            "has_dpa": has_dpa,
            "registered_date": datetime.now().isoformat()
        }

        self.registry[vendor_name].append(subprocessor)
        logger.info(f"Registered subprocessor {subprocessor_name} for {vendor_name}")

    def get_subprocessors(self, vendor_name: str) -> List[Dict[str, Any]]:
        """
        Get all subprocessors for a vendor.

        Args:
            vendor_name: Vendor name

        Returns:
            List of subprocessor details
        """
        return self.registry.get(vendor_name, [])

    def check_risk_inheritance(self, vendor_name: str) -> Dict[str, Any]:
        """
        Check for risk inheritance from subprocessors.

        Args:
            vendor_name: Vendor name

        Returns:
            Risk inheritance analysis
        """
        subprocessors = self.get_subprocessors(vendor_name)

        if not subprocessors:
            return {
                "has_subprocessors": False,
                "risk_inherited": False,
                "issues": []
            }

        issues = []
        for sub in subprocessors:
            if not sub["has_dpa"]:
                issues.append(f"{sub['name']} lacks equivalent DPA coverage")
                logger.warning(f"Subprocessor {sub['name']} lacks DPA - risk inherited by {vendor_name}")

        return {
            "has_subprocessors": True,
            "subprocessor_count": len(subprocessors),
            "risk_inherited": len(issues) > 0,
            "issues": issues,
            "subprocessors": subprocessors
        }


class ContinuousMonitor:
    """
    Continuous monitoring for quarterly vendor reviews and incident tracking.
    """

    def __init__(self):
        """Initialize continuous monitoring system."""
        self.monitoring_schedule: Dict[str, datetime] = {}
        logger.info("Initialized continuous monitoring system")

    def schedule_review(self, vendor_name: str, review_date: Optional[datetime] = None) -> None:
        """
        Schedule quarterly review for a vendor.

        Args:
            vendor_name: Vendor name
            review_date: Optional specific review date (defaults to 90 days from now)
        """
        if review_date is None:
            review_date = datetime.now() + timedelta(days=90)

        self.monitoring_schedule[vendor_name] = review_date
        logger.info(f"Scheduled review for {vendor_name} on {review_date.date()}")

    def get_due_reviews(self) -> List[str]:
        """
        Get vendors with reviews due.

        Returns:
            List of vendor names with reviews due
        """
        now = datetime.now()
        due_vendors = [
            vendor for vendor, date in self.monitoring_schedule.items()
            if date <= now
        ]

        if due_vendors:
            logger.info(f"Found {len(due_vendors)} vendors with reviews due")

        return due_vendors

    def check_certification_expiry(
        self,
        vendor_profile: VendorProfile,
        warning_days: int = 90
    ) -> Dict[str, Any]:
        """
        Check for expiring certifications.

        Args:
            vendor_profile: Vendor profile to check
            warning_days: Days before expiry to trigger warning

        Returns:
            Expiry status and warnings
        """
        warnings = []

        if vendor_profile.soc2_date:
            # SOC 2 reports are typically valid for 1 year
            expiry_date = vendor_profile.soc2_date + timedelta(days=365)
            days_until_expiry = (expiry_date - datetime.now()).days

            if days_until_expiry <= 0:
                warnings.append(f"SOC 2 report EXPIRED on {expiry_date.date()}")
                logger.error(f"SOC 2 expired for {vendor_profile.name}")
            elif days_until_expiry <= warning_days:
                warnings.append(f"SOC 2 report expires in {days_until_expiry} days")
                logger.warning(f"SOC 2 expiring soon for {vendor_profile.name}")

        return {
            "vendor": vendor_profile.name,
            "has_warnings": len(warnings) > 0,
            "warnings": warnings
        }


def calculate_roi(vendor_count: int) -> Dict[str, Any]:
    """
    Calculate ROI for automated vs manual vendor management.

    Args:
        vendor_count: Number of vendors to manage

    Returns:
        ROI analysis with cost breakdown
    """
    # Manual costs (in INR lakhs)
    analysts_needed = vendor_count / 10
    manual_cost = analysts_needed * 8  # ₹8L per analyst

    # Automated costs (in INR lakhs)
    infrastructure_cost = 12
    maintenance_cost = 4
    automated_cost = infrastructure_cost + maintenance_cost

    # Savings
    annual_savings = manual_cost - automated_cost
    roi_percentage = (annual_savings / automated_cost) * 100 if automated_cost > 0 else 0

    logger.info(f"ROI calculation for {vendor_count} vendors: {roi_percentage:.1f}% savings")

    return {
        "vendor_count": vendor_count,
        "manual_cost_lakhs": round(manual_cost, 2),
        "automated_cost_lakhs": round(automated_cost, 2),
        "annual_savings_lakhs": round(annual_savings, 2),
        "roi_percentage": round(roi_percentage, 2),
        "breakeven_vendors": 20  # Breakeven point
    }


def multi_jurisdiction_compliance_check(
    vendor_profile: VendorProfile,
    jurisdictions: List[str]
) -> Dict[str, Any]:
    """
    Check vendor compliance across multiple jurisdictions.

    Args:
        vendor_profile: Vendor to assess
        jurisdictions: List of jurisdictions (e.g., ["GDPR", "DPDPA", "CCPA"])

    Returns:
        Compliance status for each jurisdiction
    """
    results = {}

    for jurisdiction in jurisdictions:
        if jurisdiction == "GDPR":
            compliant = vendor_profile.gdpr_compliant and vendor_profile.dpa_available
            results["GDPR"] = {
                "compliant": compliant,
                "requirements_met": ["DPA available", "GDPR certified"] if compliant else [],
                "requirements_missing": [] if compliant else ["DPA or GDPR certification"]
            }

        elif jurisdiction == "DPDPA":
            # India DPDPA requires data residency in India
            has_india_dc = "India" in vendor_profile.data_center_locations
            results["DPDPA"] = {
                "compliant": has_india_dc,
                "requirements_met": ["India data center"] if has_india_dc else [],
                "requirements_missing": [] if has_india_dc else ["India data residency"]
            }

        elif jurisdiction == "CCPA":
            # California CCPA requires privacy controls
            compliant = vendor_profile.data_deletion_automated
            results["CCPA"] = {
                "compliant": compliant,
                "requirements_met": ["Automated deletion"] if compliant else [],
                "requirements_missing": [] if compliant else ["Automated data deletion"]
            }

    overall_compliant = all(r["compliant"] for r in results.values())

    logger.info(f"Multi-jurisdiction check for {vendor_profile.name}: {'PASS' if overall_compliant else 'FAIL'}")

    return {
        "vendor": vendor_profile.name,
        "overall_compliant": overall_compliant,
        "jurisdiction_results": results
    }


def assess_vendor(
    vendor_data: Dict[str, Any],
    include_subprocessors: bool = True,
    jurisdictions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Comprehensive vendor assessment function.

    Args:
        vendor_data: Dictionary with vendor details
        include_subprocessors: Whether to check subprocessor risks
        jurisdictions: List of jurisdictions to check compliance

    Returns:
        Complete assessment results
    """
    logger.info(f"Starting comprehensive assessment for {vendor_data.get('name', 'Unknown')}")

    # Create vendor profile
    profile = VendorProfile(
        name=vendor_data.get("name", "Unknown Vendor"),
        soc2_date=vendor_data.get("soc2_date"),
        iso27001_certified=vendor_data.get("iso27001_certified", False),
        penetration_testing=vendor_data.get("penetration_testing", False),
        breach_count=vendor_data.get("breach_count", 0),
        gdpr_compliant=vendor_data.get("gdpr_compliant", False),
        dpa_available=vendor_data.get("dpa_available", False),
        data_deletion_automated=vendor_data.get("data_deletion_automated", False),
        sla_guarantee=vendor_data.get("sla_guarantee", 0.0),
        actual_uptime=vendor_data.get("actual_uptime", 0.0),
        data_center_locations=vendor_data.get("data_center_locations", []),
        subprocessors=vendor_data.get("subprocessors", [])
    )

    # Perform risk assessment
    assessment = VendorRiskAssessment(profile)
    risk_report = assessment.get_detailed_report()

    # DPA validation if available
    dpa_result = None
    if vendor_data.get("dpa_text"):
        validator = DPAValidator()
        dpa_result = validator.validate_dpa(vendor_data["dpa_text"])

    # Subprocessor check if requested
    subprocessor_risk = None
    if include_subprocessors and profile.subprocessors:
        registry = SubprocessorRegistry()
        for sub in profile.subprocessors:
            registry.register_subprocessor(
                profile.name,
                sub.get("name", "Unknown"),
                sub.get("location", "Unknown"),
                sub.get("has_dpa", False)
            )
        subprocessor_risk = registry.check_risk_inheritance(profile.name)

    # Multi-jurisdiction compliance
    jurisdiction_compliance = None
    if jurisdictions:
        jurisdiction_compliance = multi_jurisdiction_compliance_check(profile, jurisdictions)

    # Certification expiry check
    monitor = ContinuousMonitor()
    expiry_check = monitor.check_certification_expiry(profile)

    return {
        "risk_assessment": risk_report,
        "dpa_validation": dpa_result,
        "subprocessor_analysis": subprocessor_risk,
        "jurisdiction_compliance": jurisdiction_compliance,
        "certification_status": expiry_check,
        "timestamp": datetime.now().isoformat()
    }
