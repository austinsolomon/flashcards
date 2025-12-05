"""
Tests for dark pattern detection frameworks.

Validates framework configuration, pattern definitions, and detection rules.
"""

import pytest

from src.frameworks.base import Citation, DetectionRules, PatternDefinition, Severity
from src.frameworks.ieee_7010 import IEEE7010Framework
from src.frameworks.dsa_article_28 import DSAArticle28Framework
from src.frameworks.attention_economy import AttentionEconomyFramework
from src.frameworks.ico_aadc import ICOAADCFramework


class TestFrameworkStructure:
    """Test framework structure and configuration."""

    def test_ieee_7010_framework(self):
        """Test IEEE 7010 framework is properly configured."""
        framework = IEEE7010Framework

        assert framework.name == "IEEE 7010-2020"
        assert framework.version == "1.0"
        assert len(framework.patterns) > 0
        assert framework.enabled is True

    def test_dsa_article_28_framework(self):
        """Test DSA Article 28 framework is properly configured."""
        framework = DSAArticle28Framework

        assert framework.name == "DSA Article 28"
        assert framework.version == "2022/2065"
        assert len(framework.patterns) > 0

    def test_attention_economy_framework(self):
        """Test Attention Economy framework is properly configured."""
        framework = AttentionEconomyFramework

        assert "Attention Economy" in framework.name
        assert len(framework.patterns) > 0

    def test_ico_aadc_framework(self):
        """Test ICO AADC framework is properly configured."""
        framework = ICOAADCFramework

        assert "AADC" in framework.name or "Age Appropriate" in framework.name
        assert len(framework.patterns) > 0


class TestPatternDefinitions:
    """Test individual pattern definitions."""

    def test_patterns_have_required_fields(self):
        """Test all patterns have required fields."""
        frameworks = [
            IEEE7010Framework,
            DSAArticle28Framework,
            AttentionEconomyFramework,
            ICOAADCFramework,
        ]

        for framework in frameworks:
            for pattern in framework.patterns:
                assert pattern.id
                assert pattern.name
                assert pattern.description
                assert pattern.detection_rules
                assert isinstance(pattern.severity, Severity)
                assert 0.0 <= pattern.confidence_threshold <= 1.0

    def test_detection_rules_structure(self):
        """Test detection rules are properly structured."""
        pattern = IEEE7010Framework.patterns[0]
        rules = pattern.detection_rules

        assert isinstance(rules, DetectionRules)
        # At least one type of rule should be present
        assert (
            len(rules.visual_indicators) > 0
            or len(rules.textual_patterns) > 0
            or len(rules.structural_markers) > 0
            or len(rules.behavioral_signals) > 0
        )

    def test_pattern_ids_unique(self):
        """Test pattern IDs are unique within frameworks."""
        frameworks = [
            IEEE7010Framework,
            DSAArticle28Framework,
            AttentionEconomyFramework,
            ICOAADCFramework,
        ]

        for framework in frameworks:
            pattern_ids = [p.id for p in framework.patterns]
            assert len(pattern_ids) == len(set(pattern_ids)), f"Duplicate IDs in {framework.name}"

    def test_citations_present(self):
        """Test patterns have legal citations."""
        frameworks = [
            IEEE7010Framework,
            DSAArticle28Framework,
            AttentionEconomyFramework,
            ICOAADCFramework,
        ]

        for framework in frameworks:
            for pattern in framework.patterns:
                assert len(pattern.legal_citations) > 0, f"{pattern.id} missing citations"
                for citation in pattern.legal_citations:
                    assert isinstance(citation, Citation)
                    assert citation.source
                    assert citation.text


class TestFrameworkMethods:
    """Test framework methods."""

    def test_get_pattern(self):
        """Test getting pattern by ID."""
        framework = IEEE7010Framework
        pattern_id = framework.patterns[0].id

        pattern = framework.get_pattern(pattern_id)
        assert pattern is not None
        assert pattern.id == pattern_id

        # Test non-existent pattern
        assert framework.get_pattern("nonexistent_id") is None

    def test_get_patterns_by_severity(self):
        """Test filtering patterns by severity."""
        framework = DSAArticle28Framework

        for severity in [Severity.MINOR, Severity.MODERATE, Severity.SEVERE, Severity.CRITICAL]:
            patterns = framework.get_patterns_by_severity(severity)
            for pattern in patterns:
                assert pattern.severity == severity

    def test_adjust_confidence_threshold(self):
        """Test adjusting confidence threshold."""
        framework = IEEE7010Framework
        pattern_id = framework.patterns[0].id
        original_threshold = framework.patterns[0].confidence_threshold

        # Adjust threshold
        success = framework.adjust_confidence_threshold(pattern_id, 0.9)
        assert success is True
        assert framework.get_pattern(pattern_id).confidence_threshold == 0.9

        # Restore original
        framework.adjust_confidence_threshold(pattern_id, original_threshold)

    def test_validate_evidence(self):
        """Test evidence validation."""
        from src.frameworks.base import EvidenceType

        framework = IEEE7010Framework
        pattern = framework.patterns[0]

        # Should pass with all required evidence
        evidence_types = pattern.evidence_requirements
        assert framework.validate_evidence(pattern.id, evidence_types) is True

        # Should fail with missing evidence
        assert framework.validate_evidence(pattern.id, []) is False


class TestSpecificPatterns:
    """Test specific pattern implementations."""

    def test_infinite_scroll_pattern(self):
        """Test infinite scroll pattern (IEEE 7010)."""
        pattern = IEEE7010Framework.get_pattern("ieee_7010_addiction_infinite_scroll")

        assert pattern is not None
        assert "infinite" in pattern.name.lower()
        assert pattern.severity == Severity.SEVERE
        assert "scroll" in " ".join(pattern.detection_rules.behavioral_signals).lower()

    def test_confirmshaming_pattern(self):
        """Test confirmshaming pattern (DSA Article 28)."""
        pattern = DSAArticle28Framework.get_pattern("dsa_28_1a_confirmshaming")

        assert pattern is not None
        assert "sham" in pattern.name.lower()
        assert any("no, i don't" in p.lower() for p in pattern.detection_rules.textual_patterns)

    def test_hidden_costs_pattern(self):
        """Test hidden costs pattern (DSA Article 28)."""
        pattern = DSAArticle28Framework.get_pattern("dsa_28_1b_hidden_costs")

        assert pattern is not None
        assert pattern.severity == Severity.CRITICAL
        assert "cost" in pattern.name.lower() or "fee" in pattern.name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
