"""
Tests for L3 M3.1: Compliance Monitoring Dashboards

Tests ALL major functions from the compliance monitoring module.
Services: Mocked/offline for testing (no external dependencies)
"""

import pytest
import os
import json
from datetime import datetime
from src.l3_m3_monitoring_reporting import (
    ComplianceMetricsCollector,
    KPICalculator,
    DashboardGenerator,
    AlertManager,
    EvidenceExporter,
    ComplianceMetric,
    ComplianceKPI,
    calculate_compliance_score,
    generate_dashboard_config,
    export_soc2_evidence
)

# Force offline mode for tests
os.environ["PROMETHEUS_ENABLED"] = "false"
os.environ["GRAFANA_ENABLED"] = "false"
os.environ["OPA_ENABLED"] = "false"
os.environ["OFFLINE"] = "true"


# Fixtures

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "prometheus": {"enabled": False},
        "grafana": {"enabled": False},
        "offline": True
    }


@pytest.fixture
def sample_documents():
    """Sample documents for PII testing"""
    return [
        {"doc_id": "doc_001", "pii_detected": True},
        {"doc_id": "doc_002", "pii_detected": True},
        {"doc_id": "doc_003", "pii_detected": False},
        {"doc_id": "doc_004", "pii_detected": True},
        {"doc_id": "doc_005", "pii_detected": False}
    ]


@pytest.fixture
def sample_access_logs():
    """Sample access logs for authorization testing"""
    return [
        {"user": "user_001", "authorized": True},
        {"user": "user_002", "authorized": True},
        {"user": "user_003", "authorized": False},
        {"user": "user_004", "authorized": True}
    ]


@pytest.fixture
def sample_events():
    """Sample events for audit trail testing"""
    return [
        {"event_type": "query", "logged": True},
        {"event_type": "ingestion", "logged": True},
        {"event_type": "deletion", "logged": True},
        {"event_type": "query", "logged": False}
    ]


# Test ComplianceMetricsCollector

def test_metrics_collector_initialization(sample_config):
    """Test metrics collector initializes correctly"""
    collector = ComplianceMetricsCollector(sample_config)
    assert collector.config == sample_config
    assert collector.metrics_buffer == []


def test_collect_pii_metrics(sample_config, sample_documents):
    """Test PII metrics collection"""
    collector = ComplianceMetricsCollector(sample_config)
    metric = collector.collect_pii_metrics("test_tenant", sample_documents)

    assert metric.metric_name == "pii_detection_rate"
    assert metric.tenant_id == "test_tenant"
    assert 0 <= metric.value <= 100
    assert metric.threshold == 95.0
    assert len(collector.metrics_buffer) == 1


def test_collect_access_control_metrics(sample_config, sample_access_logs):
    """Test access control metrics collection"""
    collector = ComplianceMetricsCollector(sample_config)
    metric = collector.collect_access_control_metrics("test_tenant", sample_access_logs)

    assert metric.metric_name == "access_control_violations"
    assert metric.tenant_id == "test_tenant"
    assert 0 <= metric.value <= 100
    assert metric.threshold == 0.1


def test_collect_audit_trail_metrics(sample_config, sample_events):
    """Test audit trail metrics collection"""
    collector = ComplianceMetricsCollector(sample_config)
    metric = collector.collect_audit_trail_metrics("test_tenant", sample_events)

    assert metric.metric_name == "audit_trail_completeness"
    assert metric.tenant_id == "test_tenant"
    assert 0 <= metric.value <= 100
    assert metric.threshold == 99.0


def test_flush_metrics_offline(sample_config, sample_documents):
    """Test metrics flushing in offline mode"""
    collector = ComplianceMetricsCollector(sample_config)
    collector.collect_pii_metrics("test_tenant", sample_documents)

    flushed = collector.flush_metrics()

    assert len(flushed) == 1
    assert len(collector.metrics_buffer) == 0


# Test KPICalculator

