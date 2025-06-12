"""
Analyzer module for Prompt Defense Simulator.

This module provides functions for analyzing and visualizing simulation results.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

from utils.evaluation import evaluate_results, get_category_effectiveness

logger = logging.getLogger("prompt_defense.analyzer")

class ResultAnalyzer:
    """
    Analyzer for simulation results
    """
    
    def __init__(self, output_dir: str = "logs"):
        """
        Initialize the analyzer
        
        Args:
            output_dir: Directory to store visualizations
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("viridis")
    
    def load_results(self, filepath: str) -> Dict[str, Any]:
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
                
            logger.info(f"Loaded results from {filepath}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading results from {filepath}: {e}")
            raise
    
    def convert_to_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert results to a pandas DataFrame
        
        Args:
            results: List of result dictionaries
            
        Returns:
            DataFrame: Results as a DataFrame
        """
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def evaluate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate results
        
        Args:
            results: List of result dictionaries
            
        Returns:
            dict: Evaluation summary
        """
        return evaluate_results(results)
    
    def plot_evaluation_breakdown(self, summary: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Plot the evaluation breakdown
        
        Args:
            summary: Summary dictionary from evaluate_results
            filename: Output filename (default: evaluation_breakdown_TIMESTAMP.png)
            
        Returns:
            str: Path to the saved plot
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"evaluation_breakdown_{timestamp}.png"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract data
        labels = []
        values = []
        
        for key, value in summary.get("percentages", {}).items():
            if key != "error" and value > 0:
                labels.append(key.replace("_", " ").title())
                values.append(value)
        
        # Create colors
        colors = sns.color_palette("viridis", len(labels))
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create pie chart
        plt.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.axis('equal')
        
        # Add title
        plt.title('Evaluation Breakdown', fontsize=16, pad=20)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved evaluation breakdown plot to {filepath}")
        return filepath
    
    def plot_category_effectiveness(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Plot the effectiveness of each attack category
        
        Args:
            results: List of result dictionaries
            filename: Output filename (default: category_effectiveness_TIMESTAMP.png)
            
        Returns:
            str: Path to the saved plot
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"category_effectiveness_{timestamp}.png"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Get category effectiveness
        effectiveness = get_category_effectiveness(results)
        
        # Sort by effectiveness (descending)
        categories = sorted(effectiveness.keys(), key=lambda k: effectiveness[k], reverse=True)
        scores = [effectiveness[k] for k in categories]
        
        # Format category names
        categories = [c.replace("_", " ").title() for c in categories]
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create bar chart
        bars = plt.bar(
            categories,
            scores,
            color=sns.color_palette("viridis", len(categories))
        )
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 1,
                f'{height:.1f}%',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        # Add labels and title
        plt.xlabel('Attack Category', fontsize=12)
        plt.ylabel('Effectiveness Score (%)', fontsize=12)
        plt.title('Attack Category Effectiveness', fontsize=16, pad=20)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set y-axis limit
        plt.ylim(0, 100)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved category effectiveness plot to {filepath}")
        return filepath
    
    def plot_security_score(self, summary: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Plot the security score
        
        Args:
            summary: Summary dictionary from evaluate_results
            filename: Output filename (default: security_score_TIMESTAMP.png)
            
        Returns:
            str: Path to the saved plot
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"security_score_{timestamp}.png"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract security score
        score = summary.get("security_score", 0)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create gauge chart
        gauge_colors = ['red', 'orange', 'yellow', 'yellowgreen', 'green']
        
        # Determine color based on score
        if score < 20:
            color_idx = 0
        elif score < 40:
            color_idx = 1
        elif score < 60:
            color_idx = 2
        elif score < 80:
            color_idx = 3
        else:
            color_idx = 4
        
        # Create semi-circle
        angles = np.linspace(0, 180, 100) * np.pi / 180
        xs = np.cos(angles)
        ys = np.sin(angles)
        
        # Plot semi-circle background
        plt.plot(xs, ys, 'k-', lw=3)
        
        # Plot colored arc based on score
        score_angle = score * np.pi / 100
        score_xs = np.cos(np.linspace(0, score_angle, 100))
        score_ys = np.sin(np.linspace(0, score_angle, 100))
        plt.plot(score_xs, score_ys, '-', color=gauge_colors[color_idx], lw=10)
        
        # Add score text
        plt.text(0, 0, f"{score:.1f}", fontsize=50, ha='center', va='center')
        plt.text(0, -0.2, "Security Score", fontsize=16, ha='center', va='center')
        
        # Add score categories
        categories = ['Critical', 'Poor', 'Fair', 'Good', 'Excellent']
        category_positions = np.linspace(0, 180, len(categories) + 1)[1:-1] * np.pi / 180
        
        for i, (pos, cat) in enumerate(zip(category_positions, categories)):
            x = 1.1 * np.cos(pos)
            y = 1.1 * np.sin(pos)
            plt.text(x, y, cat, fontsize=12, ha='center', va='center', rotation=pos * 180 / np.pi - 90)
        
        # Set aspect and limits
        plt.axis('equal')
        plt.xlim(-1.2, 1.2)
        plt.ylim(-0.3, 1.2)
        
        # Remove axes
        plt.axis('off')
        
        # Add title
        plt.title('System Prompt Security Score', fontsize=16, pad=20)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved security score plot to {filepath}")
        return filepath
    
    def generate_visualizations(self, results_data: Dict[str, Any], output_prefix: Optional[str] = None) -> List[str]:
        """
        Generate all visualizations for a results file
        
        Args:
            results_data: Results data dictionary
            output_prefix: Prefix for output filenames
            
        Returns:
            list: Paths to saved visualizations
        """
        # Extract results
        results = results_data.get("results", [])
        
        # Generate output prefix if not provided
        if output_prefix is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_prefix = f"viz_{timestamp}"
        
        # Evaluate results
        summary = self.evaluate_results(results)
        
        # Generate visualizations
        viz_paths = []
        
        # Evaluation breakdown
        eval_path = self.plot_evaluation_breakdown(
            summary,
            filename=f"{output_prefix}_eval_breakdown.png"
        )
        viz_paths.append(eval_path)
        
        # Category effectiveness
        cat_path = self.plot_category_effectiveness(
            results,
            filename=f"{output_prefix}_category_effectiveness.png"
        )
        viz_paths.append(cat_path)
        
        # Security score
        score_path = self.plot_security_score(
            summary,
            filename=f"{output_prefix}_security_score.png"
        )
        viz_paths.append(score_path)
        
        return viz_paths 