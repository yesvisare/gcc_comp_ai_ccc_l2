"""
L3 M4.4: Compliance Maturity & Continuous Improvement

This module implements a comprehensive compliance maturity assessment framework
for GCC environments, including 5-level maturity scoring, gap analysis, metrics
trending, and continuous improvement planning based on PDCA cycles.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

__all__ = [
    "MaturityLevel",
    "Dimension",
    "AssessmentQuestion",
    "MaturityAssessment",
    "GapAnalysis",
    "MetricsTracker",
    "ImprovementRoadmap",
    "PDCACycle",
    "generate_maturity_report",
    "calculate_overall_maturity",
    "create_improvement_plan"
]


class MaturityLevel(IntEnum):
    """5-level compliance maturity framework."""
    LEVEL1_AD_HOC = 1
    LEVEL2_REACTIVE = 2
    LEVEL3_DEFINED = 3
    LEVEL4_MEASURED = 4
    LEVEL5_OPTIMIZING = 5

    @property
    def description(self) -> str:
        descriptions = {
            1: "Ad-hoc (Initial) - Reactive, inconsistent compliance",
            2: "Reactive (Managed) - Basic processes, project-specific",
            3: "Defined (Proactive) - Standardized org-wide processes",
            4: "Quantitatively Managed (Measured) - Metrics-driven decisions",
            5: "Optimizing (Continuous Improvement) - Innovation culture"
        }
        return descriptions[self.value]


class Dimension(str):
    """Five dimensions of compliance maturity."""
    PEOPLE = "People"
    PROCESS = "Process"
    TECHNOLOGY = "Technology"
    METRICS = "Metrics"
    CULTURE = "Culture"

    @classmethod
    def all_dimensions(cls) -> List[str]:
        return [cls.PEOPLE, cls.PROCESS, cls.TECHNOLOGY, cls.METRICS, cls.CULTURE]


@dataclass
class AssessmentQuestion:
    """Represents a single maturity assessment question."""
    dimension: str
    question: str
    level_indicators: Dict[int, str]
    weight: float = 1.0

    def score_response(self, selected_level: int) -> int:
        """Validate and return the selected maturity level."""
        if selected_level not in range(1, 6):
            raise ValueError(f"Level must be 1-5, got {selected_level}")
        return selected_level


@dataclass
class MaturityScore:
    """Represents maturity scores across dimensions."""
    people: float
    process: float
    technology: float
    metrics: float
    culture: float
    overall: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "people": self.people,
            "process": self.process,
            "technology": self.technology,
            "metrics": self.metrics,
            "culture": self.culture,
            "overall": self.overall,
            "overall_description": MaturityLevel(self.overall).description
        }


class MaturityAssessment:
    """Main class for conducting compliance maturity assessments."""

    def __init__(self):
        """Initialize assessment with predefined questions."""
        self.questions = self._build_questionnaire()
        self.responses: Dict[str, int] = {}
        logger.info("Initialized MaturityAssessment with 25 questions")

    def _build_questionnaire(self) -> List[AssessmentQuestion]:
        """Build the complete 25-question assessment (5 per dimension)."""
        questions = []

        # PEOPLE DIMENSION (5 questions)
        questions.extend([
            AssessmentQuestion(
                dimension=Dimension.PEOPLE,
                question="How mature is your compliance training program?",
                level_indicators={
                    1: "No formal training program",
                    2: "Annual training (checkbox compliance)",
                    3: "Quarterly training with knowledge testing",
                    4: "Role-specific training with certification",
                    5: "Continuous learning with gamification"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PEOPLE,
                question="How is compliance expertise distributed?",
                level_indicators={
                    1: "1-2 people know compliance",
                    2: "Compliance officer hired, team unaware",
                    3: "Compliance champions in each team",
                    4: "All engineers trained on core requirements",
                    5: "Compliance expertise as career path"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PEOPLE,
                question="How do you onboard new engineers on compliance?",
                level_indicators={
                    1: "No onboarding, learn by mistakes",
                    2: "Compliance mentioned in general onboarding",
                    3: "Dedicated compliance onboarding session",
                    4: "Hands-on compliance labs during onboarding",
                    5: "Mentorship program with compliance projects"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PEOPLE,
                question="How are compliance responsibilities defined?",
                level_indicators={
                    1: "Undefined, 'someone else's problem'",
                    2: "Compliance team responsible",
                    3: "Shared ownership in role descriptions",
                    4: "Compliance in OKRs and performance reviews",
                    5: "Compliance as promotion criterion"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PEOPLE,
                question="What's the consequence of compliance violations?",
                level_indicators={
                    1: "No consequences or inconsistent",
                    2: "Manager discussion after incident",
                    3: "Documented warnings for repeated violations",
                    4: "Impact on performance rating",
                    5: "Termination for severe violations (enforced)"
                }
            )
        ])

        # PROCESS DIMENSION (5 questions)
        questions.extend([
            AssessmentQuestion(
                dimension=Dimension.PROCESS,
                question="How documented are your compliance processes?",
                level_indicators={
                    1: "Undocumented, tribal knowledge",
                    2: "High-level policies exist",
                    3: "Detailed procedures with examples",
                    4: "Runbooks with decision trees",
                    5: "Living documentation with version control"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PROCESS,
                question="How do you handle compliance exceptions?",
                level_indicators={
                    1: "No formal process, ad-hoc",
                    2: "Email approval from manager",
                    3: "Documented exception request process",
                    4: "Exception tracking with expiration dates",
                    5: "Automated exception lifecycle management"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PROCESS,
                question="How integrated is compliance in your SDLC?",
                level_indicators={
                    1: "Post-deployment compliance checks",
                    2: "Compliance review in UAT phase",
                    3: "Compliance requirements in design phase",
                    4: "Compliance gates in CI/CD pipeline",
                    5: "Shift-left with compliance IDE plugins"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PROCESS,
                question="How do you manage compliance SLAs?",
                level_indicators={
                    1: "No SLAs defined",
                    2: "Informal target timelines",
                    3: "Documented SLAs (e.g., 4hr MTTR for Sev1)",
                    4: "SLA tracking with escalation process",
                    5: "SLA prediction with proactive alerts"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.PROCESS,
                question="How often do you update compliance processes?",
                level_indicators={
                    1: "Never or only when auditor requires",
                    2: "Annually after audit findings",
                    3: "Quarterly process reviews",
                    4: "Continuous improvement based on metrics",
                    5: "Real-time adaptation to regulation changes"
                }
            )
        ])

        # TECHNOLOGY DIMENSION (5 questions)
        questions.extend([
            AssessmentQuestion(
                dimension=Dimension.TECHNOLOGY,
                question="How automated is your PII detection?",
                level_indicators={
                    1: "No PII detection before embedding",
                    2: "Manual PII review (sampling)",
                    3: "Regex-based automated detection",
                    4: "NER models with accuracy validation",
                    5: "AI-powered with continuous retraining"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.TECHNOLOGY,
                question="How is access control implemented?",
                level_indicators={
                    1: "No RBAC, shared credentials",
                    2: "Basic RBAC (admin vs. user)",
                    3: "Attribute-based access control (ABAC)",
                    4: "Dynamic access with context awareness",
                    5: "Zero-trust architecture with continuous auth"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.TECHNOLOGY,
                question="How complete are your audit trails?",
                level_indicators={
                    1: "No audit logging",
                    2: "Basic application logs",
                    3: "Structured audit logs (who/what/when)",
                    4: "Tamper-proof audit trails (>99.5% complete)",
                    5: "Blockchain-based immutable audit logs"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.TECHNOLOGY,
                question="How do you test compliance controls?",
                level_indicators={
                    1: "No automated testing",
                    2: "Manual testing before releases",
                    3: "Automated compliance tests in CI/CD",
                    4: "Continuous compliance scanning (OPA policies)",
                    5: "Chaos engineering for compliance resilience"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.TECHNOLOGY,
                question="How do you manage encryption keys?",
                level_indicators={
                    1: "Hardcoded keys in code",
                    2: "Environment variables",
                    3: "Secrets management tool (Vault, AWS KMS)",
                    4: "Automatic key rotation with audit",
                    5: "HSM with FIPS 140-2 Level 3 compliance"
                }
            )
        ])

        # METRICS DIMENSION (5 questions)
        questions.extend([
            AssessmentQuestion(
                dimension=Dimension.METRICS,
                question="What compliance metrics do you track?",
                level_indicators={
                    1: "No metrics tracking",
                    2: "Incident count (reactive)",
                    3: "Proactive metrics (PII accuracy, audit completeness)",
                    4: "Trending dashboards with thresholds",
                    5: "Predictive analytics for compliance risks"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.METRICS,
                question="How visible are compliance metrics?",
                level_indicators={
                    1: "Hidden in compliance team spreadsheets",
                    2: "Quarterly reports to leadership",
                    3: "Dashboards accessible to all engineers",
                    4: "Real-time dashboards in team spaces",
                    5: "Gamified metrics with leaderboards"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.METRICS,
                question="How do you respond to metric degradation?",
                level_indicators={
                    1: "Metrics ignored or not noticed",
                    2: "Discussed in retrospectives",
                    3: "Root cause analysis within 48 hours",
                    4: "Automated alerts with runbook links",
                    5: "Auto-remediation for common issues"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.METRICS,
                question="What's your PII detection accuracy target?",
                level_indicators={
                    1: "No target defined",
                    2: "Informal goal ('good enough')",
                    3: "Documented target (e.g., >95%)",
                    4: "Monitored target (>99% TP, <1% FP)",
                    5: "Continuously optimized (>99.5%)"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.METRICS,
                question="How do you track training effectiveness?",
                level_indicators={
                    1: "No tracking",
                    2: "Completion rates only",
                    3: "Quiz scores tracked",
                    4: "Correlation between training and incidents",
                    5: "Predictive models for training needs"
                }
            )
        ])

        # CULTURE DIMENSION (5 questions)
        questions.extend([
            AssessmentQuestion(
                dimension=Dimension.CULTURE,
                question="How does leadership view compliance?",
                level_indicators={
                    1: "Compliance is IT/legal's problem",
                    2: "Necessary evil for audits",
                    3: "Risk management priority",
                    4: "Competitive differentiator",
                    5: "Core company value and brand promise"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.CULTURE,
                question="How do teams react to compliance requirements?",
                level_indicators={
                    1: "Active resistance, workarounds",
                    2: "Grudging acceptance",
                    3: "Neutral, follow checklist",
                    4: "Proactive, suggest improvements",
                    5: "Championed, integrated in design thinking"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.CULTURE,
                question="How are compliance failures handled?",
                level_indicators={
                    1: "Blame individuals, cover up",
                    2: "Fix symptom, move on",
                    3: "Blameless postmortems",
                    4: "Shared learnings across teams",
                    5: "Public case studies, industry sharing"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.CULTURE,
                question="How is compliance innovation rewarded?",
                level_indicators={
                    1: "Not recognized",
                    2: "Informal thanks",
                    3: "Mentioned in team meetings",
                    4: "Spot bonuses for improvements",
                    5: "Hackathons, innovation time, promotions"
                }
            ),
            AssessmentQuestion(
                dimension=Dimension.CULTURE,
                question="How transparent is compliance information?",
                level_indicators={
                    1: "Hidden, need-to-know only",
                    2: "Compliance team has access",
                    3: "All employees can view policies",
                    4: "Real-time metrics visible to all",
                    5: "Public compliance reports (trust building)"
                }
            )
        ])

        return questions

    def collect_responses(self, responses: Dict[str, int]) -> None:
        """
        Collect assessment responses.

        Args:
            responses: Dict mapping question text to selected level (1-5)

        Raises:
            ValueError: If response level is invalid
        """
        logger.info(f"Collecting {len(responses)} assessment responses")

        for question_text, level in responses.items():
            # Find matching question
            matching = [q for q in self.questions if q.question == question_text]
            if not matching:
                logger.warning(f"Unknown question: {question_text}")
                continue

            question = matching[0]
            validated_level = question.score_response(level)
            self.responses[question_text] = validated_level

        logger.info(f"Validated {len(self.responses)} responses")

    def calculate_maturity_scores(self) -> MaturityScore:
        """
        Calculate maturity scores across all dimensions.

        Returns:
            MaturityScore with per-dimension averages and overall score
        """
        logger.info("Calculating maturity scores across 5 dimensions")

        dimension_scores: Dict[str, List[int]] = {dim: [] for dim in Dimension.all_dimensions()}

        for question in self.questions:
            if question.question in self.responses:
                score = self.responses[question.question]
                dimension_scores[question.dimension].append(score)

        # Calculate averages
        averages = {}
        for dim in Dimension.all_dimensions():
            if dimension_scores[dim]:
                averages[dim.lower()] = sum(dimension_scores[dim]) / len(dimension_scores[dim])
            else:
                averages[dim.lower()] = 0.0
                logger.warning(f"No responses for dimension: {dim}")

        # Overall = LOWEST dimension (weakest link rule)
        overall = int(min(averages.values())) if averages else 1

        maturity_score = MaturityScore(
            people=averages.get("people", 0.0),
            process=averages.get("process", 0.0),
            technology=averages.get("technology", 0.0),
            metrics=averages.get("metrics", 0.0),
            culture=averages.get("culture", 0.0),
            overall=overall
        )

        logger.info(f"Calculated overall maturity: Level {overall}")
        return maturity_score

    def get_overall_maturity_level(self) -> MaturityLevel:
        """Get the overall maturity level (weakest link)."""
        scores = self.calculate_maturity_scores()
        return MaturityLevel(scores.overall)

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive maturity assessment report.

        Returns:
            Dict containing scores, analysis, and recommendations
        """
        logger.info("Generating maturity assessment report")

        scores = self.calculate_maturity_scores()
        overall_level = MaturityLevel(scores.overall)

        # Identify limiting dimension (lowest score)
        dim_scores = {
            "People": scores.people,
            "Process": scores.process,
            "Technology": scores.technology,
            "Metrics": scores.metrics,
            "Culture": scores.culture
        }
        limiting_dimension = min(dim_scores, key=dim_scores.get)

        # Generate recommendations based on current level
        recommendations = self._generate_recommendations(overall_level, limiting_dimension)

        report = {
            "assessment_date": datetime.now().isoformat(),
            "responses_collected": len(self.responses),
            "scores": scores.to_dict(),
            "limiting_dimension": limiting_dimension,
            "limiting_score": dim_scores[limiting_dimension],
            "recommendations": recommendations,
            "next_target_level": min(overall_level.value + 1, 5),
            "estimated_timeline": self._estimate_timeline(overall_level.value)
        }

        logger.info(f"Report generated: Level {overall_level.value}, limiting dimension: {limiting_dimension}")
        return report

    def _generate_recommendations(self, level: MaturityLevel, limiting_dim: str) -> List[str]:
        """Generate specific recommendations based on maturity level."""
        recommendations = []

        if level == MaturityLevel.LEVEL1_AD_HOC:
            recommendations.extend([
                f"URGENT: Focus on {limiting_dim} dimension - this is blocking all progress",
                "Hire or designate a compliance officer",
                "Document top 3 compliance processes (PII detection, access control, audit logging)",
                "Implement basic automated PII detection (regex-based)",
                "Start tracking incident count as baseline metric"
            ])
        elif level == MaturityLevel.LEVEL2_REACTIVE:
            recommendations.extend([
                f"Prioritize {limiting_dim} dimension to reach Level 3",
                "Move from reactive to proactive compliance",
                "Implement automated compliance tests in CI/CD",
                "Establish quarterly training program with testing",
                "Create compliance champions in each team"
            ])
        elif level == MaturityLevel.LEVEL3_DEFINED:
            recommendations.extend([
                f"Strengthen {limiting_dim} dimension for Level 4 advancement",
                "Implement metrics trending dashboards (Grafana)",
                "Set quantitative targets (>99% PII accuracy, <4hr MTTR)",
                "Introduce role-specific compliance certification",
                "Deploy OPA policies for continuous compliance scanning"
            ])
        elif level == MaturityLevel.LEVEL4_MEASURED:
            recommendations.extend([
                f"Optimize {limiting_dim} dimension for Level 5 excellence",
                "Implement predictive analytics for compliance risks",
                "Deploy AI-powered PII detection with continuous retraining",
                "Create compliance innovation time (hackathons)",
                "Publish public compliance reports for transparency"
            ])
        else:  # Level 5
            recommendations.extend([
                "Maintain excellence through continuous PDCA cycles",
                "Share best practices with industry",
                "Mentor other GCCs on compliance maturity",
                "Explore emerging technologies (blockchain audit trails, zero-trust)",
                f"Monitor {limiting_dim} dimension to prevent regression"
            ])

        return recommendations

    def _estimate_timeline(self, current_level: int) -> str:
        """Estimate timeline to reach next maturity level."""
        timelines = {
            1: "6-12 months to reach Level 2 (requires organizational buy-in)",
            2: "9-12 months to reach Level 3 (process standardization takes time)",
            3: "12-18 months to reach Level 4 (metrics maturity is gradual)",
            4: "18-24 months to reach Level 5 (culture change is slow)",
            5: "Maintain through continuous 3-month PDCA cycles"
        }
        return timelines.get(current_level, "Unknown")


