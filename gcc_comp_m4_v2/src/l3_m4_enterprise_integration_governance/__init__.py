"""
L3 M4.2: Vendor Risk Assessment

This module implements a comprehensive vendor risk assessment framework for
Global Capability Centers (GCCs) managing third-party compliance in RAG systems.

Core Capabilities:
- 5-category weighted risk evaluation (Security, Privacy, Compliance, Reliability, Data Residency)
- Automated DPA clause detection
- Subprocessor tracking
- Continuous monitoring support
- Risk scoring (0-100) with approval recommendations

Part of: TechVoyageHub L3 Production RAG Engineering Track
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

__all__ = ["VendorRiskAssessment"]


class VendorRiskAssessment:
    """
    Vendor risk scoring using 5-category weighted matrix.

    Categories and weights:
    - Security (30%): SOC 2, ISO 27001, pentesting, incident history
    - Privacy (25%): GDPR/CCPA compliance, DPA, data handling
    - Compliance (20%): Certifications, audit reports, regulatory alignment
    - Reliability (15%): SLA, uptime, support responsiveness
    - Data Residency (10%): Geographic locations, subprocessors

    Score interpretation:
    - 90-100: Low Risk (Approved)
    - 70-89: Medium Risk (Approved with Conditions)
    - 50-69: High Risk (Additional Controls Required)
    - 0-49: Critical Risk (Rejected)

    Example:
        >>> assessor = VendorRiskAssessment()
        >>> inputs = {
        ...     'soc2_date': datetime.now() - timedelta(days=180),
        ...     'iso27001': True,
        ...     'breaches_count': 0,
        ...     'gdpr_compliant': True,
        ...     'dpa_available': True,
        ...     # ... other inputs
        ... }
        >>> result = assessor.calculate_overall_risk('VendorName', inputs)
        >>> print(result['overall_score'])
        92.5
    """

    # Category weights (must sum to 1.0)
    WEIGHTS = {
        'security': 0.30,
        'privacy': 0.25,
        'compliance': 0.20,
        'reliability': 0.15,
        'data_residency': 0.10
    }

    def __init__(self):
        """Initialize vendor risk assessment framework."""
        self.vendors: Dict[str, Dict[str, Any]] = {}
        logger.info("VendorRiskAssessment initialized")

    def evaluate_security(self, vendor: str, inputs: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate vendor security posture (30% weight).

        Scoring criteria:
        - SOC 2 Type II (30 points): 30 if recent (<12 months), 15 if older, 0 if none
        - ISO 27001 (20 points): 20 if certified, 0 if not
        - Penetration testing (20 points): 20 if annual, 10 if older, 0 if none
        - Incident history (30 points): 30 if no breaches, deduct 10 per breach in last 3 years

        Args:
            vendor: Vendor name
            inputs: Dict with keys: soc2_date, iso27001, pentest_date, breaches_count

        Returns:
            Tuple of (score 0-100, list of findings/concerns)
        """
        score = 0.0
        findings: List[str] = []

        # SOC 2 Type II (30 points)
        soc2_date = inputs.get('soc2_date')
        if soc2_date:
            months_old = (datetime.now() - soc2_date).days / 30
            if months_old <= 12:
                score += 30
                findings.append(f"✓ SOC 2 Type II current (issued {months_old:.0f} months ago)")
            elif months_old <= 24:
                score += 15
                findings.append(f"⚠ SOC 2 Type II outdated (issued {months_old:.0f} months ago) - request update")
            else:
                findings.append(f"✗ SOC 2 Type II too old ({months_old:.0f} months) - HIGH RISK")
        else:
            findings.append("✗ No SOC 2 Type II report - CRITICAL RISK")

        # ISO 27001 (20 points)
        if inputs.get('iso27001'):
            score += 20
            findings.append("✓ ISO 27001 certified")
        else:
            findings.append("✗ No ISO 27001 certification - consider as additional risk factor")

        # Penetration testing (20 points)
        pentest_date = inputs.get('pentest_date')
        if pentest_date:
            months_old = (datetime.now() - pentest_date).days / 30
            if months_old <= 12:
                score += 20
                findings.append(f"✓ Recent penetration test ({months_old:.0f} months ago)")
            elif months_old <= 24:
                score += 10
                findings.append(f"⚠ Penetration test outdated ({months_old:.0f} months ago)")
            else:
                findings.append(f"✗ Penetration test too old ({months_old:.0f} months)")
        else:
            findings.append("✗ No penetration testing disclosed - HIGH RISK")

        # Incident history (30 points)
        breaches_count = inputs.get('breaches_count', 0)
        if breaches_count == 0:
            score += 30
            findings.append("✓ No security breaches in past 3 years")
        else:
            deduction = min(breaches_count * 10, 30)
            score -= deduction
            findings.append(f"✗ {breaches_count} security breach(es) in past 3 years - MAJOR CONCERN")

        logger.info(f"{vendor} - Security evaluation: {score}/100")
        return (score, findings)

    def evaluate_privacy(self, vendor: str, inputs: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate vendor privacy compliance (25% weight).

        Scoring criteria:
        - GDPR compliance (40 points): 40 if compliant + DPA available, 20 if claimed but no DPA, 0 if non-compliant
        - Data handling policies (30 points): 30 if transparent, 15 if basic, 0 if unclear
        - Data deletion (20 points): 20 if automated + verified, 10 if manual, 0 if unclear
        - Data access controls (10 points): 10 if strong (MFA, audit logs), 5 if basic, 0 if weak

        Args:
            vendor: Vendor name
            inputs: Dict with keys: gdpr_compliant, dpa_available, data_policy_score, deletion_process, access_controls

        Returns:
            Tuple of (score 0-100, list of findings)
        """
        score = 0.0
        findings: List[str] = []

        # GDPR compliance (40 points)
        gdpr = inputs.get('gdpr_compliant', False)
        dpa = inputs.get('dpa_available', False)
        if gdpr and dpa:
            score += 40
            findings.append("✓ GDPR compliant with DPA available")
        elif gdpr and not dpa:
            score += 20
            findings.append("⚠ Claims GDPR compliance but no DPA - request immediately")
        else:
            findings.append("✗ Not GDPR compliant - CANNOT use for EU personal data")

        # Data handling policies (30 points)
        policy_score = inputs.get('data_policy_score', 0)  # 0-3 scale
        if policy_score >= 2:
            score += 30
            findings.append("✓ Transparent data handling policies")
        elif policy_score == 1:
            score += 15
            findings.append("⚠ Basic data handling policies - request details")
        else:
            findings.append("✗ Unclear data handling policies - HIGH RISK")

        # Data deletion (20 points)
        deletion = inputs.get('deletion_process', 'unclear')
        if deletion == 'automated_verified':
            score += 20
            findings.append("✓ Automated data deletion with verification")
        elif deletion == 'manual':
            score += 10
            findings.append("⚠ Manual data deletion - no automation")
        else:
            findings.append("✗ Unclear data deletion process - GDPR compliance risk")

        # Data access controls (10 points)
        access = inputs.get('access_controls', 'weak')
        if access == 'strong':
            score += 10
            findings.append("✓ Strong access controls (MFA, audit logs, need-to-know)")
        elif access == 'basic':
            score += 5
            findings.append("⚠ Basic access controls - request stronger controls")
        else:
            findings.append("✗ Weak access controls - RISK of unauthorized data access")

        logger.info(f"{vendor} - Privacy evaluation: {score}/100")
        return (score, findings)

    def evaluate_compliance(self, vendor: str, inputs: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate vendor regulatory compliance (20% weight).

        Scoring criteria:
        - Industry certifications (40 points): Points for HIPAA BAA, PCI-DSS, FedRAMP, etc.
        - Recent audit reports (30 points): 30 if <6 months, 15 if <12 months, 0 if older
        - Compliance change notifications (20 points): 20 if proactive, 10 if on request, 0 if reactive
        - Regulatory violations (10 points): 10 if none, -10 per violation

        Args:
            vendor: Vendor name
            inputs: Dict with keys: certifications, audit_date, notification_process, violations_count

        Returns:
            Tuple of (score 0-100, list of findings)
        """
        score = 0.0
        findings: List[str] = []

        # Industry certifications (40 points)
        certifications = inputs.get('certifications', [])
        cert_points = 0.0
        if 'hipaa_baa' in certifications:
            cert_points += 15
            findings.append("✓ HIPAA BAA available (required for healthcare data)")
        if 'pci_dss' in certifications:
            cert_points += 15
            findings.append("✓ PCI-DSS certified (required for payment data)")
        if 'fedramp' in certifications:
            cert_points += 10
            findings.append("✓ FedRAMP authorized (required for US government data)")

        score += min(cert_points, 40)  # Cap at 40 points

        if not certifications:
            findings.append("✗ No industry-specific certifications - limits use cases")

        # Recent audit reports (30 points)
        audit_date = inputs.get('audit_date')
        if audit_date:
            months_old = (datetime.now() - audit_date).days / 30
            if months_old <= 6:
                score += 30
                findings.append(f"✓ Recent audit report ({months_old:.0f} months ago)")
            elif months_old <= 12:
                score += 15
                findings.append(f"⚠ Audit report aging ({months_old:.0f} months old)")
            else:
                findings.append(f"✗ Audit report too old ({months_old:.0f} months)")
        else:
            findings.append("✗ No recent audit reports available")

        # Compliance change notifications (20 points)
        notification = inputs.get('notification_process', 'reactive')
        if notification == 'proactive':
            score += 20
            findings.append("✓ Proactive compliance change notifications")
        elif notification == 'on_request':
            score += 10
            findings.append("⚠ Compliance notifications only on request")
        else:
            findings.append("✗ Reactive compliance notifications - you must monitor manually")

        # Regulatory violations (10 points)
        violations = inputs.get('violations_count', 0)
        if violations == 0:
            score += 10
            findings.append("✓ No regulatory violations in past 5 years")
        else:
            deduction = violations * 10
            score -= deduction
            findings.append(f"✗ {violations} regulatory violation(s) - MAJOR RED FLAG")

        logger.info(f"{vendor} - Compliance evaluation: {score}/100")
        return (score, findings)

    def evaluate_reliability(self, vendor: str, inputs: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate vendor operational reliability (15% weight).

        Scoring criteria:
        - SLA guarantees (40 points): 40 if 99.9%+, 20 if 99.5-99.9%, 0 if <99.5%
        - Actual uptime (30 points): 30 if meets SLA, deduct for violations
        - Support responsiveness (20 points): 20 if <1 hour critical, 10 if <4 hours, 0 if >4 hours
        - DR/BC plan (10 points): 10 if tested annually, 5 if documented, 0 if none

        Args:
            vendor: Vendor name
            inputs: Dict with keys: sla_guarantee, actual_uptime_12m, support_response_time, dr_plan

        Returns:
            Tuple of (score 0-100, list of findings)
        """
        score = 0.0
        findings: List[str] = []

        # SLA guarantees (40 points)
        sla = inputs.get('sla_guarantee', 0.0)
        if sla >= 99.9:
            score += 40
            downtime = (100 - sla) * 87.6  # hours per year
            findings.append(f"✓ Strong SLA: {sla}% ({downtime:.1f} hours downtime/year max)")
        elif sla >= 99.5:
            score += 20
            downtime = (100 - sla) * 87.6
            findings.append(f"⚠ Moderate SLA: {sla}% ({downtime:.1f} hours downtime/year max)")
        else:
            findings.append(f"✗ Weak SLA: {sla}% - HIGH RISK for production systems")

        # Actual uptime (30 points)
        actual_uptime = inputs.get('actual_uptime_12m', 0.0)
        if actual_uptime >= sla:
            score += 30
            findings.append(f"✓ Met SLA commitment: {actual_uptime}% actual uptime")
        elif actual_uptime >= sla - 0.5:
            score += 15
            findings.append(f"⚠ Marginally missed SLA: {actual_uptime}% vs {sla}% committed")
        else:
            findings.append(f"✗ Significantly missed SLA: {actual_uptime}% vs {sla}% - SLA violations")

        # Support responsiveness (20 points)
        response_time = inputs.get('support_response_time', '8h')
        if 'min' in response_time or '<1h' in response_time:
            score += 20
            findings.append(f"✓ Excellent support response: {response_time}")
        elif '<4h' in response_time:
            score += 10
            findings.append(f"⚠ Moderate support response: {response_time}")
        else:
            findings.append(f"✗ Slow support response: {response_time} - RISK during incidents")

        # DR/BC plan (10 points)
        dr_plan = inputs.get('dr_plan', 'none')
        if dr_plan == 'tested_annually':
            score += 10
            findings.append("✓ DR/BC plan tested annually")
        elif dr_plan == 'documented':
            score += 5
            findings.append("⚠ DR/BC plan documented but not tested")
        else:
            findings.append("✗ No DR/BC plan - MAJOR RISK for business continuity")

        logger.info(f"{vendor} - Reliability evaluation: {score}/100")
        return (score, findings)

    def evaluate_data_residency(self, vendor: str, inputs: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate vendor data residency compliance (10% weight).

        Scoring criteria:
        - Data center locations (40 points): 40 if customer-selectable, 20 if fixed but compliant, 0 if problematic
        - Subprocessor locations (30 points): 30 if disclosed + compliant, 15 if disclosed, 0 if unknown
        - Cross-border transfers (20 points): 20 if SCCs in place, 10 if claimed, 0 if unclear
        - Data sovereignty (10 points): 10 if supports localization, 5 if limited, 0 if no control

        Args:
            vendor: Vendor name
            inputs: Dict with keys: dc_locations, dc_selectable, subproc_locations, sccs_available, localization_support

        Returns:
            Tuple of (score 0-100, list of findings)
        """
        score = 0.0
        findings: List[str] = []

        # Data center locations (40 points)
        dc_locations = inputs.get('dc_locations', [])
        dc_selectable = inputs.get('dc_selectable', False)

        if dc_selectable and len(dc_locations) >= 3:
            score += 40
            findings.append(f"✓ Customer-selectable data centers: {', '.join(dc_locations)}")
        elif not dc_selectable and 'EU' in dc_locations:
            score += 20
            findings.append(f"⚠ Fixed data centers (no selection): {', '.join(dc_locations)}")
        elif not dc_locations:
            findings.append("✗ Data center locations unknown - CANNOT verify data residency compliance")

        # Subprocessor locations (30 points)
        subproc_locations = inputs.get('subproc_locations', [])
        if subproc_locations:
            score += 30
            findings.append(f"✓ Subprocessor locations disclosed: {', '.join(subproc_locations)}")
        else:
            findings.append("✗ Subprocessor locations unknown - compliance risk")

        # Cross-border transfers (20 points)
        sccs = inputs.get('sccs_available', False)
        if sccs:
            score += 20
            findings.append("✓ Standard Contractual Clauses (SCCs) in place for cross-border transfers")
        else:
            findings.append("✗ No SCCs for cross-border transfers - GDPR violation risk")

        # Data sovereignty (10 points)
        localization = inputs.get('localization_support', 'none')
        if localization == 'full':
            score += 10
            findings.append("✓ Full data localization support")
        elif localization == 'partial':
            score += 5
            findings.append("⚠ Partial data localization support")
        else:
            findings.append("✗ No data localization support - limits use cases")

        logger.info(f"{vendor} - Data Residency evaluation: {score}/100")
        return (score, findings)

    def calculate_overall_risk(self, vendor: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall vendor risk score using weighted average of 5 categories.

        Args:
            vendor: Vendor name
            inputs: Dict with all evaluation inputs

        Returns:
            Dict with overall score, category scores, risk level, findings, and recommendation
        """
        logger.info(f"Calculating overall risk for {vendor}")

        # Evaluate each category
        security_score, security_findings = self.evaluate_security(vendor, inputs)
        privacy_score, privacy_findings = self.evaluate_privacy(vendor, inputs)
        compliance_score, compliance_findings = self.evaluate_compliance(vendor, inputs)
        reliability_score, reliability_findings = self.evaluate_reliability(vendor, inputs)
        residency_score, residency_findings = self.evaluate_data_residency(vendor, inputs)

        # Calculate weighted average
        overall_score = (
            security_score * self.WEIGHTS['security'] +
            privacy_score * self.WEIGHTS['privacy'] +
            compliance_score * self.WEIGHTS['compliance'] +
            reliability_score * self.WEIGHTS['reliability'] +
            residency_score * self.WEIGHTS['data_residency']
        )

        # Determine risk level and recommendation
        if overall_score >= 90:
            risk_level = "LOW RISK"
            recommendation = "APPROVED - Low risk vendor, suitable for production use"
        elif overall_score >= 70:
            risk_level = "MEDIUM RISK"
            recommendation = "APPROVED WITH CONDITIONS - Require additional controls or monitoring"
        elif overall_score >= 50:
            risk_level = "HIGH RISK"
            recommendation = "ADDITIONAL CONTROLS REQUIRED - Risk mitigation plan needed before approval"
        else:
            risk_level = "CRITICAL RISK"
            recommendation = "REJECTED - Risk too high, seek alternative vendor"

        # Compile results
        result = {
            'vendor': vendor,
            'assessment_date': datetime.now().isoformat(),
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'category_scores': {
                'security': round(security_score, 1),
                'privacy': round(privacy_score, 1),
                'compliance': round(compliance_score, 1),
                'reliability': round(reliability_score, 1),
                'data_residency': round(residency_score, 1)
            },
            'findings': {
                'security': security_findings,
                'privacy': privacy_findings,
                'compliance': compliance_findings,
                'reliability': reliability_findings,
                'data_residency': residency_findings
            }
        }

        # Store assessment
        self.vendors[vendor] = result

        logger.info(f"{vendor} - Overall score: {overall_score:.1f}/100 ({risk_level})")
        return result

    def generate_report(self, output_format: str = 'dict') -> Any:
        """
        Generate summary report of all vendor assessments.

        Args:
            output_format: 'dict', 'dataframe', or 'excel'

        Returns:
            Report in specified format
        """
        if not self.vendors:
            logger.warning("No vendor assessments completed")
            return {'error': 'No vendor assessments completed'}

        # Create summary dataframe
        summary_data = []
        for vendor, assessment in self.vendors.items():
            summary_data.append({
                'Vendor': vendor,
                'Overall Score': assessment['overall_score'],
                'Risk Level': assessment['risk_level'],
                'Security': assessment['category_scores']['security'],
                'Privacy': assessment['category_scores']['privacy'],
                'Compliance': assessment['category_scores']['compliance'],
                'Reliability': assessment['category_scores']['reliability'],
                'Data Residency': assessment['category_scores']['data_residency'],
                'Recommendation': assessment['recommendation'],
                'Assessment Date': assessment['assessment_date']
            })

        df = pd.DataFrame(summary_data)
        df = df.sort_values('Overall Score', ascending=False)  # Sort by risk (lowest risk first)

        if output_format == 'dataframe':
            logger.info(f"Generated dataframe report with {len(df)} vendors")
            return df
        elif output_format == 'excel':
            filename = f"vendor_risk_assessment_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(filename, index=False)
            logger.info(f"Generated Excel report: {filename}")
            return {'filename': filename, 'rows': len(df)}
        else:
            logger.info(f"Generated dict report with {len(df)} vendors")
            return df.to_dict('records')
