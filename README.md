# AI Safety & Evaluation Platform

A comprehensive framework for evaluating Large Language Models (LLMs) with focus on safety, alignment, and performance testing - designed to demonstrate skills relevant to AI safety roles at companies like OpenAI and Anthropic.

## Features

- **LLM Safety Evaluation**: Automated testing for helpfulness, harmlessness, and honesty
- **Red-teaming Framework**: Adversarial testing for jailbreaks, bias, and harmful outputs  
- **Constitutional AI Simulation**: Principle-based behavior analysis and training
- **Model Interpretability**: Attention analysis and mechanistic interpretability tools
- **Automated Benchmarking**: Performance evaluation across multiple dimensions
- **Experiment Tracking**: MLflow integration for systematic evaluation

## Architecture

```
ai-safety-eval-platform/
├── src/
│   ├── evaluators/          # Core evaluation engines
│   ├── safety/              # Safety testing modules
│   ├── constitutional/      # Constitutional AI implementation
│   ├── red_team/           # Adversarial testing tools
│   ├── interpretability/   # Model analysis tools
│   └── benchmarks/         # Automated benchmarking
├── configs/                # Evaluation configurations
├── tests/                  # Test suites
└── experiments/            # Experiment results
```

## Technology Stack

- **Python 3.9+** with PyTorch, Transformers, Anthropic API
- **Claude Models** (Claude-3-Sonnet) for evaluation and constitutional AI
- **MLflow** for experiment tracking
- **Ray** for distributed evaluation
- **FastAPI** for web interface
- **Jupyter** for analysis notebooks

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key"
python demo.py
```

This project demonstrates systematic V&V methodologies applied to AI safety - leveraging automotive testing experience for safety-critical AI evaluation.# Test trigger for GitHub Actions

This change will trigger all workflows to run and demonstrate the CI/CD pipeline.

Sun Jul 27 17:54:28 CDT 2025
