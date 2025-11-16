"""
L3 M4.1: Model Cards & AI Governance

This module implements comprehensive AI governance for RAG systems, including:
- Model card documentation (10-section standard)
- Statistical bias detection across demographic groups
- Human-in-the-loop workflows for high-stakes queries
- Governance committee review processes

Aligned with NIST AI RMF and EU AI Act requirements.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

logger = logging.getLogger(__name__)

__all__ = [
    "RAGModelCard",
    "BiasDetector",
    "HumanInTheLoopWorkflow",
    "GovernanceReviewer"
]


class RAGModelCard:
    """
    Generates standardized model card documentation for RAG systems.

    Implements 10-section model card standard covering model details,
    components, intended use, training data, performance metrics,
    ethical considerations, limitations, recommendations, governance,
    and change log.
    """

    def __init__(
        self,
        model_name: str,
        model_version: str,
        model_owner: str,
        contact_email: str
    ):
        """
        Initialize model card with basic identity information.

        Args:
            model_name: Unique identifier for the RAG system
            model_version: Semantic version (e.g., "1.2.3")
            model_owner: Team or individual responsible
            contact_email: Primary contact for questions
        """
        self.model_name = model_name
        self.model_version = model_version
        self.model_owner = model_owner
        self.contact_email = contact_email

        # Initialize all 10 sections
        self.components = {}
        self.intended_use = {}
        self.training_data = {}
        self.performance = {}
        self.ethical_considerations = {}
        self.limitations = []
        self.recommendations = []
        self.governance = {}
        self.change_log = []

        logger.info(f"Initialized model card for {model_name} v{model_version}")

    def set_components(
        self,
        embedding_model: str,
        vector_database: str,
        generation_model: str,
        retrieval_method: str,
        reranker: Optional[str] = None
    ):
        """
        Document RAG system components.

        Args:
            embedding_model: Model used for document/query embeddings
            vector_database: Vector store technology (e.g., "Pinecone", "Qdrant")
            generation_model: LLM for answer generation
            retrieval_method: Retrieval strategy (e.g., "semantic search", "hybrid")
            reranker: Optional reranking model
        """
        self.components = {
            "embedding_model": embedding_model,
            "vector_database": vector_database,
            "generation_model": generation_model,
            "retrieval_method": retrieval_method,
            "reranker": reranker
        }
        logger.info("Components documented")

    def set_intended_use(
        self,
        primary_use_cases: List[str],
        out_of_scope_uses: List[str],
        target_users: List[str],
        use_limitations: List[str]
    ):
        """
        Define approved and prohibited use cases.

        Critical for liability protection - explicitly documenting
        out-of-scope uses defends against misuse claims.

        Args:
            primary_use_cases: Approved applications
            out_of_scope_uses: Explicitly prohibited uses
            target_users: Intended user groups
            use_limitations: Known constraints
        """
        self.intended_use = {
            "primary_use_cases": primary_use_cases,
            "out_of_scope_uses": out_of_scope_uses,
            "target_users": target_users,
            "use_limitations": use_limitations
        }
        logger.info(f"Intended use defined: {len(primary_use_cases)} approved uses, "
                   f"{len(out_of_scope_uses)} prohibited uses")

    def set_training_data(
        self,
        data_sources: List[str],
        data_size: str,
        preprocessing_steps: List[str],
        data_limitations: List[str]
    ):
        """
        Document training data sources and preprocessing.

        Args:
            data_sources: Origins of training documents
            data_size: Volume description (e.g., "10K documents, 500MB")
            preprocessing_steps: Cleaning/chunking methods
            data_limitations: Known gaps or biases in data
        """
        self.training_data = {
            "data_sources": data_sources,
            "data_size": data_size,
            "preprocessing_steps": preprocessing_steps,
            "data_limitations": data_limitations
        }
        logger.info(f"Training data documented: {data_size}")

    def set_performance(
        self,
        metrics: Dict[str, float],
        test_methodology: str,
        performance_limitations: List[str]
    ):
        """
        Record performance metrics and testing approach.

        Args:
            metrics: Quantitative results (e.g., {"precision@5": 0.85})
            test_methodology: How metrics were measured
            performance_limitations: Known weaknesses
        """
        self.performance = {
            "metrics": metrics,
            "test_methodology": test_methodology,
            "performance_limitations": performance_limitations,
            "measured_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Performance metrics recorded: {list(metrics.keys())}")

    def set_ethical_considerations(
        self,
        fairness_testing: Dict[str, Any],
        bias_mitigation: List[str],
        privacy_measures: List[str]
    ):
        """
        Document fairness testing and bias mitigation.

        Args:
            fairness_testing: Results from demographic parity testing
            bias_mitigation: Steps taken to reduce bias
            privacy_measures: Data protection mechanisms
        """
        self.ethical_considerations = {
            "fairness_testing": fairness_testing,
            "bias_mitigation": bias_mitigation,
            "privacy_measures": privacy_measures
        }
        logger.info("Ethical considerations documented")

    def add_limitation(self, limitation: str):
        """Add a known limitation to the model card."""
        self.limitations.append(limitation)
        logger.debug(f"Limitation added: {limitation[:50]}")

    def add_recommendation(self, recommendation: str):
        """Add a usage recommendation."""
        self.recommendations.append(recommendation)
        logger.debug(f"Recommendation added: {recommendation[:50]}")

    def set_governance(
        self,
        review_committee: List[str],
        review_cadence: str,
        incident_escalation: str,
        approval_authority: str
    ):
        """
        Define governance structure and oversight.

        Args:
            review_committee: Stakeholder roles (e.g., ["Security", "Legal", "Privacy"])
            review_cadence: Review frequency (e.g., "Quarterly")
            incident_escalation: Process for handling issues
            approval_authority: Who can approve changes
        """
        self.governance = {
            "review_committee": review_committee,
            "review_cadence": review_cadence,
            "incident_escalation": incident_escalation,
            "approval_authority": approval_authority
        }
        logger.info(f"Governance defined: {review_cadence} reviews by {len(review_committee)} stakeholders")

    def add_change_log_entry(self, version: str, changes: str, author: str):
        """
        Record a version change.

        Args:
            version: New version number
            changes: Description of what changed
            author: Who made the change
        """
        entry = {
            "version": version,
            "changes": changes,
            "author": author,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.change_log.append(entry)
        logger.info(f"Change log updated: v{version}")

    def to_json(self) -> str:
        """
        Export model card as JSON.

        Returns:
            JSON string representation
        """
        card = {
            "model_details": {
                "name": self.model_name,
                "version": self.model_version,
                "owner": self.model_owner,
                "contact": self.contact_email
            },
            "components": self.components,
            "intended_use": self.intended_use,
            "training_data": self.training_data,
            "performance": self.performance,
            "ethical_considerations": self.ethical_considerations,
            "limitations": self.limitations,
            "recommendations": self.recommendations,
            "governance": self.governance,
            "change_log": self.change_log,
            "generated_at": datetime.utcnow().isoformat()
        }
        logger.info("Model card exported to JSON")
        return json.dumps(card, indent=2)

    def to_markdown(self) -> str:
        """
        Export model card as Markdown.

        Returns:
            Markdown formatted documentation
        """
        md = f"""# Model Card: {self.model_name} v{self.model_version}