def test_kpi_calculator_initialization(sample_config):
    """Test KPI calculator initializes with correct thresholds"""
    calculator = KPICalculator(sample_config)
    assert calculator.thresholds["audit_trail_completeness"] == 99.0
    assert calculator.thresholds["pii_detection_precision"] == 95.0
    assert calculator.thresholds["access_control_violations"] == 0.1


def test_calculate_audit_completeness(sample_config):
    """Test audit trail completeness KPI calculation"""
    calculator = KPICalculator(sample_config)

    metrics = [
        ComplianceMetric(
            metric_name="audit_trail_completeness",
            value=99.5,
            timestamp=datetime.now(),
            tenant_id="test",
            labels={},
            threshold=99.0
        )
    ]

    kpi = calculator.calculate_audit_completeness(metrics)

    assert kpi.name == "audit_trail_completeness"
    assert kpi.current_value == 99.5
    assert kpi.target_value == 99.0
    assert kpi.status == "healthy"
    assert kpi.is_compliant() is True


def test_calculate_audit_completeness_violation(sample_config):
    """Test audit trail completeness KPI with violation"""
    calculator = KPICalculator(sample_config)

    metrics = [
        ComplianceMetric(
            metric_name="audit_trail_completeness",
            value=98.0,
            timestamp=datetime.now(),
            tenant_id="test",
            labels={},
            threshold=99.0
        )
    ]

    kpi = calculator.calculate_audit_completeness(metrics)

    assert kpi.status == "critical"
    assert kpi.is_compliant() is False


def test_calculate_access_violations(sample_config):
    """Test access control violations KPI calculation"""
    calculator = KPICalculator(sample_config)

    metrics = [
        ComplianceMetric(
            metric_name="access_control_violations",
            value=0.05,
            timestamp=datetime.now(),
            tenant_id="test",
            labels={},
            threshold=0.1
        )
    ]

    kpi = calculator.calculate_access_violations(metrics)

    assert kpi.name == "access_control_violations"
    assert kpi.current_value == 0.05
    assert kpi.status == "healthy"
    assert kpi.is_compliant() is True


def test_calculate_all_kpis(sample_config):
    """Test calculation of all KPIs"""
    calculator = KPICalculator(sample_config)

    metrics = [
        ComplianceMetric("audit_trail_completeness", 99.5, datetime.now(), "test", {}),
        ComplianceMetric("pii_detection_rate", 96.0, datetime.now(), "test", {}),
        ComplianceMetric("access_control_violations", 0.05, datetime.now(), "test", {})
    ]

    kpis = calculator.calculate_all_kpis(metrics)

    # Should return 6 KPIs (audit, pii precision, pii recall, access, encryption, cert)
    assert len(kpis) == 6
    assert all(isinstance(kpi, ComplianceKPI) for kpi in kpis)


# Test DashboardGenerator

def test_dashboard_generator_initialization(sample_config):
    """Test dashboard generator initializes correctly"""
    generator = DashboardGenerator(sample_config)
    assert generator.config == sample_config


def test_generate_cfo_dashboard(sample_config):
    """Test CFO dashboard generation"""
    generator = DashboardGenerator(sample_config)
    calculator = KPICalculator(sample_config)

    metrics = [ComplianceMetric("audit_trail_completeness", 99.5, datetime.now(), "test", {})]
    kpis = calculator.calculate_all_kpis(metrics)

    dashboard = generator.generate_cfo_dashboard(kpis)

    assert dashboard["title"] == "CFO Compliance Overview"
    assert "audit" in dashboard["tags"]
    assert "panels" in dashboard
    assert len(dashboard["panels"]) > 0


def test_generate_cto_dashboard(sample_config):
    """Test CTO dashboard generation"""
    generator = DashboardGenerator(sample_config)
    calculator = KPICalculator(sample_config)

    metrics = [ComplianceMetric("encryption_coverage", 100.0, datetime.now(), "test", {})]
    kpis = calculator.calculate_all_kpis(metrics)

    dashboard = generator.generate_cto_dashboard(kpis)

    assert dashboard["title"] == "CTO Technical Compliance"
    assert "technical" in dashboard["tags"]
    assert "panels" in dashboard


