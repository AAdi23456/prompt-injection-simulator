#!/usr/bin/env python3
"""
Run Evaluation for Prompt Defense Simulator

This script runs a full evaluation of system prompts against attack prompts,
analyzes the results, and generates visualizations and reports.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from simulator import Simulator
from utils.logger import setup_logger
from utils.evaluation import evaluate_results
from utils.result_logger import ResultLogger
from utils.analyzer import ResultAnalyzer

def load_system_prompts(directory: str) -> Dict[str, str]:
    """
    Load system prompts from a directory
    
    Args:
        directory: Path to the directory containing system prompt files
        
    Returns:
        dict: System prompts (name -> content)
    """
    prompts = {}
    
    # Check if directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"System prompts directory not found: {directory}")
    
    # Load system prompts
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            name = os.path.splitext(filename)[0]
            filepath = os.path.join(directory, filename)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                prompts[name] = content
            except Exception as e:
                logging.warning(f"Error loading system prompt '{name}': {e}")
    
    return prompts

def load_attack_prompts(filepath: str) -> List[Dict[str, Any]]:
    """
    Load attack prompts from a JSON file
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        list: Attack prompts
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Handle different file formats
        if isinstance(data, dict) and "prompts" in data:
            return data["prompts"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unrecognized format in {filepath}")
    except Exception as e:
        raise ValueError(f"Error loading attack prompts: {e}")

def run_evaluation(
    system_prompt: str,
    system_prompt_name: str,
    attack_prompts: List[Dict[str, Any]],
    model: str,
    safe_mode: bool,
    output_dir: str,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    Run an evaluation
    
    Args:
        system_prompt: System prompt content
        system_prompt_name: Name of the system prompt
        attack_prompts: List of attack prompts
        model: Model to use
        safe_mode: Whether to enable safe mode
        output_dir: Output directory
        delay: Delay between API calls
        
    Returns:
        dict: Evaluation results
    """
    logger = logging.getLogger(__name__)
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    eval_dir = os.path.join(output_dir, f"eval_{system_prompt_name}_{timestamp}")
    os.makedirs(eval_dir, exist_ok=True)
    
    # Initialize simulator
    simulator = Simulator(
        model=model,
        output_dir=eval_dir,
        safe_mode=safe_mode,
        log_results=True
    )
    
    # Set system prompt
    simulator.system_prompt = system_prompt
    
    # Set attack prompts
    simulator.attack_prompts = attack_prompts
    
    # Run simulation
    logger.info(f"Running evaluation for system prompt '{system_prompt_name}'")
    results = simulator.run_batch(delay=delay)
    
    # Save results
    result_path = simulator.save_results(results)
    
    # Evaluate results
    summary = evaluate_results(results)
    
    # Set up result logger and analyzer
    result_logger = ResultLogger(eval_dir)
    analyzer = ResultAnalyzer(eval_dir)
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    results_data = {
        "results": results,
        "metadata": {
            "model": model,
            "system_prompt": system_prompt_name,
            "safe_mode": safe_mode,
            "timestamp": datetime.now().isoformat(),
            "num_attacks": len(results)
        }
    }
    viz_paths = analyzer.generate_visualizations(results_data, f"{system_prompt_name}")
    
    # Generate report
    logger.info("Generating report...")
    report_data = {
        "results": results,
        "summary": summary,
        "metadata": results_data["metadata"]
    }
    report_path = result_logger.save_report(report_data, f"{system_prompt_name}_report.txt")
    
    # Save summary
    summary_path = result_logger.save_summary(summary, f"{system_prompt_name}_summary.json")
    
    return {
        "system_prompt": system_prompt_name,
        "results": results,
        "summary": summary,
        "result_path": result_path,
        "report_path": report_path,
        "summary_path": summary_path,
        "visualization_paths": viz_paths
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run a prompt defense evaluation")
    parser.add_argument("--system-prompts", type=str, default="system_prompts", help="Directory containing system prompt files")
    parser.add_argument("--attack-prompts", type=str, default="attacks/attack_prompts.json", help="Path to attack prompts file")
    parser.add_argument("--model", type=str, help="OpenAI model to use")
    parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    parser.add_argument("--no-safe-mode", action="store_false", dest="safe_mode", help="Disable safe mode")
    parser.add_argument("--output-dir", type=str, default="logs", help="Output directory for logs and results")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (in seconds)")
    parser.add_argument("--system-prompt", type=str, help="Specific system prompt to evaluate (by name)")
    parser.set_defaults(safe_mode=True)
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Get OpenAI model from environment if not specified
    model = args.model
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    try:
        # Load system prompts
        system_prompts = load_system_prompts(args.system_prompts)
        logger.info(f"Loaded {len(system_prompts)} system prompts")
        
        if len(system_prompts) == 0:
            logger.error(f"No system prompts found in {args.system_prompts}")
            return 1
        
        # Filter to specific system prompt if specified
        if args.system_prompt:
            if args.system_prompt in system_prompts:
                system_prompts = {args.system_prompt: system_prompts[args.system_prompt]}
            else:
                logger.error(f"System prompt '{args.system_prompt}' not found")
                return 1
        
        # Load attack prompts
        attack_prompts = load_attack_prompts(args.attack_prompts)
        logger.info(f"Loaded {len(attack_prompts)} attack prompts")
        
        # Run evaluations
        evaluations = []
        
        for name, prompt in system_prompts.items():
            try:
                evaluation = run_evaluation(
                    system_prompt=prompt,
                    system_prompt_name=name,
                    attack_prompts=attack_prompts,
                    model=model,
                    safe_mode=args.safe_mode,
                    output_dir=args.output_dir,
                    delay=args.delay
                )
                
                evaluations.append(evaluation)
                
                # Print summary
                security_score = evaluation["summary"]["security_score"]
                logger.info(f"System prompt '{name}' security score: {security_score}/100")
                
            except Exception as e:
                logger.error(f"Error evaluating system prompt '{name}': {e}")
        
        # Compare evaluations if more than one
        if len(evaluations) > 1:
            logger.info("\nSystem Prompt Comparison:")
            
            # Sort by security score (descending)
            evaluations.sort(key=lambda e: e["summary"]["security_score"], reverse=True)
            
            for i, eval_data in enumerate(evaluations):
                name = eval_data["system_prompt"]
                score = eval_data["summary"]["security_score"]
                compromised = eval_data["summary"]["evaluations"]["compromised"]
                secure = eval_data["summary"]["evaluations"]["secure"]
                total = eval_data["summary"]["total"]
                
                logger.info(f"{i+1}. {name}: {score}/100 (Compromised: {compromised}/{total}, Secure: {secure}/{total})")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 