#!/usr/bin/env python3
"""
Run a simulation of the prompt defense system.

This script runs a simulation using the configured parameters and logs the results.
"""

import os
import argparse
import logging
from dotenv import load_dotenv

from simulator import Simulator
from utils.logger import setup_logger

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run a prompt defense simulation")
    parser.add_argument("--system-prompt", type=str, help="Path to system prompt file")
    parser.add_argument("--attack-prompts", type=str, help="Path to attack prompts file")
    parser.add_argument("--model", type=str, help="OpenAI model to use")
    parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    parser.add_argument("--no-safe-mode", action="store_false", dest="safe_mode", help="Disable safe mode")
    parser.add_argument("--output-dir", type=str, default="logs", help="Output directory for logs and results")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (in seconds)")
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
    
    # Initialize simulator
    simulator = Simulator(
        system_prompt_path=args.system_prompt,
        attack_prompts_path=args.attack_prompts,
        model=model,
        output_dir=args.output_dir,
        safe_mode=args.safe_mode
    )
    
    # Run simulation
    try:
        result_path = simulator.run(delay=args.delay)
        if result_path:
            logger.info(f"Results saved to {result_path}")
        
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 