class GapAnalysis:
    """Performs gap analysis between current and target maturity states."""

    def __init__(self, current_score: MaturityScore, target_level: int):
        """
        Initialize gap analysis.

        Args:
            current_score: Current maturity scores
            target_level: Target maturity level (1-5)
        """
        self.current = current_score
        self.target = target_level
        logger.info(f"Initialized gap analysis: Current L{current_score.overall} → Target L{target_level}")

    def identify_gaps(self) -> Dict[str, Any]:
        """
        Identify gaps between current and target state.

        Returns:
            Dict containing gap analysis with prioritized improvements
        """
        logger.info("Performing gap analysis")

        gaps = {}
        dimensions = {
            "People": self.current.people,
            "Process": self.current.process,
            "Technology": self.current.technology,
            "Metrics": self.current.metrics,
            "Culture": self.current.culture
        }

        for dim, score in dimensions.items():
            gap = self.target - score
            if gap > 0:
                gaps[dim] = {
                    "current": score,
                    "target": self.target,
                    "gap": gap,
                    "priority": "High" if gap >= 2 else "Medium" if gap >= 1 else "Low"
                }

        # Sort by gap size (descending)
        sorted_gaps = dict(sorted(gaps.items(), key=lambda x: x[1]["gap"], reverse=True))

        analysis = {
            "gaps_identified": len(sorted_gaps),
            "dimension_gaps": sorted_gaps,
            "total_effort_estimate": self._estimate_effort(sorted_gaps),
            "recommended_sequence": self._recommend_sequence(sorted_gaps)
        }

        logger.info(f"Identified {len(sorted_gaps)} dimension gaps")
        return analysis

    def _estimate_effort(self, gaps: Dict[str, Any]) -> str:
        """Estimate total effort required to close gaps."""
        total_gap = sum(g["gap"] for g in gaps.values())

        if total_gap < 2:
            return "Low (1-2 quarters)"
        elif total_gap < 4:
            return "Medium (2-4 quarters)"
        elif total_gap < 6:
            return "High (4-6 quarters)"
        else:
            return "Very High (6+ quarters)"

    def _recommend_sequence(self, gaps: Dict[str, Any]) -> List[str]:
        """Recommend sequence for addressing gaps."""
        # Culture and People first (foundation), then Process, then Technology/Metrics
        priority_order = ["Culture", "People", "Process", "Technology", "Metrics"]

        sequence = []
        for dim in priority_order:
            if dim in gaps:
                sequence.append(f"{dim} (gap: {gaps[dim]['gap']:.1f} levels)")

        return sequence


@dataclass
class ComplianceMetric:
    """Represents a compliance metric with trending data."""
    name: str
    current_value: float
    target_value: float
    unit: str
    trend_direction: str  # "improving", "stable", "degrading"
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)

    @property
    def is_meeting_target(self) -> bool:
        """Check if current value meets target."""
        # For accuracy metrics, higher is better
        if "accuracy" in self.name.lower() or "completeness" in self.name.lower():
            return self.current_value >= self.target_value
        # For violation/incident metrics, lower is better
        elif "violation" in self.name.lower() or "incident" in self.name.lower():
            return self.current_value <= self.target_value
        # For MTTR, lower is better
        elif "mttr" in self.name.lower():
            return self.current_value <= self.target_value
        else:
            return abs(self.current_value - self.target_value) < 0.05


class MetricsTracker:
    """Tracks compliance metrics over time and generates trending dashboards."""

    def __init__(self):
        """Initialize metrics tracker with standard compliance metrics."""
        self.metrics: Dict[str, ComplianceMetric] = {}
        self._initialize_standard_metrics()
        logger.info("Initialized MetricsTracker with 6 standard metrics")

    def _initialize_standard_metrics(self) -> None:
        """Initialize the 6 key compliance metrics."""
        self.metrics = {
            "pii_detection_accuracy": ComplianceMetric(
                name="PII Detection Accuracy",
                current_value=0.0,
                target_value=99.0,
                unit="%",
                trend_direction="stable"
            ),
            "audit_trail_completeness": ComplianceMetric(
                name="Audit Trail Completeness",
                current_value=0.0,
                target_value=99.5,
                unit="%",
                trend_direction="stable"
            ),
            "access_violations": ComplianceMetric(
                name="Access Violations",
                current_value=0.0,
                target_value=0.1,
                unit="% of queries",
                trend_direction="stable"
            ),
            "incident_mttr": ComplianceMetric(
                name="Incident MTTR (Severity 1)",
                current_value=0.0,
                target_value=4.0,
                unit="hours",
                trend_direction="stable"
            ),
            "compliance_test_coverage": ComplianceMetric(
                name="Compliance Test Coverage",
                current_value=0.0,
                target_value=95.0,
                unit="%",
                trend_direction="stable"
            ),
            "training_completion_rate": ComplianceMetric(
                name="Training Completion Rate",
                current_value=0.0,
                target_value=100.0,
                unit="%",
                trend_direction="stable"
            )
        }

    def update_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None) -> None:
        """
        Update a metric with new value.

        Args:
            metric_name: Name of the metric
            value: New metric value
            timestamp: Optional timestamp (defaults to now)
        """
        if metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {metric_name}")
            return

        ts = timestamp or datetime.now()
        metric = self.metrics[metric_name]

        # Store historical value
        metric.historical_values.append((ts, metric.current_value))

        # Update current value
        old_value = metric.current_value
        metric.current_value = value

        # Update trend direction
        if len(metric.historical_values) >= 3:
            recent_values = [v for _, v in metric.historical_values[-3:]]
            if all(recent_values[i] < recent_values[i+1] for i in range(len(recent_values)-1)):
                metric.trend_direction = "improving"
            elif all(recent_values[i] > recent_values[i+1] for i in range(len(recent_values)-1)):
                metric.trend_direction = "degrading"
            else:
                metric.trend_direction = "stable"

        logger.info(f"Updated {metric_name}: {old_value} → {value} ({metric.trend_direction})")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics with status."""
        summary = {
            "total_metrics": len(self.metrics),
            "meeting_target": 0,
            "degrading": 0,
            "metrics": {}
        }

        for name, metric in self.metrics.items():
            summary["metrics"][name] = {
                "current": metric.current_value,
                "target": metric.target_value,
                "unit": metric.unit,
                "trend": metric.trend_direction,
                "meeting_target": metric.is_meeting_target
            }

            if metric.is_meeting_target:
                summary["meeting_target"] += 1
            if metric.trend_direction == "degrading":
                summary["degrading"] += 1

        return summary

    def detect_regressions(self) -> List[str]:
        """Detect metrics moving in wrong direction."""
        regressions = []

        for name, metric in self.metrics.items():
            if metric.trend_direction == "degrading":
                regressions.append(
                    f"{metric.name}: {metric.current_value}{metric.unit} "
                    f"(target: {metric.target_value}{metric.unit}) - DEGRADING"
                )

        if regressions:
            logger.warning(f"Detected {len(regressions)} metric regressions")

        return regressions


@dataclass
class Initiative:
    """Represents an improvement initiative."""
    title: str
    description: str
    dimension: str
    owner: str
    timeline_weeks: int
    impact: str  # "Low", "Medium", "High"
    effort: str  # "Low", "Medium", "High"
    status: str = "Planned"  # "Planned", "In Progress", "Completed", "Abandoned"
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None


class ImprovementRoadmap:
    """Creates and manages compliance improvement roadmaps."""

    def __init__(self, gap_analysis: Dict[str, Any]):
        """
        Initialize roadmap from gap analysis.

        Args:
            gap_analysis: Gap analysis results
        """
        self.gaps = gap_analysis
        self.initiatives: List[Initiative] = []
        logger.info("Initialized ImprovementRoadmap")

    def create_initiatives(self, max_concurrent: int = 3) -> List[Initiative]:
        """
        Create prioritized initiatives based on gaps.

        Args:
            max_concurrent: Maximum concurrent initiatives (default: 3)

        Returns:
            List of Initiative objects
        """
        logger.info(f"Creating improvement initiatives (max concurrent: {max_concurrent})")

        initiatives = []
        dimension_gaps = self.gaps.get("dimension_gaps", {})

        # Create initiatives for each gap
        for dimension, gap_info in dimension_gaps.items():
            gap_size = gap_info["gap"]

            if gap_size >= 2:  # Major gap
                initiatives.append(Initiative(
                    title=f"Major {dimension} Improvement",
                    description=f"Close {gap_size:.1f} level gap in {dimension}",
                    dimension=dimension,
                    owner="TBD",
                    timeline_weeks=16,
                    impact="High",
                    effort="High"
                ))
            elif gap_size >= 1:  # Medium gap
                initiatives.append(Initiative(
                    title=f"{dimension} Enhancement",
                    description=f"Improve {dimension} by {gap_size:.1f} levels",
                    dimension=dimension,
                    owner="TBD",
                    timeline_weeks=8,
                    impact="Medium",
                    effort="Medium"
                ))
            else:  # Small gap
                initiatives.append(Initiative(
                    title=f"{dimension} Fine-tuning",
                    description=f"Refine {dimension} practices",
                    dimension=dimension,
                    owner="TBD",
                    timeline_weeks=4,
                    impact="Low",
                    effort="Low"
                ))

        # Sort by impact/effort ratio (high impact, low effort first)
        impact_scores = {"High": 3, "Medium": 2, "Low": 1}
        effort_scores = {"Low": 1, "Medium": 2, "High": 3}

        initiatives.sort(
            key=lambda i: impact_scores[i.impact] / effort_scores[i.effort],
            reverse=True
        )

        self.initiatives = initiatives[:max_concurrent * 2]  # Keep top initiatives
        logger.info(f"Created {len(self.initiatives)} prioritized initiatives")

        return self.initiatives

    def generate_roadmap(self) -> Dict[str, Any]:
        """Generate visual roadmap with timeline."""
        if not self.initiatives:
            self.create_initiatives()

        roadmap = {
            "total_initiatives": len(self.initiatives),
            "timeline_weeks": max(i.timeline_weeks for i in self.initiatives),
            "initiatives": [
                {
                    "title": i.title,
                    "dimension": i.dimension,
                    "owner": i.owner,
                    "weeks": i.timeline_weeks,
                    "impact": i.impact,
                    "effort": i.effort,
                    "status": i.status
                }
                for i in self.initiatives
            ],
            "quarterly_breakdown": self._create_quarterly_breakdown()
        }

        return roadmap

    def _create_quarterly_breakdown(self) -> Dict[str, List[str]]:
        """Break initiatives into quarters."""
        quarters = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

        for initiative in self.initiatives:
            if initiative.timeline_weeks <= 12:
                quarters["Q1"].append(initiative.title)
            elif initiative.timeline_weeks <= 24:
                quarters["Q2"].append(initiative.title)
            elif initiative.timeline_weeks <= 36:
                quarters["Q3"].append(initiative.title)
            else:
                quarters["Q4"].append(initiative.title)

        return quarters


class PDCACycle:
    """Implements Plan-Do-Check-Act continuous improvement cycle."""

    def __init__(self, cycle_name: str, duration_weeks: int = 12):
        """
        Initialize PDCA cycle.

        Args:
            cycle_name: Name of the cycle (e.g., "2025-Q1")
            duration_weeks: Cycle duration (default: 12 weeks)
        """
        self.cycle_name = cycle_name
        self.duration_weeks = duration_weeks
        self.phase = "Plan"
        self.start_date = datetime.now()
        self.initiatives: List[Initiative] = []
        self.results: Dict[str, Any] = {}
        logger.info(f"Initialized PDCA cycle: {cycle_name} ({duration_weeks} weeks)")

    def plan(self, initiatives: List[Initiative]) -> None:
        """
        Plan phase: Set goals and initiatives.

        Args:
            initiatives: List of initiatives for this cycle
        """
        logger.info(f"PDCA Plan phase: {len(initiatives)} initiatives")
        self.phase = "Plan"
        self.initiatives = initiatives

        # Assign start dates
        for i, initiative in enumerate(self.initiatives):
            initiative.start_date = self.start_date + timedelta(weeks=i * 2)

    def do(self) -> None:
        """Do phase: Execute initiatives."""
        logger.info("PDCA Do phase: Executing initiatives")
        self.phase = "Do"

        for initiative in self.initiatives:
            initiative.status = "In Progress"

    def check(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check phase: Measure results.

        Args:
            metrics_summary: Current metrics from MetricsTracker

        Returns:
            Analysis of results
        """
        logger.info("PDCA Check phase: Measuring results")
        self.phase = "Check"

        self.results = {
            "cycle_name": self.cycle_name,
            "metrics_meeting_target": metrics_summary.get("meeting_target", 0),
            "total_metrics": metrics_summary.get("total_metrics", 0),
            "degrading_metrics": metrics_summary.get("degrading", 0),
            "completed_initiatives": sum(1 for i in self.initiatives if i.status == "Completed"),
            "total_initiatives": len(self.initiatives)
        }

        return self.results

    def act(self) -> List[str]:
        """
        Act phase: Standardize successes and plan next cycle.

        Returns:
            List of actions for next cycle
        """
        logger.info("PDCA Act phase: Planning next cycle")
        self.phase = "Act"

        actions = []

        # Identify successful initiatives
        successful = [i for i in self.initiatives if i.status == "Completed"]
        if successful:
            actions.append(f"Standardize {len(successful)} successful initiatives")

        # Identify abandoned initiatives
        abandoned = [i for i in self.initiatives if i.status == "Abandoned"]
        if abandoned:
            actions.append(f"Document lessons from {len(abandoned)} abandoned initiatives")

        # Recommend next cycle focus
        if self.results.get("degrading_metrics", 0) > 0:
            actions.append("URGENT: Address degrading metrics in next cycle")

        completion_rate = (
            self.results.get("completed_initiatives", 0) /
            max(self.results.get("total_initiatives", 1), 1) * 100
        )

        if completion_rate < 50:
            actions.append("Reduce initiative count in next cycle (overcommitted)")
        elif completion_rate > 80:
            actions.append("Can increase initiative count in next cycle")

        return actions