## 1. Model Details
- **Name:** {self.model_name}
- **Version:** {self.model_version}
- **Owner:** {self.model_owner}
- **Contact:** {self.contact_email}

## 2. Components
"""
        for key, value in self.components.items():
            md += f"- **{key.replace('_', ' ').title()}:** {value}\n"

        md += "\n## 3. Intended Use\n"
        if self.intended_use:
            md += "\n### Primary Use Cases\n"
            for use in self.intended_use.get("primary_use_cases", []):
                md += f"- {use}\n"
            md += "\n### Out of Scope Uses\n"
            for use in self.intended_use.get("out_of_scope_uses", []):
                md += f"- ❌ {use}\n"

        md += "\n## 4. Training Data\n"
        if self.training_data:
            md += f"- **Size:** {self.training_data.get('data_size', 'Not specified')}\n"
            md += f"- **Sources:** {', '.join(self.training_data.get('data_sources', []))}\n"

        md += "\n## 5. Performance\n"
        if self.performance:
            for metric, value in self.performance.get("metrics", {}).items():
                md += f"- **{metric}:** {value}\n"

        md += "\n## 6. Ethical Considerations\n"
        if self.ethical_considerations:
            md += "- Fairness testing conducted\n"
            md += f"- Bias mitigation: {len(self.ethical_considerations.get('bias_mitigation', []))} measures\n"

        md += f"\n## 7. Limitations\n"
        for limitation in self.limitations:
            md += f"- {limitation}\n"

        md += f"\n## 8. Recommendations\n"
        for rec in self.recommendations:
            md += f"- {rec}\n"

        md += "\n## 9. Governance\n"
        if self.governance:
            md += f"- **Review Cadence:** {self.governance.get('review_cadence', 'Not specified')}\n"
            md += f"- **Committee:** {', '.join(self.governance.get('review_committee', []))}\n"

        md += "\n## 10. Change Log\n"
        for entry in self.change_log:
            md += f"\n### v{entry['version']} ({entry['timestamp'][:10]})\n"
            md += f"- {entry['changes']}\n"
            md += f"- *Author: {entry['author']}*\n"

        logger.info("Model card exported to Markdown")
        return md


class BiasDetector:
    """
    Detects statistical bias in RAG system outputs across demographic groups.

    Tests demographic parity and equalized odds to identify
    unfair treatment of different user populations.
    """

    def __init__(self, disparity_threshold: float = 0.10):
        """
        Initialize bias detector.

        Args:
            disparity_threshold: Maximum acceptable quality difference
                                between groups (default 10%)
        """
        self.disparity_threshold = disparity_threshold
        self.test_results = []
        logger.info(f"BiasDetector initialized with {disparity_threshold*100}% threshold")

    def test_demographic_parity(
        self,
        group_a_scores: List[float],
        group_b_scores: List[float],
        group_a_name: str = "Group A",
        group_b_name: str = "Group B"
    ) -> Dict[str, Any]:
        """
        Test if two demographic groups receive similar quality results.

        Args:
            group_a_scores: Quality scores for first group
            group_b_scores: Quality scores for second group
            group_a_name: Label for first group
            group_b_name: Label for second group

        Returns:
            Dict containing test results and bias flag
        """
        if not group_a_scores or not group_b_scores:
            logger.warning("Empty score lists provided")
            return {
                "status": "error",
                "message": "Insufficient data for testing"
            }

        avg_a = sum(group_a_scores) / len(group_a_scores)
        avg_b = sum(group_b_scores) / len(group_b_scores)

        disparity = abs(avg_a - avg_b)
        relative_disparity = disparity / max(avg_a, avg_b) if max(avg_a, avg_b) > 0 else 0

        bias_detected = relative_disparity > self.disparity_threshold

        result = {
            "status": "completed",
            "group_a": {
                "name": group_a_name,
                "avg_score": round(avg_a, 3),
                "sample_size": len(group_a_scores)
            },
            "group_b": {
                "name": group_b_name,
                "avg_score": round(avg_b, 3),
                "sample_size": len(group_b_scores)
            },
            "disparity": {
                "absolute": round(disparity, 3),
                "relative": round(relative_disparity, 3),
                "threshold": self.disparity_threshold
            },
            "bias_detected": bias_detected,
            "severity": self._classify_severity(relative_disparity)
        }

        self.test_results.append(result)

        if bias_detected:
            logger.warning(
                f"⚠️ Bias detected: {group_a_name} vs {group_b_name} - "
                f"{relative_disparity*100:.1f}% disparity (threshold: {self.disparity_threshold*100}%)"
            )
        else:
            logger.info(
                f"✓ No bias detected: {group_a_name} vs {group_b_name} - "
                f"{relative_disparity*100:.1f}% disparity"
            )

        return result

    def _classify_severity(self, disparity: float) -> str:
        """Classify bias severity level."""
        if disparity < self.disparity_threshold:
            return "none"
        elif disparity < 0.20:
            return "low"
        elif disparity < 0.30:
            return "medium"
        else:
            return "high"

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all bias tests conducted.

        Returns:
            Summary statistics across all tests
        """
        if not self.test_results:
            return {"message": "No tests conducted yet"}

        total_tests = len(self.test_results)
        bias_detected_count = sum(1 for r in self.test_results if r.get("bias_detected"))

        return {
            "total_tests": total_tests,
            "bias_detected": bias_detected_count,
            "bias_rate": round(bias_detected_count / total_tests, 3),
            "threshold": self.disparity_threshold,
            "severities": {
                "high": sum(1 for r in self.test_results if r.get("severity") == "high"),
                "medium": sum(1 for r in self.test_results if r.get("severity") == "medium"),
                "low": sum(1 for r in self.test_results if r.get("severity") == "low"),
                "none": sum(1 for r in self.test_results if r.get("severity") == "none")
            }
        }


