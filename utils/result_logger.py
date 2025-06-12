"""
Result Logger for Prompt Defense Simulator.

This module provides functions for logging and saving simulation results.
"""

import os
import json
import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("prompt_defense.result_logger")

class ResultLogger:
    """
    Logger for simulation results
    """
    
    def __init__(self, output_dir: str = "logs"):
        """
        Initialize the result logger
        
        Args:
            output_dir: Directory to store results
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
    
    def save_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save data to a JSON file
        
        Args:
            data: Data to save
            filename: Filename (default: results_TIMESTAMP.json)
            
        Returns:
            str: Path to the saved file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"results_{timestamp}.json"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Results saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving results to JSON: {e}")
            raise
    
    def save_csv(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Save results to a CSV file
        
        Args:
            results: List of result dictionaries
            filename: Filename (default: results_TIMESTAMP.csv)
            
        Returns:
            str: Path to the saved file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"results_{timestamp}.csv"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Define CSV fields
        fields = [
            "attack_name",
            "attack_category",
            "prompt",
            "response",
            "evaluation",
            "is_safe",
            "duration",
            "timestamp"
        ]
        
        # Save to file
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                
                for result in results:
                    # Flatten nested structure if needed
                    row = result.copy()
                    writer.writerow(row)
                
            logger.info(f"Results saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")
            raise
    
    def save_summary(self, summary: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save a summary to a JSON file
        
        Args:
            summary: Summary data
            filename: Filename (default: summary_TIMESTAMP.json)
            
        Returns:
            str: Path to the saved file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"summary_{timestamp}.json"
        
        return self.save_json(summary, filename)
    
    def save_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save a human-readable report
        
        Args:
            data: Report data with 'results' and 'summary' keys
            filename: Filename (default: report_TIMESTAMP.txt)
            
        Returns:
            str: Path to the saved file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.txt"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract data
        summary = data.get("summary", {})
        results = data.get("results", [])
        metadata = data.get("metadata", {})
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                # Write header
                f.write("====================================================\n")
                f.write("        PROMPT DEFENSE SIMULATOR - REPORT           \n")
                f.write("====================================================\n\n")
                
                # Write metadata
                f.write("SIMULATION METADATA\n")
                f.write("-------------------\n")
                f.write(f"Timestamp: {metadata.get('timestamp', datetime.now().isoformat())}\n")
                f.write(f"Model: {metadata.get('model', 'unknown')}\n")
                f.write(f"Safe Mode: {'Enabled' if metadata.get('safe_mode', False) else 'Disabled'}\n")
                f.write(f"Total Attacks: {summary.get('total', len(results))}\n\n")
                
                # Write summary
                f.write("SUMMARY\n")
                f.write("-------\n")
                f.write(f"Security Score: {summary.get('security_score', 0)}/100\n\n")
                
                # Write evaluations
                f.write("Evaluation Results:\n")
                for key, value in summary.get("percentages", {}).items():
                    f.write(f"  - {key.replace('_', ' ').title()}: {value}%\n")
                
                # Write category effectiveness
                f.write("\nCategory Effectiveness:\n")
                for category, data in summary.get("category_percentages", {}).items():
                    f.write(f"  - {category.replace('_', ' ').title()}:\n")
                    for key, value in data.items():
                        if key != "total":
                            f.write(f"      - {key.replace('_', ' ').title()}: {value}%\n")
                
                # Write top attacks
                f.write("\nSTRONGEST ATTACKS\n")
                f.write("-----------------\n")
                
                top_attacks = []
                for r in results:
                    if r.get("evaluation") in ["compromised", "potential_compromise"]:
                        top_attacks.append(r)
                
                top_attacks = sorted(top_attacks, key=lambda x: 
                                    1 if x.get("evaluation") == "compromised" else 0, 
                                    reverse=True)[:3]
                
                for i, attack in enumerate(top_attacks):
                    f.write(f"{i+1}. {attack.get('attack_name', 'Unknown')}\n")
                    f.write(f"   Category: {attack.get('attack_category', 'Unknown')}\n")
                    f.write(f"   Evaluation: {attack.get('evaluation', 'Unknown')}\n")
                    f.write(f"   Prompt: {attack.get('prompt', 'Unknown')[:100]}...\n\n")
                
                # Write detailed results
                f.write("\nDETAILED RESULTS\n")
                f.write("----------------\n")
                
                for i, result in enumerate(results):
                    f.write(f"Attack #{i+1}: {result.get('attack_name', 'Unknown')}\n")
                    f.write(f"Category: {result.get('attack_category', 'Unknown')}\n")
                    f.write(f"Evaluation: {result.get('evaluation', 'Unknown')}\n")
                    f.write(f"Prompt: {result.get('prompt', 'Unknown')[:100]}...\n")
                    
                    if "error" in result:
                        f.write(f"ERROR: {result['error']}\n")
                    else:
                        f.write(f"Response: {result.get('response', 'Unknown')[:100]}...\n")
                    
                    f.write("\n")
                
            logger.info(f"Report saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise 