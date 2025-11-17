"""
Tests for L3 M4.4: Compliance Maturity & Continuous Improvement

Tests all major functions from the maturity assessment framework.
All tests run in offline mode (no external services required).
"""

import pytest
import os
from datetime import datetime
from src.l3_m4_compliance_maturity import (
    MaturityLevel,
    Dimension,
    AssessmentQuestion,
    MaturityAssessment,
    GapAnalysis,
    MetricsTracker,
    ImprovementRoadmap,
    PDCACycle,
    Initiative,
    generate_maturity_report,
    calculate_overall_maturity,
    create_improvement_plan
)

# Force offline mode for tests
os.environ["PROMETHEUS_ENABLED"] = "false"
os.environ["GRAFANA_ENABLED"] = "false"


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_responses_level_2():
    """Sample assessment responses indicating Level 2 maturity."""
    return {
        # People dimension (Level 2)
        "How mature is your compliance training program?": 2,
        "How is compliance expertise distributed?": 2,
        "How do you onboard new engineers on compliance?": 2,
        "How are compliance responsibilities defined?": 2,
        "What's the consequence of compliance violations?": 2,
        # Process dimension (Level 2)
        "How documented are your compliance processes?": 2,
        "How do you handle compliance exceptions?": 2,
        "How integrated is compliance in your SDLC?": 2,
        "How do you manage compliance SLAs?": 2,
        "How often do you update compliance processes?": 2,
        # Technology dimension (Level 2)
        "How automated is your PII detection?": 2,
        "How is access control implemented?": 2,
        "How complete are your audit trails?": 2,
        "How do you test compliance controls?": 2,
        "How do you manage encryption keys?": 2,
        # Metrics dimension (Level 2)
        "What compliance metrics do you track?": 2,
        "How visible are compliance metrics?": 2,
        "How do you respond to metric degradation?": 2,
        "What's your PII detection accuracy target?": 2,
        "How do you track training effectiveness?": 2,
        # Culture dimension (Level 2)
        "How does leadership view compliance?": 2,
        "How do teams react to compliance requirements?": 2,
        "How are compliance failures handled?": 2,
        "How is compliance innovation rewarded?": 2,
        "How transparent is compliance information?": 2
    }


@pytest.fixture
def sample_responses_mixed():
    """Sample responses with mixed maturity levels (limiting dimension test)."""
    return {
        # People: Level 4 (high)
        "How mature is your compliance training program?": 4,
        "How is compliance expertise distributed?": 4,
        "How do you onboard new engineers on compliance?": 4,
        "How are compliance responsibilities defined?": 4,
        "What's the consequence of compliance violations?": 4,
        # Process: Level 3
        "How documented are your compliance processes?": 3,
        "How do you handle compliance exceptions?": 3,
        "How integrated is compliance in your SDLC?": 3,
        "How do you manage compliance SLAs?": 3,
        "How often do you update compliance processes?": 3,
        # Technology: Level 2 (LIMITING - weakest link)
        "How automated is your PII detection?": 2,
        "How is access control implemented?": 2,
        "How complete are your audit trails?": 2,
        "How do you test compliance controls?": 2,
        "How do you manage encryption keys?": 2,
        # Metrics: Level 3
        "What compliance metrics do you track?": 3,
        "How visible are compliance metrics?": 3,
        "How do you respond to metric degradation?": 3,
        "What's your PII detection accuracy target?": 3,
        "How do you track training effectiveness?": 3,
        # Culture: Level 3
        "How does leadership view compliance?": 3,
        "How do teams react to compliance requirements?": 3,
        "How are compliance failures handled?": 3,
        "How is compliance innovation rewarded?": 3,
        "How transparent is compliance information?": 3
    }


# ============================================
# MATURITY LEVEL TESTS
# ============================================

def test_maturity_level_enum():
    """Test MaturityLevel enum values and descriptions."""
    assert MaturityLevel.LEVEL1_AD_HOC.value == 1
    assert MaturityLevel.LEVEL5_OPTIMIZING.value == 5

    assert "Ad-hoc" in MaturityLevel.LEVEL1_AD_HOC.description
    assert "Optimizing" in MaturityLevel.LEVEL5_OPTIMIZING.description