def test_generate_compliance_officer_dashboard(sample_config):
    """Test Compliance Officer dashboard generation"""
    generator = DashboardGenerator(sample_config)
    calculator = KPICalculator(sample_config)

    metrics = [ComplianceMetric("pii_detection_rate", 96.0, datetime.now(), "test", {})]
    kpis = calculator.calculate_all_kpis(metrics)

    dashboard = generator.generate_compliance_officer_dashboard(kpis)

    assert dashboard["title"] == "Compliance Officer - Regulatory Dashboard"
    assert "regulatory" in dashboard["tags"]
    assert len(dashboard["panels"]) > 0


# Test AlertManager

def test_alert_manager_initialization(sample_config):
    """Test alert manager initializes correctly"""
    manager = AlertManager(sample_config)
    assert manager.config == sample_config
    assert manager.alert_rules == []


def test_create_alert_rule(sample_config):
    """Test alert rule creation"""
    manager = AlertManager(sample_config)

    kpi = ComplianceKPI("audit_trail_completeness", 98.0, 99.0, "%", "critical", "stable")
    rule = manager.create_alert_rule(kpi, "critical")

    assert rule["name"] == "audit_trail_completeness_threshold_violation"
    assert rule["severity"] == "critical"
    assert "pagerduty" in rule["notification_channels"]


def test_evaluate_kpis_no_violations(sample_config):
    """Test KPI evaluation with no violations"""
    manager = AlertManager(sample_config)

    kpis = [
        ComplianceKPI("audit_trail_completeness", 99.5, 99.0, "%", "healthy", "stable"),
        ComplianceKPI("encryption_coverage", 100.0, 100.0, "%", "healthy", "stable")
    ]

    alerts = manager.evaluate_kpis(kpis)

    assert len(alerts) == 0


def test_evaluate_kpis_with_violations(sample_config):
    """Test KPI evaluation with violations"""
    manager = AlertManager(sample_config)

    kpis = [
        ComplianceKPI("audit_trail_completeness", 98.0, 99.0, "%", "critical", "degrading"),
        ComplianceKPI("access_control_violations", 0.2, 0.1, "%", "warning", "stable")
    ]

    alerts = manager.evaluate_kpis(kpis)

    assert len(alerts) == 2
    assert any(alert["severity"] == "critical" for alert in alerts)


# Test EvidenceExporter

def test_evidence_exporter_initialization(sample_config):
    """Test evidence exporter initializes correctly"""
    exporter = EvidenceExporter(sample_config)
    assert exporter.config == sample_config


def test_export_soc2_evidence(sample_config):
    """Test SOC2 evidence export"""
    exporter = EvidenceExporter(sample_config)

    kpis = [
        ComplianceKPI("audit_trail_completeness", 99.9, 99.0, "%", "healthy", "stable"),
        ComplianceKPI("access_control_violations", 0.01, 0.1, "%", "healthy", "stable"),
        ComplianceKPI("encryption_coverage", 100.0, 100.0, "%", "healthy", "stable")
    ]

    report = exporter.export_soc2_evidence(kpis, 90)

    assert report["report_type"] == "SOC2_TSC_Evidence"
    assert report["time_range_days"] == 90
    assert "CC6.1" in report["control_mappings"]
    assert "CC7.2" in report["control_mappings"]
    assert "CC6.6" in report["control_mappings"]
    assert len(report["kpi_summary"]) == 3


# Test Convenience Functions

