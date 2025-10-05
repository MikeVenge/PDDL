#!/usr/bin/env python3
"""
PDDL Planner CLI
A simple command-line tool to interact with the PDDL model via Fireworks AI API.
"""

import argparse
import json
import sys
import requests


API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
API_KEY = "fw_3ZHFp8ZR5WeoadXcFcjEKY4z"
MODEL = "accounts/colin-fbf68a/models/pddl-gpt-oss-model"
SYSTEM_PROMPT = "You are an expert planning assistant. When given a problem, output a structured plan in PDDL format with actions and explanations."


def call_pddl_model(user_prompt, temperature=0.5, max_tokens=10000):
    """
    Call the PDDL model API with the given user prompt.
    
    Args:
        user_prompt (str): The user's planning problem
        temperature (float): Sampling temperature (default: 0.5)
        max_tokens (int): Maximum tokens to generate (default: 10000)
    
    Returns:
        dict: The API response
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        sys.exit(1)


def format_output(response):
    """
    Format the API response for terminal output.
    
    Args:
        response (dict): The API response
    """
    try:
        # Extract the assistant's message
        content = response['choices'][0]['message']['content']
        
        # Print separator
        print("\n" + "="*80)
        print("PDDL PLANNING RESULT")
        print("="*80 + "\n")
        
        # Print the content
        print(content)
        
        # Print usage statistics if available
        if 'usage' in response:
            usage = response['usage']
            print("\n" + "-"*80)
            print("USAGE STATISTICS")
            print("-"*80)
            print(f"Prompt tokens:     {usage.get('prompt_tokens', 'N/A')}")
            print(f"Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"Total tokens:      {usage.get('total_tokens', 'N/A')}")
        
        print("\n" + "="*80 + "\n")
        
    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        print("\nRaw response:")
        print(json.dumps(response, indent=2))


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="PDDL Planner CLI - Generate planning solutions using the PDDL model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "I need to organize a conference with 100 attendees"
  %(prog)s --temperature 0.7 "Plan a 7-day trip to Japan"
  %(prog)s --interactive
        """
    )
    
    parser.add_argument(
        'prompt',
        nargs='?',
        help='The planning problem to solve'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode (prompt for input)'
    )
    
    parser.add_argument(
        '-t', '--temperature',
        type=float,
        default=0.5,
        help='Sampling temperature (default: 0.5)'
    )
    
    parser.add_argument(
        '-m', '--max-tokens',
        type=int,
        default=10000,
        help='Maximum tokens to generate (default: 10000)'
    )
    
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Output raw JSON response'
    )
    
    args = parser.parse_args()
    
    # Get the user prompt
    if args.interactive or not args.prompt:
        print("PDDL Planner - Interactive Mode")
        print("-" * 40)
        print("Enter your planning problem (press Ctrl+D or Ctrl+Z when done):\n")
        try:
            user_prompt = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            sys.exit(0)
        
        if not user_prompt:
            print("No input provided.", file=sys.stderr)
            sys.exit(1)
    else:
        user_prompt = args.prompt
    
    # Call the API
    print("Generating plan...", file=sys.stderr)
    response = call_pddl_model(user_prompt, args.temperature, args.max_tokens)
    
    # Format and display the output
    if args.raw:
        print(json.dumps(response, indent=2))
    else:
        format_output(response)


if __name__ == "__main__":
    main()