# Convenience functions

def generate_maturity_report(responses: Dict[str, int]) -> Dict[str, Any]:
    """
    Convenience function to generate maturity report from responses.

    Args:
        responses: Dict mapping question text to selected level (1-5)

    Returns:
        Complete maturity assessment report
    """
    assessment = MaturityAssessment()
    assessment.collect_responses(responses)
    return assessment.generate_report()


def calculate_overall_maturity(responses: Dict[str, int]) -> int:
    """
    Convenience function to calculate overall maturity level.

    Args:
        responses: Dict mapping question text to selected level (1-5)

    Returns:
        Overall maturity level (1-5)
    """
    assessment = MaturityAssessment()
    assessment.collect_responses(responses)
    scores = assessment.calculate_maturity_scores()
    return scores.overall


def create_improvement_plan(
    current_responses: Dict[str, int],
    target_level: int,
    max_initiatives: int = 3
) -> Dict[str, Any]:
    """
    Convenience function to create complete improvement plan.

    Args:
        current_responses: Current assessment responses
        target_level: Target maturity level (1-5)
        max_initiatives: Maximum concurrent initiatives

    Returns:
        Complete improvement plan with roadmap
    """
    # Generate assessment
    assessment = MaturityAssessment()
    assessment.collect_responses(current_responses)
    current_scores = assessment.calculate_maturity_scores()

    # Perform gap analysis
    gap_analysis = GapAnalysis(current_scores, target_level)
    gaps = gap_analysis.identify_gaps()

    # Create roadmap
    roadmap = ImprovementRoadmap(gaps)
    roadmap.create_initiatives(max_concurrent=max_initiatives)
    roadmap_plan = roadmap.generate_roadmap()

    return {
        "current_maturity": current_scores.to_dict(),
        "target_level": target_level,
        "gap_analysis": gaps,
        "improvement_roadmap": roadmap_plan,
        "estimated_timeline": f"{roadmap_plan['timeline_weeks']} weeks"
    }