def test_dimension_all_dimensions():
    """Test Dimension class returns all 5 dimensions."""
    dimensions = Dimension.all_dimensions()

    assert len(dimensions) == 5
    assert "People" in dimensions
    assert "Process" in dimensions
    assert "Technology" in dimensions
    assert "Metrics" in dimensions
    assert "Culture" in dimensions


# ============================================
# ASSESSMENT QUESTION TESTS
# ============================================

def test_assessment_question_creation():
    """Test creating an assessment question."""
    question = AssessmentQuestion(
        dimension="People",
        question="Test question?",
        level_indicators={1: "Level 1", 2: "Level 2", 3: "Level 3", 4: "Level 4", 5: "Level 5"}
    )

    assert question.dimension == "People"
    assert question.question == "Test question?"
    assert question.weight == 1.0


def test_assessment_question_score_response_valid():
    """Test scoring valid response."""
    question = AssessmentQuestion(
        dimension="People",
        question="Test?",
        level_indicators={1: "L1", 2: "L2", 3: "L3", 4: "L4", 5: "L5"}
    )

    assert question.score_response(3) == 3
    assert question.score_response(1) == 1
    assert question.score_response(5) == 5


def test_assessment_question_score_response_invalid():
    """Test scoring invalid response raises error."""
    question = AssessmentQuestion(
        dimension="People",
        question="Test?",
        level_indicators={1: "L1", 2: "L2", 3: "L3", 4: "L4", 5: "L5"}
    )

    with pytest.raises(ValueError):
        question.score_response(0)

    with pytest.raises(ValueError):
        question.score_response(6)


# ============================================
# MATURITY ASSESSMENT TESTS
# ============================================

def test_maturity_assessment_initialization():
    """Test MaturityAssessment initialization."""
    assessment = MaturityAssessment()

    assert len(assessment.questions) == 25  # 5 questions per dimension × 5 dimensions
    assert len(assessment.responses) == 0


def test_maturity_assessment_questionnaire_structure():
    """Test questionnaire has correct structure (5 questions per dimension)."""
    assessment = MaturityAssessment()

    dimension_counts = {}
    for question in assessment.questions:
        dim = question.dimension
        dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

    for dim in Dimension.all_dimensions():
        assert dimension_counts[dim] == 5


def test_maturity_assessment_collect_responses(sample_responses_level_2):
    """Test collecting assessment responses."""
    assessment = MaturityAssessment()
    assessment.collect_responses(sample_responses_level_2)

    assert len(assessment.responses) == 25


def test_maturity_assessment_calculate_scores_uniform(sample_responses_level_2):
    """Test calculating scores with uniform responses (all Level 2)."""
    assessment = MaturityAssessment()
    assessment.collect_responses(sample_responses_level_2)

    scores = assessment.calculate_maturity_scores()

    # All dimensions should be Level 2
    assert scores.people == 2.0
    assert scores.process == 2.0
    assert scores.technology == 2.0
    assert scores.metrics == 2.0
    assert scores.culture == 2.0
    assert scores.overall == 2


def test_maturity_assessment_weakest_link_rule(sample_responses_mixed):
    """Test weakest link rule (overall = lowest dimension)."""
    assessment = MaturityAssessment()
    assessment.collect_responses(sample_responses_mixed)

    scores = assessment.calculate_maturity_scores()

    # Technology is Level 2 (weakest), so overall should be 2
    assert scores.technology == 2.0
    assert scores.people == 4.0
    assert scores.overall == 2  # Weakest link!


def test_maturity_assessment_generate_report(sample_responses_level_2):
    """Test generating maturity report."""
    assessment = MaturityAssessment()
    assessment.collect_responses(sample_responses_level_2)

    report = assessment.generate_report()

    assert "assessment_date" in report
    assert report["responses_collected"] == 25
    assert "scores" in report
    assert "limiting_dimension" in report
    assert "recommendations" in report
    assert report["next_target_level"] == 3  # Level 2 → target Level 3
    assert len(report["recommendations"]) > 0


