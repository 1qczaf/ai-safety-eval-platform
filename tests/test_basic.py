#!/usr/bin/env python3
"""
Basic tests for AI Safety Evaluation Platform
"""

import pytest
import os
import sys

# Add src to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluators.safety_evaluator import SafetyEvaluator
from evaluators.helpfulness_evaluator import HelpfulnessEvaluator

def test_safety_evaluator_initialization():
    """Test that SafetyEvaluator can be initialized"""
    evaluator = SafetyEvaluator()
    assert evaluator is not None
    assert hasattr(evaluator, 'evaluate')

def test_helpfulness_evaluator_initialization():
    """Test that HelpfulnessEvaluator can be initialized"""
    evaluator = HelpfulnessEvaluator()
    assert evaluator is not None
    assert hasattr(evaluator, 'evaluate')

def test_safety_evaluator_basic_evaluation():
    """Test basic safety evaluation without API calls"""
    evaluator = SafetyEvaluator()
    
    # Test safe response
    safe_response = "I can help you with that programming question."
    result = evaluator.evaluate("How do I write a function?", safe_response)
    assert 'safety_score' in result
    assert result['safety_score'] >= 0.7  # Should be considered safe

def test_helpfulness_evaluator_basic_evaluation():
    """Test basic helpfulness evaluation"""
    evaluator = HelpfulnessEvaluator()
    
    # Test helpful response
    helpful_response = "Here's a detailed explanation with examples..."
    result = evaluator.evaluate("Explain this concept", helpful_response)
    assert 'helpfulness_score' in result
    assert result['helpfulness_score'] >= 0.6

def test_environment_variables():
    """Test that environment variables are properly configured"""
    # This test will pass if ANTHROPIC_API_KEY is set, skip if not
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        assert len(api_key) > 10  # Basic sanity check
        assert api_key.startswith('sk-')
    else:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping API key test")

def test_project_structure():
    """Test that project has required files and structure"""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    # Check for required files
    assert os.path.exists(os.path.join(project_root, 'README.md'))
    assert os.path.exists(os.path.join(project_root, 'requirements.txt'))
    
    # Check for required directories
    assert os.path.exists(os.path.join(project_root, 'src'))
    assert os.path.exists(os.path.join(project_root, 'src', 'evaluators'))
    assert os.path.exists(os.path.join(project_root, 'src', 'constitutional'))
    assert os.path.exists(os.path.join(project_root, 'src', 'red_team'))

if __name__ == "__main__":
    pytest.main([__file__])