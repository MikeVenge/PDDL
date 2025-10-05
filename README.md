# PDDL Planner CLI

A simple command-line tool to interact with the PDDL model via Fireworks AI API.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x pddl_planner.py
```

## Usage

### Basic Usage

Pass your planning problem directly as a command-line argument:

```bash
python pddl_planner.py "I have $10,000 to invest. I want to build a diversified portfolio with stocks, bonds, and keep some cash reserve. My goal is moderate risk with long-term growth. Create a step-by-step investment plan."
```

### Interactive Mode

Run in interactive mode to enter multi-line prompts:

```bash
python pddl_planner.py --interactive
```

Or simply:

```bash
python pddl_planner.py
```

Then paste or type your prompt, and press `Ctrl+D` (Mac/Linux) or `Ctrl+Z` (Windows) when done.

### Options

- `-i, --interactive`: Run in interactive mode
- `-t, --temperature TEMP`: Set sampling temperature (default: 0.5)
- `-m, --max-tokens NUM`: Set maximum tokens to generate (default: 10000)
- `--raw`: Output raw JSON response instead of formatted output

### Examples

```bash
# Basic usage
python pddl_planner.py "Plan a 7-day vacation to Japan"

# With custom temperature
python pddl_planner.py --temperature 0.7 "Organize a conference with 100 attendees"

# Interactive mode
python pddl_planner.py --interactive

# Raw JSON output
python pddl_planner.py --raw "Create a project plan for building a mobile app"
```

## Features

- ✅ Simple command-line interface
- ✅ Interactive mode for multi-line prompts
- ✅ Formatted output with usage statistics
- ✅ Configurable temperature and max tokens
- ✅ Raw JSON output option
- ✅ Error handling

## API Configuration

The script uses the following defaults:
- **API URL**: `https://api.fireworks.ai/inference/v1/chat/completions`
- **Model**: `accounts/colin-fbf68a/models/pddl-gpt-oss-model`
- **Temperature**: 0.5
- **Max Tokens**: 10000

To use a different API key, edit the `API_KEY` variable in `pddl_planner.py`.