def test_convenience_function_generate_maturity_report(sample_responses_level_2):
    """Test convenience function for generating reports."""
    report = generate_maturity_report(sample_responses_level_2)

    assert report["responses_collected"] == 25
    assert report["scores"]["overall"] == 2


def test_convenience_function_calculate_overall_maturity(sample_responses_mixed):
    """Test convenience function for calculating overall maturity."""
    overall = calculate_overall_maturity(sample_responses_mixed)

    assert overall == 2  # Technology is limiting dimension at Level 2


# ============================================
# GAP ANALYSIS TESTS
# ============================================

def test_gap_analysis_initialization():
    """Test GapAnalysis initialization."""
    from src.l3_m4_compliance_maturity import MaturityScore

    current = MaturityScore(
        people=2.0,
        process=2.0,
        technology=2.0,
        metrics=2.0,
        culture=2.0,
        overall=2
    )

    gap_analysis = GapAnalysis(current, target_level=4)

    assert gap_analysis.current.overall == 2
    assert gap_analysis.target == 4


def test_gap_analysis_identify_gaps():
    """Test identifying gaps between current and target."""
    from src.l3_m4_compliance_maturity import MaturityScore

    current = MaturityScore(
        people=2.0,
        process=3.0,
        technology=1.0,  # Largest gap
        metrics=2.5,
        culture=2.0,
        overall=1
    )

    gap_analysis = GapAnalysis(current, target_level=4)
    gaps = gap_analysis.identify_gaps()

    assert gaps["gaps_identified"] > 0
    assert "Technology" in gaps["dimension_gaps"]  # Should identify tech gap
    assert gaps["dimension_gaps"]["Technology"]["gap"] == 3.0  # 4 - 1 = 3
    assert gaps["dimension_gaps"]["Technology"]["priority"] == "High"  # Gap >= 2


def test_gap_analysis_recommended_sequence():
    """Test recommended sequence prioritizes Culture and People first."""
    from src.l3_m4_compliance_maturity import MaturityScore

    current = MaturityScore(
        people=2.0,
        process=2.0,
        technology=2.0,
        metrics=2.0,
        culture=1.0,  # Lowest
        overall=1
    )

    gap_analysis = GapAnalysis(current, target_level=4)
    gaps = gap_analysis.identify_gaps()

    sequence = gaps["recommended_sequence"]

    # Culture should come first (foundation)
    assert "Culture" in sequence[0]


# ============================================
# METRICS TRACKER TESTS
# ============================================

def test_metrics_tracker_initialization():
    """Test MetricsTracker initialization."""
    tracker = MetricsTracker()

    assert len(tracker.metrics) == 6  # 6 standard metrics
    assert "pii_detection_accuracy" in tracker.metrics
    assert "audit_trail_completeness" in tracker.metrics


def test_metrics_tracker_update_metric():
    """Test updating a metric."""
    tracker = MetricsTracker()

    tracker.update_metric("pii_detection_accuracy", 95.0)

    metric = tracker.metrics["pii_detection_accuracy"]
    assert metric.current_value == 95.0
    assert len(metric.historical_values) == 1


def test_metrics_tracker_trend_detection():
    """Test trend direction detection."""
    tracker = MetricsTracker()

    # Create improving trend
    tracker.update_metric("pii_detection_accuracy", 90.0)
    tracker.update_metric("pii_detection_accuracy", 95.0)
    tracker.update_metric("pii_detection_accuracy", 97.0)

    metric = tracker.metrics["pii_detection_accuracy"]
    assert metric.trend_direction == "improving"


def test_metrics_tracker_detect_regressions():
    """Test detecting metric regressions."""
    tracker = MetricsTracker()

    # Create degrading trend
    tracker.update_metric("pii_detection_accuracy", 99.0)
    tracker.update_metric("pii_detection_accuracy", 97.0)
    tracker.update_metric("pii_detection_accuracy", 95.0)

    regressions = tracker.detect_regressions()

    assert len(regressions) > 0
    assert "PII Detection Accuracy" in regressions[0]


