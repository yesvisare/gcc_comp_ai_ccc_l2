"""
Tests for L3 M4.1: Model Cards & AI Governance

Comprehensive test suite covering:
- Model card generation (JSON and Markdown)
- Bias detection with demographic parity testing
- Human-in-the-loop workflow and queue management
- Governance review processes and committee voting

SERVICE: LOCAL (No external APIs - all tests run offline)
"""

import pytest
import json
from datetime import datetime

from src.l3_m4_enterprise_integration import (
    RAGModelCard,
    BiasDetector,
    HumanInTheLoopWorkflow,
    GovernanceReviewer
)


# ============================================================================
# RAGModelCard Tests
# ============================================================================

class TestRAGModelCard:
    """Tests for model card generation"""

    def test_initialization(self):
        """Test model card can be initialized with basic info"""
        card = RAGModelCard(
            model_name="GCC_RAG_v1",
            model_version="1.0.0",
            model_owner="AI Engineering Team",
            contact_email="ai-team@gcc.com"
        )

        assert card.model_name == "GCC_RAG_v1"
        assert card.model_version == "1.0.0"
        assert card.model_owner == "AI Engineering Team"
        assert card.contact_email == "ai-team@gcc.com"

    def test_set_components(self):
        """Test setting RAG system components"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")

        card.set_components(
            embedding_model="text-embedding-3-small",
            vector_database="Qdrant",
            generation_model="gpt-4",
            retrieval_method="semantic search",
            reranker="cohere-rerank-v3"
        )

        assert card.components["embedding_model"] == "text-embedding-3-small"
        assert card.components["vector_database"] == "Qdrant"
        assert card.components["generation_model"] == "gpt-4"
        assert card.components["reranker"] == "cohere-rerank-v3"

    def test_set_intended_use(self):
        """Test documenting intended and prohibited uses"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")

        primary_uses = [
            "Employee HR policy questions",
            "Benefits information lookup"
        ]
        prohibited_uses = [
            "Making termination decisions",
            "Setting compensation without review"
        ]

        card.set_intended_use(
            primary_use_cases=primary_uses,
            out_of_scope_uses=prohibited_uses,
            target_users=["HR team", "Employees"],
            use_limitations=["Requires human review for high-stakes decisions"]
        )

        assert len(card.intended_use["primary_use_cases"]) == 2
        assert len(card.intended_use["out_of_scope_uses"]) == 2
        assert "Making termination decisions" in card.intended_use["out_of_scope_uses"]

    def test_add_limitations_and_recommendations(self):
        """Test adding limitations and recommendations"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")

        card.add_limitation("May hallucinate when document coverage is sparse")
        card.add_limitation("Retrieval quality degrades with ambiguous queries")
        card.add_recommendation("Conduct quarterly bias testing")

        assert len(card.limitations) == 2
        assert len(card.recommendations) == 1

    def test_set_governance(self):
        """Test setting governance structure"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")

        card.set_governance(
            review_committee=["Security", "Legal", "Privacy", "Product"],
            review_cadence="Quarterly",
            incident_escalation="Report via JIRA to AI Governance Board",
            approval_authority="VP Engineering and Chief Legal Officer"
        )

        assert card.governance["review_cadence"] == "Quarterly"
        assert len(card.governance["review_committee"]) == 4
        assert "Legal" in card.governance["review_committee"]

    def test_change_log(self):
        """Test version change tracking"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")

        card.add_change_log_entry(
            version="1.0.0",
            changes="Initial release",
            author="AI Team"
        )

        card.add_change_log_entry(
            version="1.1.0",
            changes="Added reranking model",
            author="AI Team"
        )

        assert len(card.change_log) == 2
        assert card.change_log[1]["version"] == "1.1.0"

    def test_to_json_export(self):
        """Test exporting model card as JSON"""
        card = RAGModelCard("test", "1.0", "team", "team@test.com")
        card.set_components(
            embedding_model="test-embed",
            vector_database="test-db",
            generation_model="test-llm",
            retrieval_method="semantic"
        )

        json_output = card.to_json()
        parsed = json.loads(json_output)

        assert parsed["model_details"]["name"] == "test"
        assert parsed["model_details"]["version"] == "1.0"
        assert parsed["components"]["embedding_model"] == "test-embed"
        assert "generated_at" in parsed

    def test_to_markdown_export(self):
        """Test exporting model card as Markdown"""
        card = RAGModelCard("GCC_RAG", "2.0", "AI Team", "ai@gcc.com")
        card.set_components(
            embedding_model="text-embedding-3-small",
            vector_database="Qdrant",
            generation_model="gpt-4",
            retrieval_method="hybrid"
        )
        card.add_limitation("Test limitation")

        markdown = card.to_markdown()

        assert "# Model Card: GCC_RAG v2.0" in markdown
        assert "## 1. Model Details" in markdown
        assert "## 2. Components" in markdown
        assert "Test limitation" in markdown


# ============================================================================
# BiasDetector Tests
# ============================================================================

class TestBiasDetector:
    """Tests for bias detection functionality"""

    def test_initialization(self):
        """Test bias detector initialization with custom threshold"""
        detector = BiasDetector(disparity_threshold=0.15)
        assert detector.disparity_threshold == 0.15
        assert len(detector.test_results) == 0

    def test_no_bias_detected(self):
        """Test when groups have similar scores (no bias)"""
        detector = BiasDetector(disparity_threshold=0.10)

        group_a_scores = [0.85, 0.88, 0.83, 0.87, 0.86]
        group_b_scores = [0.84, 0.86, 0.85, 0.88, 0.85]

        result = detector.test_demographic_parity(
            group_a_scores=group_a_scores,
            group_b_scores=group_b_scores,
            group_a_name="Region A",
            group_b_name="Region B"
        )

        assert result["status"] == "completed"
        assert result["bias_detected"] is False
        assert result["severity"] == "none"

    def test_bias_detected_medium_severity(self):
        """Test when bias exceeds threshold (medium severity)"""
        detector = BiasDetector(disparity_threshold=0.10)

        # Region A gets high quality results
        group_a_scores = [0.90, 0.92, 0.88, 0.91, 0.89]  # avg ~0.90

        # Region B gets significantly lower quality
        group_b_scores = [0.70, 0.68, 0.72, 0.69, 0.71]  # avg ~0.70

        result = detector.test_demographic_parity(
            group_a_scores=group_a_scores,
            group_b_scores=group_b_scores,
            group_a_name="North America",
            group_b_name="Asia Pacific"
        )

        assert result["status"] == "completed"
        assert result["bias_detected"] is True
        assert result["severity"] in ["medium", "low"]  # Depends on exact calculation
        assert result["disparity"]["relative"] > 0.10

    def test_bias_detected_high_severity(self):
        """Test high severity bias (>30% disparity)"""
        detector = BiasDetector(disparity_threshold=0.10)

        group_a_scores = [0.95, 0.96, 0.94, 0.97, 0.95]  # avg ~0.954
        group_b_scores = [0.50, 0.48, 0.52, 0.49, 0.51]  # avg ~0.50

        result = detector.test_demographic_parity(
            group_a_scores=group_a_scores,
            group_b_scores=group_b_scores,
            group_a_name="Engineering Dept",
            group_b_name="Marketing Dept"
        )

        assert result["bias_detected"] is True
        assert result["severity"] == "high"

    def test_empty_score_lists(self):
        """Test handling of empty input lists"""
        detector = BiasDetector()

        result = detector.test_demographic_parity(
            group_a_scores=[],
            group_b_scores=[0.8, 0.9]
        )

        assert result["status"] == "error"
        assert "Insufficient data" in result["message"]

    def test_summary_statistics(self):
        """Test summary of multiple bias tests"""
        detector = BiasDetector(disparity_threshold=0.10)

        # Run 3 tests
        detector.test_demographic_parity([0.85, 0.86], [0.84, 0.85], "A", "B")  # No bias
        detector.test_demographic_parity([0.90, 0.91], [0.70, 0.72], "C", "D")  # Bias
        detector.test_demographic_parity([0.88, 0.89], [0.87, 0.88], "E", "F")  # No bias

        summary = detector.get_summary()

        assert summary["total_tests"] == 3
        assert summary["bias_detected"] == 1
        assert summary["bias_rate"] == pytest.approx(0.333, abs=0.01)


# ============================================================================
# HumanInTheLoopWorkflow Tests
# ============================================================================

class TestHumanInTheLoopWorkflow:
    """Tests for human-in-the-loop workflow"""

    def test_initialization(self):
        """Test workflow initialization with default keywords"""
        workflow = HumanInTheLoopWorkflow()
        assert "legal" in workflow.high_risk_keywords
        assert "termination" in workflow.high_risk_keywords
        assert len(workflow.review_queue) == 0

    def test_custom_risk_keywords(self):
        """Test initialization with custom risk keywords"""
        custom_keywords = ["confidential", "merger", "acquisition"]
        workflow = HumanInTheLoopWorkflow(high_risk_keywords=custom_keywords)

        assert "confidential" in workflow.high_risk_keywords
        assert len(workflow.high_risk_keywords) == 3

    def test_classify_low_risk_query(self):
        """Test classification of low-risk query"""
        workflow = HumanInTheLoopWorkflow()

        classification = workflow.classify_query(
            query="What are the office hours for the reception desk?",
            user_context={"department": "HR"}
        )

        assert classification["risk_level"] == "LOW"
        assert classification["requires_review"] is False
        assert len(classification["triggered_keywords"]) == 0

    def test_classify_high_risk_legal_query(self):
        """Test classification of high-risk legal query"""
        workflow = HumanInTheLoopWorkflow()

        classification = workflow.classify_query(
            query="What are the legal implications of terminating an employee?"
        )

        assert classification["risk_level"] == "HIGH"
        assert classification["requires_review"] is True
        assert "legal" in classification["triggered_keywords"]
        assert "termination" in classification["triggered_keywords"]

    def test_classify_high_risk_investment_query(self):
        """Test classification of financial/investment query"""
        workflow = HumanInTheLoopWorkflow()

        classification = workflow.classify_query(
            query="Should we make this investment in the new startup?"
        )

        assert classification["risk_level"] == "HIGH"
        assert "investment" in classification["triggered_keywords"]

    def test_route_to_review_queue(self):
        """Test routing high-risk query to review queue"""
        workflow = HumanInTheLoopWorkflow()

        classification = workflow.classify_query(
            query="Can we fire someone for this violation?"
        )

        queue_result = workflow.route_to_review(classification)

        assert queue_result["status"] == "queued_for_review"
        assert queue_result["queue_id"] == 1
        assert queue_result["queue_position"] == 1
        assert len(workflow.review_queue) == 1

    def test_process_query_low_risk(self):
        """Test end-to-end processing of low-risk query"""
        workflow = HumanInTheLoopWorkflow()

        result = workflow.process_query(
            query="What is the vacation policy?",
            user_context={"user": "employee123"}
        )

        assert result["status"] == "approved"
        assert "can proceed" in result["message"].lower()

    def test_process_query_high_risk(self):
        """Test end-to-end processing of high-risk query"""
        workflow = HumanInTheLoopWorkflow()

        result = workflow.process_query(
            query="Legal advice on discrimination lawsuit"
        )

        assert result["status"] == "queued_for_review"
        assert "queue_id" in result
        assert len(workflow.review_queue) == 1

    def test_queue_status_tracking(self):
        """Test queue status after multiple queries"""
        workflow = HumanInTheLoopWorkflow()

        # Process mix of queries
        workflow.process_query("Normal question")  # Low risk
        workflow.process_query("Legal termination question")  # High risk
        workflow.process_query("Another investment query")  # High risk

        status = workflow.get_queue_status()

        assert status["total_queued"] == 2  # Only high-risk queued
        assert status["pending_review"] == 2
        assert status["audit_log_size"] == 3  # All queries logged


# ============================================================================
# GovernanceReviewer Tests
# ============================================================================

class TestGovernanceReviewer:
    """Tests for governance review processes"""

    def test_initialization(self):
        """Test governance reviewer initialization"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal", "Privacy"],
            review_cadence="Monthly",
            approval_threshold=0.67
        )

        assert len(reviewer.committee_members) == 3
        assert reviewer.review_cadence == "Monthly"
        assert reviewer.approval_threshold == 0.67

    def test_submit_for_review(self):
        """Test submitting change for governance review"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal"],
            review_cadence="Quarterly"
        )

        result = reviewer.submit_for_review(
            change_type="model_update",
            description="Upgrade to GPT-4 Turbo",
            impact_assessment="Improved accuracy, faster responses",
            submitted_by="AI Engineering"
        )

        assert result["status"] == "submitted"
        assert result["review_id"] == 1
        assert result["committee_size"] == 2

    def test_cast_vote_approve(self):
        """Test committee member approving a change"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal"],
            approval_threshold=0.50
        )

        # Submit review
        reviewer.submit_for_review(
            change_type="data_source_change",
            description="Add new document collection",
            impact_assessment="Broader coverage",
            submitted_by="Data Team"
        )

        # Cast vote
        result = reviewer.cast_vote(
            review_id=1,
            committee_member="Security",
            vote="approve",
            comments="Security assessment passed"
        )

        assert result["status"] == "vote_recorded"
        assert result["votes_cast"] == 1
        assert result["votes_needed"] == 2

    def test_vote_from_invalid_member(self):
        """Test vote from non-committee member is rejected"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal"]
        )

        reviewer.submit_for_review(
            change_type="test",
            description="test",
            impact_assessment="test",
            submitted_by="test"
        )

        result = reviewer.cast_vote(
            review_id=1,
            committee_member="InvalidMember",
            vote="approve"
        )

        assert result["status"] == "error"
        assert "not on the committee" in result["message"]

    def test_review_approval_with_threshold(self):
        """Test review is approved when threshold is met"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal", "Privacy"],
            approval_threshold=0.67  # Need 2 of 3 votes
        )

        # Submit review
        reviewer.submit_for_review(
            change_type="algorithm_change",
            description="Switch to hybrid search",
            impact_assessment="Better retrieval quality",
            submitted_by="AI Team"
        )

        # Get 2 approvals and 1 rejection
        reviewer.cast_vote(1, "Security", "approve")
        reviewer.cast_vote(1, "Legal", "approve")
        reviewer.cast_vote(1, "Privacy", "reject")

        review = reviewer.review_history[0]
        assert review["decision"] == "approved"
        assert review["approval_rate"] >= 0.67

    def test_review_rejection_below_threshold(self):
        """Test review is rejected when approval threshold not met"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal", "Privacy"],
            approval_threshold=0.67  # Need 2 of 3 votes
        )

        # Submit review
        reviewer.submit_for_review(
            change_type="test",
            description="test",
            impact_assessment="test",
            submitted_by="test"
        )

        # Get only 1 approval
        reviewer.cast_vote(1, "Security", "approve")
        reviewer.cast_vote(1, "Legal", "reject")
        reviewer.cast_vote(1, "Privacy", "reject")

        review = reviewer.review_history[0]
        assert review["decision"] == "rejected"

    def test_report_incident_low_severity(self):
        """Test reporting low severity incident"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal"]
        )

        result = reviewer.report_incident(
            incident_type="query_timeout",
            description="System timed out on complex query",
            severity="low",
            reported_by="Operations"
        )

        assert result["status"] == "reported"
        assert result["escalated"] is False
        assert "next meeting" in result["next_steps"].lower()

    def test_report_incident_critical_severity(self):
        """Test reporting critical incident triggers escalation"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal"]
        )

        result = reviewer.report_incident(
            incident_type="bias_detected",
            description="20% quality disparity between regions detected",
            severity="critical",
            reported_by="AI Team"
        )

        assert result["status"] == "reported"
        assert result["escalated"] is True
        assert "immediate escalation" in result["next_steps"].lower()

    def test_governance_summary(self):
        """Test governance summary metrics"""
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal", "Privacy"],
            review_cadence="Quarterly"
        )

        # Submit and complete one review
        reviewer.submit_for_review("test1", "desc1", "impact1", "team1")
        reviewer.cast_vote(1, "Security", "approve")
        reviewer.cast_vote(1, "Legal", "approve")
        reviewer.cast_vote(1, "Privacy", "approve")

        # Submit pending review
        reviewer.submit_for_review("test2", "desc2", "impact2", "team2")

        # Report incidents
        reviewer.report_incident("type1", "desc1", "low", "team1")
        reviewer.report_incident("type2", "desc2", "critical", "team2")

        summary = reviewer.get_governance_summary()

        assert summary["committee"]["size"] == 3
        assert summary["committee"]["review_cadence"] == "Quarterly"
        assert summary["reviews"]["total"] == 2
        assert summary["reviews"]["approved"] == 1
        assert summary["reviews"]["pending"] == 1
        assert summary["incidents"]["total"] == 2
        assert summary["incidents"]["critical"] == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test integration of multiple governance components"""

    def test_complete_governance_workflow(self):
        """Test complete workflow from model card to governance approval"""

        # Step 1: Create model card
        card = RAGModelCard(
            model_name="GCC_Compliance_RAG",
            model_version="1.0.0",
            model_owner="AI Engineering",
            contact_email="ai@gcc.com"
        )

        card.set_components(
            embedding_model="text-embedding-3-small",
            vector_database="Qdrant",
            generation_model="gpt-4",
            retrieval_method="hybrid"
        )

        # Step 2: Run bias testing
        detector = BiasDetector(disparity_threshold=0.10)

        bias_result = detector.test_demographic_parity(
            group_a_scores=[0.85, 0.87, 0.86],
            group_b_scores=[0.84, 0.86, 0.85],
            group_a_name="Team A",
            group_b_name="Team B"
        )

        # Add to model card
        card.set_ethical_considerations(
            fairness_testing=bias_result,
            bias_mitigation=["Regular demographic testing", "Diverse training data"],
            privacy_measures=["PII detection", "Access controls"]
        )

        # Step 3: Configure human review
        workflow = HumanInTheLoopWorkflow()

        query_result = workflow.process_query(
            "Legal implications of policy change"
        )

        # Add to model card
        card.add_recommendation("High-stakes queries routed to human review")

        # Step 4: Submit for governance approval
        reviewer = GovernanceReviewer(
            committee_members=["Security", "Legal", "Privacy"],
            approval_threshold=0.67
        )

        governance_result = reviewer.submit_for_review(
            change_type="new_rag_system",
            description="Deploy GCC Compliance RAG v1.0",
            impact_assessment="500 employees, HR/Legal use cases",
            submitted_by="AI Engineering"
        )

        # Step 5: Committee approval
        reviewer.cast_vote(governance_result["review_id"], "Security", "approve")
        reviewer.cast_vote(governance_result["review_id"], "Legal", "approve")
        reviewer.cast_vote(governance_result["review_id"], "Privacy", "approve")

        # Verify complete workflow
        assert card.model_name == "GCC_Compliance_RAG"
        assert bias_result["bias_detected"] is False
        assert query_result["status"] == "queued_for_review"
        assert reviewer.review_history[0]["decision"] == "approved"

        # Generate final model card
        json_card = card.to_json()
        assert json_card is not None
        assert len(json_card) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
