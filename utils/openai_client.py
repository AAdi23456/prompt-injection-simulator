"""
OpenAI API client for Prompt Defense Simulator.

This module provides functions for interacting with the OpenAI API.
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("prompt_defense.openai")

# Check for API key in a way that allows for mocking in tests
api_key = os.getenv("OPENAI_API_KEY")
if not api_key and not os.environ.get("PYTEST_CURRENT_TEST"):
    logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    # Don't raise error immediately to allow for test mocking

def get_completion(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=500):
    """
    Get a completion from the OpenAI API
    
    Args:
        system_prompt: The system prompt to use
        user_prompt: The user prompt (attack)
        model: The model to use (default: gpt-3.5-turbo)
        temperature: The temperature (default: 0.7)
        max_tokens: Maximum tokens in response (default: 500)
        
    Returns:
        str: The model's response text
    """
    try:
        # Check API key before making the call
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            
        logger.debug(f"Calling OpenAI API with model: {model}")
        
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API using the new format
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        return response_content
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise 