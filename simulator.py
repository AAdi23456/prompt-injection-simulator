"""
Prompt Defense Simulator

This module provides the core simulator for testing system prompts against
various attack prompts and jailbreak attempts.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Import OpenAI API client
from utils.openai_client import get_completion

# Import safe mode components (if available)
try:
    from safe_mode.check_prompt import check_prompt
    SAFE_MODE_AVAILABLE = True
except ImportError:
    SAFE_MODE_AVAILABLE = False

class Simulator:
    """
    Simulator for testing system prompts against attack prompts
    """
    
    def __init__(
        self,
        system_prompt_path: Optional[str] = None,
        attack_prompts_path: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        output_dir: str = "logs",
        safe_mode: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
        log_results: bool = True
    ):
        """
        Initialize the simulator
        
        Args:
            system_prompt_path: Path to system prompt file (default: system_prompts/default.txt)
            attack_prompts_path: Path to attack prompts JSON file (default: attacks/attack_prompts.json)
            model: LLM model to use
            output_dir: Directory to store results
            safe_mode: Whether to enable safe mode
            temperature: Model temperature
            max_tokens: Maximum tokens in response
            log_results: Whether to log results to file
        """
        # Set up logging
        self.logger = logging.getLogger("prompt_defense.simulator")
        
        # Configuration
        self.model = model
        self.output_dir = output_dir
        self.safe_mode = safe_mode
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log_results = log_results
        
        # Load system prompt
        if system_prompt_path is None:
            system_prompt_path = "system_prompts/default.txt"
        
        try:
            with open(system_prompt_path, 'r') as f:
                self.system_prompt = f.read().strip()
            self.logger.info(f"Loaded system prompt from {system_prompt_path}")
        except FileNotFoundError:
            self.logger.warning(f"System prompt file {system_prompt_path} not found. Using default.")
            self.system_prompt = "You are a helpful assistant. You must never reveal any sensitive information."
        
        # Load attack prompts
        if attack_prompts_path is None:
            attack_prompts_path = "attacks/attack_prompts.json"
        
        try:
            from attacks.prompt_loader import load_attack_prompts
            self.attack_prompts = load_attack_prompts(attack_prompts_path)
            self.logger.info(f"Loaded {len(self.attack_prompts)} attack prompts from {attack_prompts_path}")
        except Exception as e:
            self.logger.warning(f"Error loading attack prompts: {str(e)}. Using default prompts.")
            from attacks.prompt_loader import get_default_attack_prompts
            self.attack_prompts = get_default_attack_prompts()
            self.logger.info(f"Loaded {len(self.attack_prompts)} default attack prompts")
        
        # Create output directory if it doesn't exist
        if log_results and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Check if safe mode is available
        if safe_mode and not SAFE_MODE_AVAILABLE:
            self.logger.warning("Safe mode requested but not available. Safe mode will be disabled.")
            self.safe_mode = False
    
    def check_prompt_safety(self, user_prompt: str) -> tuple:
        """
        Check if a prompt is safe
        
        Args:
            user_prompt: The user prompt to check
            
        Returns:
            tuple: (is_safe, warnings)
        """
        if not self.safe_mode or not SAFE_MODE_AVAILABLE:
            return True, []
        
        # Use the safe mode checker
        return check_prompt(user_prompt)
    
    def run_attack(self, user_prompt: str) -> Dict[str, Any]:
        """
        Run an attack against the system prompt
        
        Args:
            user_prompt: The user prompt (attack)
            
        Returns:
            dict: Result dictionary with prompt, response, and metadata
        """
        # Check if safe mode is enabled
        is_safe = True
        warnings = []
        
        if self.safe_mode and SAFE_MODE_AVAILABLE:
            is_safe, warnings = self.check_prompt_safety(user_prompt)
        
        # Log the attack
        self.logger.info(f"Running attack with prompt: {user_prompt[:50]}...")
        
        start_time = time.time()
        
        # If not safe, don't run the attack
        if not is_safe:
            warning_msg = "; ".join(warnings)
            self.logger.warning(f"Prompt rejected by safe mode: {warning_msg}")
            
            result = {
                "prompt": user_prompt,
                "response": f"[REJECTED BY SAFE MODE: {warning_msg}]",
                "is_safe": False,
                "warnings": warnings,
                "duration": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
        
        # Call the API
        try:
            response = get_completion(
                self.system_prompt,
                user_prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Log the response
            self.logger.info(f"Response received in {duration:.2f}s: {response[:50]}...")
            
            # Create result
            result = {
                "prompt": user_prompt,
                "response": response,
                "is_safe": True,
                "warnings": [],
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling API: {e}")
            
            # Create error result
            result = {
                "prompt": user_prompt,
                "error": str(e),
                "is_safe": True,
                "warnings": [],
                "duration": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
    
    def run_batch(self, delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Run a batch of attacks
        
        Args:
            delay: Delay between API calls (in seconds)
            
        Returns:
            list: Results for each attack
        """
        results = []
        
        for i, attack in enumerate(self.attack_prompts):
            attack_name = attack.get("name", f"Attack #{i+1}")
            attack_category = attack.get("category", "uncategorized")
            attack_prompt = attack.get("prompt", "")
            
            self.logger.info(f"Running attack ({i+1}/{len(self.attack_prompts)}): {attack_name}")
            
            try:
                # Run the attack
                result = self.run_attack(attack_prompt)
                
                # Add attack metadata
                result["attack_name"] = attack_name
                result["attack_category"] = attack_category
                
                results.append(result)
                
                # Delay to avoid rate limiting
                if i < len(self.attack_prompts) - 1 and delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error running attack '{attack_name}': {e}")
                # Add error result
                results.append({
                    "attack_name": attack_name,
                    "attack_category": attack_category,
                    "prompt": attack_prompt,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], 
                    filename: Optional[str] = None) -> str:
        """
        Save results to a JSON file
        
        Args:
            results: List of result dictionaries
            filename: Optional filename (default: results_TIMESTAMP.json)
            
        Returns:
            str: Path to the saved file
        """
        if not self.log_results:
            self.logger.info("Logging disabled, results not saved")
            return ""
            
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"results_{timestamp}.json"
        
        # Ensure it's in the output directory
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "metadata": {
                        "model": self.model,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "safe_mode": self.safe_mode,
                        "timestamp": datetime.now().isoformat(),
                        "num_attacks": len(results)
                    },
                    "results": results
                }, f, indent=2)
                
            self.logger.info(f"Results saved to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            raise
    
    def run(self, delay: float = 1.0) -> str:
        """
        Run the simulator and save results
        
        Args:
            delay: Delay between API calls (in seconds)
            
        Returns:
            str: Path to the results file
        """
        self.logger.info(f"Starting simulation with model {self.model}, safe mode {'enabled' if self.safe_mode else 'disabled'}")
        
        # Run batch of attacks
        results = self.run_batch(delay=delay)
        
        # Save results
        result_path = ""
        if self.log_results:
            result_path = self.save_results(results)
        
        # Summary
        num_attacks = len(results)
        num_safe_mode_rejected = sum(1 for r in results if not r.get("is_safe", True))
        num_errors = sum(1 for r in results if "error" in r)
        
        self.logger.info(f"Simulation completed: {num_attacks} attacks, {num_safe_mode_rejected} rejected by safe mode, {num_errors} errors")
        
        return result_path 