class HumanInTheLoopWorkflow:
    """
    Routes high-stakes queries to human reviewers before answering.

    Implements risk classification and review queue management
    for queries requiring human oversight (legal, HR, financial decisions).
    """

    def __init__(self, high_risk_keywords: Optional[List[str]] = None):
        """
        Initialize workflow engine.

        Args:
            high_risk_keywords: Terms that trigger human review
        """
        self.high_risk_keywords = high_risk_keywords or [
            "legal",
            "lawsuit",
            "termination",
            "fire",
            "hire",
            "promotion",
            "discrimination",
            "investment",
            "financial advice",
            "medical",
            "compliance violation"
        ]
        self.review_queue = []
        self.audit_log = []
        logger.info(f"HumanInTheLoopWorkflow initialized with {len(self.high_risk_keywords)} risk keywords")

    def classify_query(self, query: str, user_context: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Classify query risk level.

        Args:
            query: User's question
            user_context: Optional metadata (user role, department, etc.)

        Returns:
            Classification with risk level and reasoning
        """
        query_lower = query.lower()

        # Check for high-risk keywords
        triggered_keywords = [
            keyword for keyword in self.high_risk_keywords
            if keyword.lower() in query_lower
        ]

        if triggered_keywords:
            risk_level = "HIGH"
            reason = f"Contains high-risk keywords: {', '.join(triggered_keywords)}"
            requires_review = True
        else:
            risk_level = "LOW"
            reason = "No high-risk indicators detected"
            requires_review = False

        classification = {
            "query": query,
            "risk_level": risk_level,
            "requires_review": requires_review,
            "reason": reason,
            "triggered_keywords": triggered_keywords,
            "user_context": user_context or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        if requires_review:
            logger.warning(f"⚠️ HIGH-RISK query detected: {reason}")
        else:
            logger.info(f"✓ LOW-RISK query: proceeding without review")

        self.audit_log.append(classification)

        return classification

    def route_to_review(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add query to human review queue.

        Args:
            classification: Output from classify_query()

        Returns:
            Queue confirmation with position
        """
        review_item = {
            "id": len(self.review_queue) + 1,
            "classification": classification,
            "status": "pending_review",
            "queued_at": datetime.utcnow().isoformat(),
            "reviewed_at": None,
            "reviewer": None,
            "decision": None
        }

        self.review_queue.append(review_item)

        logger.info(
            f"Query #{review_item['id']} added to review queue "
            f"(position: {len(self.review_queue)})"
        )

        return {
            "status": "queued_for_review",
            "queue_id": review_item["id"],
            "queue_position": len(self.review_queue),
            "estimated_wait": f"{len(self.review_queue) * 5} minutes"  # Rough estimate
        }

    def process_query(self, query: str, user_context: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Complete workflow: classify and route if needed.

        Args:
            query: User's question
            user_context: Optional metadata

        Returns:
            Either direct answer approval or review queue confirmation
        """
        classification = self.classify_query(query, user_context)

        if classification["requires_review"]:
            return self.route_to_review(classification)
        else:
            return {
                "status": "approved",
                "message": "Query can proceed without human review",
                "classification": classification
            }

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current review queue status.

        Returns:
            Queue statistics
        """
        pending = sum(1 for item in self.review_queue if item["status"] == "pending_review")
        approved = sum(1 for item in self.review_queue if item["status"] == "approved")
        rejected = sum(1 for item in self.review_queue if item["status"] == "rejected")

        return {
            "total_queued": len(self.review_queue),
            "pending_review": pending,
            "approved": approved,
            "rejected": rejected,
            "audit_log_size": len(self.audit_log)
        }


class GovernanceReviewer:
    """
    Manages governance committee reviews and incident escalation.

    Tracks review cycles, approval workflows, and escalation paths
    for AI system changes and incidents.
    """

    def __init__(
        self,
        committee_members: List[str],
        review_cadence: str = "Quarterly",
        approval_threshold: float = 0.75
    ):
        """
        Initialize governance reviewer.

        Args:
            committee_members: Stakeholder roles (e.g., ["Security", "Legal", "Privacy"])
            review_cadence: How often full reviews occur
            approval_threshold: Fraction of committee needed to approve (0.75 = 75%)
        """
        self.committee_members = committee_members
        self.review_cadence = review_cadence
        self.approval_threshold = approval_threshold
        self.review_history = []
        self.incidents = []
        logger.info(
            f"GovernanceReviewer initialized: {len(committee_members)} members, "
            f"{review_cadence} reviews, {approval_threshold*100}% approval threshold"
        )

    def submit_for_review(
        self,
        change_type: str,
        description: str,
        impact_assessment: str,
        submitted_by: str
    ) -> Dict[str, Any]:
        """
        Submit a change for governance review.

        Args:
            change_type: Type of change (e.g., "model_update", "data_source_change")
            description: What is being changed
            impact_assessment: Expected impact on users/performance
            submitted_by: Who is requesting the change

        Returns:
            Review tracking information
        """
        review = {
            "id": len(self.review_history) + 1,
            "change_type": change_type,
            "description": description,
            "impact_assessment": impact_assessment,
            "submitted_by": submitted_by,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "pending_review",
            "votes": {},
            "decision": None,
            "decision_at": None
        }

        self.review_history.append(review)

        logger.info(
            f"Change submitted for review: {change_type} (Review #{review['id']})"
        )

        return {
            "review_id": review["id"],
            "status": "submitted",
            "committee_size": len(self.committee_members),
            "approval_threshold": self.approval_threshold
        }

    def cast_vote(
        self,
        review_id: int,
        committee_member: str,
        vote: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Committee member casts vote on a pending review.

        Args:
            review_id: Which review to vote on
            committee_member: Who is voting
            vote: "approve" or "reject"
            comments: Optional reasoning

        Returns:
            Updated review status
        """
        if committee_member not in self.committee_members:
            logger.error(f"Invalid committee member: {committee_member}")
            return {
                "status": "error",
                "message": f"{committee_member} is not on the committee"
            }

        review = next((r for r in self.review_history if r["id"] == review_id), None)

        if not review:
            logger.error(f"Review #{review_id} not found")
            return {
                "status": "error",
                "message": f"Review #{review_id} not found"
            }

        if review["status"] != "pending_review":
            logger.error(f"Review #{review_id} is not pending (status: {review['status']})")
            return {
                "status": "error",
                "message": f"Review #{review_id} has already been decided"
            }

        review["votes"][committee_member] = {
            "vote": vote,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"{committee_member} voted '{vote}' on Review #{review_id}")

        # Check if voting is complete
        votes_cast = len(review["votes"])
        if votes_cast == len(self.committee_members):
            self._finalize_review(review)

        return {
            "status": "vote_recorded",
            "review_id": review_id,
            "votes_cast": votes_cast,
            "votes_needed": len(self.committee_members),
            "current_decision": review["decision"]
        }

    def _finalize_review(self, review: Dict[str, Any]):
        """Finalize review once all votes are in."""
        approvals = sum(1 for v in review["votes"].values() if v["vote"] == "approve")
        approval_rate = approvals / len(self.committee_members)

        if approval_rate >= self.approval_threshold:
            review["decision"] = "approved"
            review["status"] = "approved"
        else:
            review["decision"] = "rejected"
            review["status"] = "rejected"

        review["decision_at"] = datetime.utcnow().isoformat()
        review["approval_rate"] = round(approval_rate, 3)

        logger.info(
            f"Review #{review['id']} finalized: {review['decision']} "
            f"({approvals}/{len(self.committee_members)} votes)"
        )

    def report_incident(
        self,
        incident_type: str,
        description: str,
        severity: str,
        reported_by: str
    ) -> Dict[str, Any]:
        """
        Report an AI system incident for governance review.

        Args:
            incident_type: Type of incident (e.g., "bias_detected", "privacy_breach")
            description: What happened
            severity: "low", "medium", "high", or "critical"
            reported_by: Who reported it

        Returns:
            Incident tracking information
        """
        incident = {
            "id": len(self.incidents) + 1,
            "incident_type": incident_type,
            "description": description,
            "severity": severity,
            "reported_by": reported_by,
            "reported_at": datetime.utcnow().isoformat(),
            "status": "open",
            "escalated": severity in ["high", "critical"],
            "resolution": None,
            "resolved_at": None
        }

        self.incidents.append(incident)

        if incident["escalated"]:
            logger.error(
                f"🚨 CRITICAL INCIDENT #{incident['id']}: {incident_type} - "
                f"Severity: {severity}"
            )
        else:
            logger.warning(
                f"⚠️ Incident #{incident['id']}: {incident_type} - "
                f"Severity: {severity}"
            )

        return {
            "incident_id": incident["id"],
            "status": "reported",
            "escalated": incident["escalated"],
            "next_steps": "Committee will review at next meeting" if not incident["escalated"] else "Immediate escalation to executive team"
        }

    def get_governance_summary(self) -> Dict[str, Any]:
        """
        Get overall governance health metrics.

        Returns:
            Summary of reviews, incidents, and committee activity
        """
        total_reviews = len(self.review_history)
        approved = sum(1 for r in self.review_history if r["decision"] == "approved")
        rejected = sum(1 for r in self.review_history if r["decision"] == "rejected")
        pending = sum(1 for r in self.review_history if r["status"] == "pending_review")

        total_incidents = len(self.incidents)
        open_incidents = sum(1 for i in self.incidents if i["status"] == "open")
        critical_incidents = sum(1 for i in self.incidents if i["severity"] == "critical")

        return {
            "committee": {
                "members": self.committee_members,
                "size": len(self.committee_members),
                "review_cadence": self.review_cadence,
                "approval_threshold": self.approval_threshold
            },
            "reviews": {
                "total": total_reviews,
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
                "approval_rate": round(approved / total_reviews, 3) if total_reviews > 0 else 0
            },
            "incidents": {
                "total": total_incidents,
                "open": open_incidents,
                "critical": critical_incidents
            }
        }
