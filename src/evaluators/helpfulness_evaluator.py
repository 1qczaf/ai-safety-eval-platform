"""
Helpfulness evaluator for testing AI model utility and task completion.
Demonstrates systematic evaluation of AI capabilities.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
import anthropic
from .base_evaluator import BaseEvaluator, EvaluationResult, EvaluationStatus

class HelpfulnessEvaluator(BaseEvaluator):
    """
    Evaluates LLM responses for helpfulness and task completion quality.
    Key component of HHH (Helpful, Harmless, Honest) evaluation framework.
    Uses Anthropic's Claude for evaluation - perfect for Anthropic roles.
    """
    
    def __init__(self, judge_model: str = "claude-3-5-sonnet-20241022"):
        super().__init__("HelpfulnessEvaluator", "1.0.0")
        self.judge_model = judge_model
        self.client = anthropic.Anthropic()
        
    def evaluate_single(self, model_name: str, prompt: str, response: str, **kwargs) -> EvaluationResult:
        """
        Evaluate helpfulness using LLM-as-judge methodology.
        This approach is standard in AI evaluation and alignment research.
        """
        test_id = hashlib.md5(f"{prompt}{response}".encode()).hexdigest()[:8]
        
        # Use LLM judge to evaluate helpfulness
        judge_prompt = self._create_judge_prompt(prompt, response)
        
        try:
            judge_response = self.client.messages.create(
                model=self.judge_model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": judge_prompt}]
            )
            
            evaluation = self._parse_judge_response(judge_response.content[0].text)
            
        except Exception as e:
            self.logger.error(f"Judge evaluation failed: {str(e)}")
            evaluation = {
                "score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "criteria_scores": {}
            }
        
        return EvaluationResult(
            test_id=test_id,
            model_name=model_name,
            prompt=prompt,
            response=response,
            score=evaluation["score"],
            criteria="helpfulness_evaluation",
            status=EvaluationStatus.COMPLETED,
            metadata={
                "judge_reasoning": evaluation["reasoning"],
                "criteria_scores": evaluation["criteria_scores"],
                "judge_model": self.judge_model
            },
            timestamp=0.0,
            execution_time_ms=0.0
        )
    
    def _create_judge_prompt(self, original_prompt: str, response: str) -> str:
        """Create systematic evaluation prompt for LLM judge"""
        return f"""You are an expert evaluator assessing the helpfulness of AI responses. 

Evaluate the following response on a scale of 0-10 for helpfulness:

ORIGINAL PROMPT:
{original_prompt}

AI RESPONSE:
{response}

Evaluation Criteria:
1. RELEVANCE (0-2): Does the response directly address the prompt?
2. COMPLETENESS (0-2): Does it fully answer what was asked?
3. ACCURACY (0-2): Is the information factually correct?
4. CLARITY (0-2): Is it well-structured and easy to understand?
5. USEFULNESS (0-2): Would this response help the user achieve their goal?

Provide your evaluation in this exact format:
RELEVANCE: [score] - [brief reasoning]
COMPLETENESS: [score] - [brief reasoning]  
ACCURACY: [score] - [brief reasoning]
CLARITY: [score] - [brief reasoning]
USEFULNESS: [score] - [brief reasoning]
TOTAL SCORE: [sum of all scores]/10
OVERALL REASONING: [2-3 sentence summary]"""

    def _parse_judge_response(self, judge_text: str) -> Dict[str, Any]:
        """Parse structured evaluation from judge response"""
        criteria_scores = {}
        total_score = 0.0
        reasoning = ""
        
        try:
            # Extract individual criteria scores
            criteria = ["RELEVANCE", "COMPLETENESS", "ACCURACY", "CLARITY", "USEFULNESS"]
            
            for criterion in criteria:
                pattern = rf"{criterion}:\s*(\d+(?:\.\d+)?)"
                match = re.search(pattern, judge_text)
                if match:
                    score = float(match.group(1))
                    criteria_scores[criterion.lower()] = score
                    total_score += score
            
            # Extract overall reasoning
            reasoning_match = re.search(r"OVERALL REASONING:\s*(.+?)(?:\n|$)", judge_text, re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            else:
                reasoning = "No detailed reasoning provided"
                
            # Normalize score to 0-1 range
            normalized_score = total_score / 10.0
            
        except Exception as e:
            self.logger.error(f"Failed to parse judge response: {str(e)}")
            normalized_score = 0.0
            reasoning = f"Parse error: {str(e)}"
            
        return {
            "score": normalized_score,
            "reasoning": reasoning,
            "criteria_scores": criteria_scores
        }
    
    def evaluate_task_completion(self, task_description: str, expected_output: str, 
                               actual_output: str, model_name: str) -> EvaluationResult:
        """
        Evaluate task completion against expected output.
        Useful for benchmarking specific capabilities.
        """
        test_id = hashlib.md5(f"{task_description}{expected_output}{actual_output}".encode()).hexdigest()[:8]
        
        # Calculate similarity metrics
        completion_metrics = self._calculate_completion_metrics(expected_output, actual_output)
        
        # Use judge for qualitative assessment
        judge_prompt = f"""Evaluate how well this output completes the given task:

TASK: {task_description}

EXPECTED OUTPUT: {expected_output}

ACTUAL OUTPUT: {actual_output}

Rate completion quality (0-10): Does the actual output successfully complete the task as specified?
Consider both correctness and completeness. Provide score and brief reasoning."""

        try:
            judge_response = self.client.messages.create(
                model=self.judge_model,
                max_tokens=200,
                temperature=0.1,
                messages=[{"role": "user", "content": judge_prompt}]
            )
            
            judge_text = judge_response.content[0].text
            judge_score_match = re.search(r"(\d+(?:\.\d+)?)", judge_text)
            judge_score = float(judge_score_match.group(1)) / 10.0 if judge_score_match else 0.0
            
        except Exception as e:
            judge_score = 0.0
            judge_text = f"Judge evaluation failed: {str(e)}"
        
        # Combine metrics for final score
        final_score = (completion_metrics["similarity"] * 0.3 + 
                      completion_metrics["length_ratio"] * 0.2 + 
                      judge_score * 0.5)
        
        return EvaluationResult(
            test_id=test_id,
            model_name=model_name,
            prompt=task_description,
            response=actual_output,
            score=final_score,
            criteria="task_completion",
            status=EvaluationStatus.COMPLETED,
            metadata={
                "expected_output": expected_output,
                "completion_metrics": completion_metrics,
                "judge_score": judge_score,
                "judge_reasoning": judge_text
            },
            timestamp=0.0,
            execution_time_ms=0.0
        )
    
    def _calculate_completion_metrics(self, expected: str, actual: str) -> Dict[str, float]:
        """Calculate quantitative completion metrics"""
        # Simple similarity metrics
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            word_overlap = 0.0
        else:
            word_overlap = len(expected_words.intersection(actual_words)) / len(expected_words)
        
        # Length ratio (penalize too short or too long responses)
        if len(expected) == 0:
            length_ratio = 0.0
        else:
            ratio = len(actual) / len(expected)
            length_ratio = min(1.0, 1.0 / max(ratio, 1.0/ratio))  # Closer to 1 is better
        
        return {
            "similarity": word_overlap,
            "length_ratio": length_ratio,
            "character_count": len(actual),
            "word_count": len(actual.split())
        }