def test_calculate_compliance_score_all_compliant():
    """Test compliance score calculation with all KPIs compliant"""
    kpis = [
        ComplianceKPI("kpi1", 99.5, 99.0, "%", "healthy", "stable"),
        ComplianceKPI("kpi2", 100.0, 100.0, "%", "healthy", "stable"),
        ComplianceKPI("kpi3", 0.05, 0.1, "%", "healthy", "stable")
    ]

    score = calculate_compliance_score(kpis)

    assert score == 100.0


def test_calculate_compliance_score_partial_compliance():
    """Test compliance score with partial compliance"""
    kpis = [
        ComplianceKPI("kpi1", 99.5, 99.0, "%", "healthy", "stable"),
        ComplianceKPI("kpi2", 98.0, 99.0, "%", "critical", "degrading"),
        ComplianceKPI("kpi3", 0.05, 0.1, "%", "healthy", "stable")
    ]

    # kpi2 is not compliant, so 2/3 = 66.67%
    score = calculate_compliance_score(kpis)

    assert 66.0 <= score <= 67.0


def test_generate_dashboard_config_cfo():
    """Test dashboard config generation for CFO"""
    kpis = [ComplianceKPI("audit_trail_completeness", 99.5, 99.0, "%", "healthy", "stable")]

    config = generate_dashboard_config(kpis, "cfo")

    assert config["title"] == "CFO Compliance Overview"


def test_generate_dashboard_config_cto():
    """Test dashboard config generation for CTO"""
    kpis = [ComplianceKPI("encryption_coverage", 100.0, 100.0, "%", "healthy", "stable")]

    config = generate_dashboard_config(kpis, "cto")

    assert config["title"] == "CTO Technical Compliance"


def test_generate_dashboard_config_compliance_officer():
    """Test dashboard config generation for Compliance Officer"""
    kpis = [ComplianceKPI("pii_detection_precision", 96.0, 95.0, "%", "healthy", "stable")]

    config = generate_dashboard_config(kpis, "compliance_officer")

    assert config["title"] == "Compliance Officer - Regulatory Dashboard"


def test_export_soc2_evidence_convenience():
    """Test SOC2 evidence export convenience function"""
    kpis = [
        ComplianceKPI("audit_trail_completeness", 99.9, 99.0, "%", "healthy", "stable"),
        ComplianceKPI("access_control_violations", 0.01, 0.1, "%", "healthy", "stable")
    ]

    report = export_soc2_evidence(kpis, 90)

    assert report["report_type"] == "SOC2_TSC_Evidence"
    assert report["time_range_days"] == 90


# Integration Tests

def test_full_metrics_pipeline(sample_config, sample_documents, sample_access_logs, sample_events):
    """Test full metrics collection and KPI calculation pipeline"""
    # Collect metrics
    collector = ComplianceMetricsCollector(sample_config)
    collector.collect_pii_metrics("test_tenant", sample_documents)
    collector.collect_access_control_metrics("test_tenant", sample_access_logs)
    collector.collect_audit_trail_metrics("test_tenant", sample_events)

    metrics = collector.flush_metrics()

    # Calculate KPIs
    calculator = KPICalculator(sample_config)
    kpis = calculator.calculate_all_kpis(metrics)

    # Generate dashboard
    generator = DashboardGenerator(sample_config)
    dashboard = generator.generate_compliance_officer_dashboard(kpis)

    # Evaluate alerts
    alert_manager = AlertManager(sample_config)
    alerts = alert_manager.evaluate_kpis(kpis)

    # Export evidence
    exporter = EvidenceExporter(sample_config)
    evidence = exporter.export_soc2_evidence(kpis, 90)

    # Assertions
    assert len(metrics) == 3
    assert len(kpis) == 6
    assert "panels" in dashboard
    assert "control_mappings" in evidence


@pytest.mark.skipif(
    os.getenv("PROMETHEUS_ENABLED", "false").lower() != "true",
    reason="Prometheus not enabled"
)
def test_prometheus_integration():
    """Test Prometheus integration (if enabled)"""
    # This test would run if Prometheus is actually available
    # For now, it's skipped in offline mode
    pass