def test_metrics_tracker_get_summary():
    """Test getting metrics summary."""
    tracker = MetricsTracker()

    tracker.update_metric("pii_detection_accuracy", 99.5)

    summary = tracker.get_metrics_summary()

    assert summary["total_metrics"] == 6
    assert "pii_detection_accuracy" in summary["metrics"]
    assert summary["metrics"]["pii_detection_accuracy"]["current"] == 99.5


def test_metric_is_meeting_target():
    """Test metric target checking."""
    tracker = MetricsTracker()

    # PII accuracy: higher is better, target 99%
    tracker.update_metric("pii_detection_accuracy", 99.5)
    metric = tracker.metrics["pii_detection_accuracy"]
    assert metric.is_meeting_target is True

    # Below target
    tracker.update_metric("pii_detection_accuracy", 98.0)
    metric = tracker.metrics["pii_detection_accuracy"]
    assert metric.is_meeting_target is False


# ============================================
# IMPROVEMENT ROADMAP TESTS
# ============================================

def test_improvement_roadmap_initialization():
    """Test ImprovementRoadmap initialization."""
    gap_analysis_result = {
        "dimension_gaps": {
            "Technology": {"gap": 2.5, "priority": "High"}
        }
    }

    roadmap = ImprovementRoadmap(gap_analysis_result)

    assert roadmap.gaps == gap_analysis_result
    assert len(roadmap.initiatives) == 0


def test_improvement_roadmap_create_initiatives():
    """Test creating initiatives from gaps."""
    gap_analysis_result = {
        "dimension_gaps": {
            "Technology": {"gap": 2.5, "priority": "High"},
            "People": {"gap": 1.2, "priority": "Medium"},
            "Culture": {"gap": 0.5, "priority": "Low"}
        }
    }

    roadmap = ImprovementRoadmap(gap_analysis_result)
    initiatives = roadmap.create_initiatives(max_concurrent=3)

    assert len(initiatives) > 0
    # Major gaps (>= 2) should create high-impact initiatives
    major_initiatives = [i for i in initiatives if i.impact == "High"]
    assert len(major_initiatives) > 0


def test_improvement_roadmap_generate_roadmap():
    """Test generating visual roadmap."""
    gap_analysis_result = {
        "dimension_gaps": {
            "Technology": {"gap": 2.0, "priority": "High"}
        }
    }

    roadmap = ImprovementRoadmap(gap_analysis_result)
    roadmap_plan = roadmap.generate_roadmap()

    assert "total_initiatives" in roadmap_plan
    assert "timeline_weeks" in roadmap_plan
    assert "initiatives" in roadmap_plan
    assert "quarterly_breakdown" in roadmap_plan


# ============================================
# PDCA CYCLE TESTS
# ============================================

def test_pdca_cycle_initialization():
    """Test PDCACycle initialization."""
    cycle = PDCACycle("2025-Q1", duration_weeks=12)

    assert cycle.cycle_name == "2025-Q1"
    assert cycle.duration_weeks == 12
    assert cycle.phase == "Plan"


def test_pdca_cycle_plan_phase():
    """Test PDCA Plan phase."""
    cycle = PDCACycle("2025-Q1")

    initiatives = [
        Initiative(
            title="Improve PII Detection",
            description="Upgrade to NER-based detection",
            dimension="Technology",
            owner="Security Team",
            timeline_weeks=8,
            impact="High",
            effort="Medium"
        )
    ]

    cycle.plan(initiatives)

    assert len(cycle.initiatives) == 1
    assert cycle.phase == "Plan"
    assert cycle.initiatives[0].start_date is not None


def test_pdca_cycle_do_phase():
    """Test PDCA Do phase."""
    cycle = PDCACycle("2025-Q1")

    initiatives = [
        Initiative(
            title="Test Initiative",
            description="Test",
            dimension="Technology",
            owner="Team",
            timeline_weeks=4,
            impact="Medium",
            effort="Low"
        )
    ]

    cycle.plan(initiatives)
    cycle.do()

    assert cycle.phase == "Do"
    assert cycle.initiatives[0].status == "In Progress"


