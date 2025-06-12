# Prompt Injection & Jailbreak Defense Simulator

A test harness for evaluating system prompts against various prompt injection and jailbreak attempts.

## Overview

This project provides a simulation environment to test how well system prompts hold up against different types of prompt injection and jailbreak attempts. It helps in developing more robust AI systems by identifying vulnerabilities in system prompts and suggesting improvements.

## Features

- Test system prompts against common attack vectors
- Document and analyze the effectiveness of different attack strategies
- Implement "Safe Mode" to detect potentially risky patterns in user inputs
- Generate comprehensive reports of test results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prompt-injection-simulator.git
cd prompt-injection-simulator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the simulator with:
```bash
python run_simulation.py
```

For detailed analysis of results:
```bash
python analyze_results.py logs/results_20250612_160211.json --report --csv
```

## Attack Strategies Tested

The simulator tests against various attack strategies including:
1. Direct instruction override attempts
2. Roleplaying scenarios to bypass restrictions
3. Technical manipulation attempts
4. Context confusion techniques
5. Authority invocation strategies

## Safe Mode

The Safe Mode feature pre-screens user inputs for potentially risky patterns like:
- Requests to ignore or forget previous instructions
- Attempts to bypass system constraints
- Commands to disregard safety protocols

## Defense Strategies

Based on our testing, we recommend the following defense strategies:
1. System prompt hardening with explicit boundaries
2. Input validation and sanitization
3. Response filtering for sensitive information
4. Multi-layer verification for high-risk actions
5. Regular updates to defense mechanisms based on new attack patterns

## License

MIT