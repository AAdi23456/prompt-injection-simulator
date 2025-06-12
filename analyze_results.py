#!/usr/bin/env python3
"""
Analyze Prompt Defense Simulator Results

This script analyzes results from simulation runs and generates visualizations.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, List, Optional

from utils.logger import setup_logger
from utils.evaluation import evaluate_results, get_strongest_attacks
from utils.result_logger import ResultLogger
from utils.analyzer import ResultAnalyzer

def load_results(filepath: str) -> Dict[str, Any]:
    """
    Load results from a JSON file
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        dict: Loaded results
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise ValueError(f"Error loading results file: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Analyze prompt defense simulation results")
    parser.add_argument("results_file", type=str, help="Path to results JSON file")
    parser.add_argument("--output-dir", type=str, default="logs", help="Output directory for visualizations and reports")
    parser.add_argument("--prefix", type=str, help="Prefix for output filenames")
    parser.add_argument("--report", action="store_true", help="Generate a text report")
    parser.add_argument("--csv", action="store_true", help="Generate a CSV file")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.WARNING if args.quiet else logging.INFO
    setup_logger(log_level)
    logger = logging.getLogger(__name__)
    
    # Load results
    try:
        results_data = load_results(args.results_file)
        results = results_data.get("results", [])
        metadata = results_data.get("metadata", {})
        
        logger.info(f"Loaded {len(results)} results from {args.results_file}")
        
        # Generate output prefix if not provided
        output_prefix = args.prefix
        if output_prefix is None:
            basename = os.path.basename(args.results_file)
            output_prefix = os.path.splitext(basename)[0]
        
        # Set up result logger and analyzer
        result_logger = ResultLogger(args.output_dir)
        analyzer = ResultAnalyzer(args.output_dir)
        
        # Evaluate results
        summary = evaluate_results(results)
        logger.info(f"Overall security score: {summary.get('security_score', 0)}/100")
        
        # Generate visualizations
        logger.info("Generating visualizations...")
        viz_paths = analyzer.generate_visualizations(results_data, output_prefix)
        logger.info(f"Generated {len(viz_paths)} visualizations")
        
        # Find strongest attacks
        strongest_attacks = get_strongest_attacks(results)
        
        if not args.quiet:
            # Print top attacks
            print("\n=== STRONGEST ATTACKS ===")
            for i, attack in enumerate(strongest_attacks):
                print(f"{i+1}. {attack.get('attack_name', 'Unknown')} ({attack.get('attack_category', 'Unknown')})")
                print(f"   Evaluation: {attack.get('evaluation', 'Unknown')}")
                print(f"   Prompt: {attack.get('prompt', 'Unknown')[:100]}...")
                print("")
        
        # Generate report if requested
        if args.report:
            logger.info("Generating report...")
            report_data = {
                "results": results,
                "summary": summary,
                "metadata": metadata
            }
            report_path = result_logger.save_report(report_data, f"{output_prefix}_report.txt")
            logger.info(f"Report saved to {report_path}")
        
        # Generate CSV if requested
        if args.csv:
            logger.info("Generating CSV...")
            csv_path = result_logger.save_csv(results, f"{output_prefix}_results.csv")
            logger.info(f"CSV saved to {csv_path}")
        
        # Save summary
        summary_path = result_logger.save_summary(summary, f"{output_prefix}_summary.json")
        logger.info(f"Summary saved to {summary_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error analyzing results: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 