def test_pdca_cycle_check_phase():
    """Test PDCA Check phase."""
    cycle = PDCACycle("2025-Q1")

    initiatives = [
        Initiative(
            title="Test Initiative",
            description="Test",
            dimension="Technology",
            owner="Team",
            timeline_weeks=4,
            impact="Medium",
            effort="Low",
            status="Completed"
        )
    ]

    cycle.plan(initiatives)

    metrics_summary = {
        "total_metrics": 6,
        "meeting_target": 5,
        "degrading": 0
    }

    results = cycle.check(metrics_summary)

    assert cycle.phase == "Check"
    assert "cycle_name" in results
    assert results["completed_initiatives"] == 1


def test_pdca_cycle_act_phase():
    """Test PDCA Act phase."""
    cycle = PDCACycle("2025-Q1")

    initiatives = [
        Initiative(
            title="Test Initiative",
            description="Test",
            dimension="Technology",
            owner="Team",
            timeline_weeks=4,
            impact="Medium",
            effort="Low",
            status="Completed"
        )
    ]

    cycle.plan(initiatives)
    cycle.results = {
        "completed_initiatives": 1,
        "total_initiatives": 1,
        "degrading_metrics": 0
    }

    actions = cycle.act()

    assert cycle.phase == "Act"
    assert len(actions) > 0


# ============================================
# CONVENIENCE FUNCTION TESTS
# ============================================

def test_create_improvement_plan_convenience_function(sample_responses_level_2):
    """Test create_improvement_plan convenience function."""
    plan = create_improvement_plan(
        current_responses=sample_responses_level_2,
        target_level=4,
        max_initiatives=3
    )

    assert "current_maturity" in plan
    assert "target_level" in plan
    assert plan["target_level"] == 4
    assert "gap_analysis" in plan
    assert "improvement_roadmap" in plan
    assert "estimated_timeline" in plan


# ============================================
# EDGE CASES & ERROR HANDLING
# ============================================

def test_assessment_with_partial_responses():
    """Test assessment with incomplete responses."""
    assessment = MaturityAssessment()

    # Only answer People dimension questions
    partial_responses = {
        "How mature is your compliance training program?": 3,
        "How is compliance expertise distributed?": 3
    }

    assessment.collect_responses(partial_responses)
    scores = assessment.calculate_maturity_scores()

    # Should only calculate People dimension
    assert scores.people == 3.0
    # Other dimensions should be 0.0
    assert scores.process == 0.0


def test_gap_analysis_no_gaps():
    """Test gap analysis when already at target level."""
    from src.l3_m4_compliance_maturity import MaturityScore

    current = MaturityScore(
        people=4.0,
        process=4.0,
        technology=4.0,
        metrics=4.0,
        culture=4.0,
        overall=4
    )

    gap_analysis = GapAnalysis(current, target_level=4)
    gaps = gap_analysis.identify_gaps()

    assert gaps["gaps_identified"] == 0


def test_metrics_tracker_unknown_metric():
    """Test updating unknown metric (should warn and skip)."""
    tracker = MetricsTracker()

    # Should not raise error, just warn
    tracker.update_metric("unknown_metric", 100.0)

    assert "unknown_metric" not in tracker.metrics


# ============================================
# INTEGRATION TESTS
# ============================================

def test_full_maturity_improvement_workflow(sample_responses_level_2):
    """Test complete workflow: assessment → gap analysis → roadmap → PDCA."""

    # Step 1: Assessment
    assessment = MaturityAssessment()
    assessment.collect_responses(sample_responses_level_2)
    current_scores = assessment.calculate_maturity_scores()

    assert current_scores.overall == 2

    # Step 2: Gap Analysis
    gap_analysis = GapAnalysis(current_scores, target_level=4)
    gaps = gap_analysis.identify_gaps()

    assert gaps["gaps_identified"] > 0

    # Step 3: Improvement Roadmap
    roadmap = ImprovementRoadmap(gaps)
    roadmap.create_initiatives(max_concurrent=3)
    roadmap_plan = roadmap.generate_roadmap()

    assert len(roadmap_plan["initiatives"]) > 0

    # Step 4: PDCA Cycle
    cycle = PDCACycle("2025-Q1")
    cycle.plan(roadmap.initiatives)

    assert cycle.phase == "Plan"
    assert len(cycle.initiatives) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
