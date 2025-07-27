"""
Base evaluator class for LLM evaluation framework.
Demonstrates systematic V&V methodologies from automotive testing.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time
import json

class EvaluationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class EvaluationResult:
    """Structured evaluation result following automotive V&V standards"""
    test_id: str
    model_name: str
    prompt: str
    response: str
    score: float
    criteria: str
    status: EvaluationStatus
    metadata: Dict[str, Any]
    timestamp: float
    execution_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "model_name": self.model_name,
            "prompt": self.prompt,
            "response": self.response,
            "score": self.score,
            "criteria": self.criteria,
            "status": self.status.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms
        }

class BaseEvaluator(ABC):
    """
    Abstract base class for all evaluators.
    Implements automotive-style systematic testing approach.
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"evaluator.{name}")
        self.results: List[EvaluationResult] = []
        
    @abstractmethod
    def evaluate_single(self, model_name: str, prompt: str, response: str, **kwargs) -> EvaluationResult:
        """Evaluate a single model response"""
        pass
    
    def evaluate_batch(self, test_cases: List[Dict[str, Any]]) -> List[EvaluationResult]:
        """
        Evaluate a batch of test cases with systematic logging.
        Demonstrates batch processing capabilities for AI safety evaluation.
        """
        results = []
        
        self.logger.info(f"Starting batch evaluation: {len(test_cases)} test cases")
        
        for i, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                
                result = self.evaluate_single(
                    model_name=test_case["model_name"],
                    prompt=test_case["prompt"], 
                    response=test_case["response"],
                    **test_case.get("metadata", {})
                )
                
                result.execution_time_ms = (time.time() - start_time) * 1000
                result.timestamp = start_time
                
                results.append(result)
                self.results.append(result)
                
                self.logger.debug(f"Completed test {i+1}/{len(test_cases)}: {result.test_id}")
                
            except Exception as e:
                self.logger.error(f"Failed test case {i}: {str(e)}")
                error_result = EvaluationResult(
                    test_id=f"error_{i}",
                    model_name=test_case.get("model_name", "unknown"),
                    prompt=test_case.get("prompt", ""),
                    response="ERROR",
                    score=0.0,
                    criteria=self.name,
                    status=EvaluationStatus.FAILED,
                    metadata={"error": str(e)},
                    timestamp=time.time(),
                    execution_time_ms=0.0
                )
                results.append(error_result)
        
        self.logger.info(f"Batch evaluation completed: {len(results)} results")
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate evaluation report with automotive V&V style metrics"""
        if not self.results:
            return {"error": "No evaluation results available"}
            
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == EvaluationStatus.COMPLETED])
        failed_tests = len([r for r in self.results if r.status == EvaluationStatus.FAILED])
        
        scores = [r.score for r in self.results if r.status == EvaluationStatus.COMPLETED]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "evaluator": self.name,
            "version": self.version,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
                "average_score": avg_score,
                "min_score": min(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0
            },
            "detailed_results": [r.to_dict() for r in self.results]
        }
    
    def save_results(self, filepath: str) -> None:
        """Save evaluation results to file"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"Results saved to {filepath}")