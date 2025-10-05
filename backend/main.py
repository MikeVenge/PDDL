"""
PDDL RLHF Backend API
FastAPI server for generating PDDL plans and collecting human feedback.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import requests
import os
import json
import re
from datetime import datetime
import uuid

app = FastAPI(title="PDDL RLHF API", version="1.0.0")

# CORS configuration for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
API_KEY = os.getenv("FIREWORKS_API_KEY", "fw_3ZHFp8ZR5WeoadXcFcjEKY4z")
MODEL = "accounts/colin-fbf68a/models/pddl-gpt-oss-model"
SYSTEM_PROMPT = "You are an expert planning assistant. When given a problem, output a structured plan in PDDL format with actions and explanations."
TRAINING_DATA_DIR = "training_data"

# Ensure training data directory exists
os.makedirs(TRAINING_DATA_DIR, exist_ok=True)


# Request/Response Models
class GeneratePlanRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=5000)
    temperature: float = Field(0.5, ge=0.0, le=1.0)
    max_tokens: int = Field(10000, ge=1000, le=20000)


class Step(BaseModel):
    step_id: str
    step_number: int
    step_content: str
    section: Optional[str] = None


class GeneratePlanResponse(BaseModel):
    session_id: str
    prompt: str
    plan_text: str
    steps: List[Step]
    metadata: Dict[str, Any]


class FeedbackItem(BaseModel):
    step_id: str
    step_number: int
    step_content: str
    rating: str = Field(..., pattern="^(positive|negative)$")
    reason: Optional[str] = None

    @validator('reason')
    def validate_reason(cls, v, values):
        if values.get('rating') == 'negative' and (not v or len(v) < 10):
            raise ValueError('Reason is required and must be at least 10 characters for negative ratings')
        return v


class SubmitFeedbackRequest(BaseModel):
    session_id: str
    prompt: str
    plan_text: str
    feedback: List[FeedbackItem]
    metadata: Dict[str, Any]


class SubmitFeedbackResponse(BaseModel):
    success: bool
    dataset: Dict[str, Any]
    file_path: str


# Helper Functions
def parse_steps_from_plan(plan_text: str) -> List[Step]:
    """
    Parse PDDL plan output into discrete steps.
    Handles PDDL action definitions, numbered lists, tables, and action sequences.
    Based on MIT PDDL BlocksWorld format.
    """
    steps = []
    step_counter = 1
    
    # Split into lines for processing
    lines = plan_text.split('\n')
    current_section = None
    
    # PDDL-specific patterns
    # Pattern 1: PDDL action definition (e.g., "(:action action-name" or "(:durative-action action-name")
    pddl_action_start = re.compile(r'^\s*\(:(durative-)?action\s+([a-zA-Z0-9\-_]+)')
    
    # Pattern 2: Numbered steps (e.g., "1:", "1.", "Step 1:", "**1.**", etc.)
    numbered_pattern = re.compile(r'^[\*\s]*(\d+)[\*]*[:\.\)]\s*(.+)$')
    
    # Pattern 3: Action in plan format (e.g., "0: (action-name param1 param2)")
    action_pattern = re.compile(r'^\d+:\s*\(([^)]+)\)\s*;?\s*(.*)$')
    
    # Pattern 4: Section headers (including emoji numbers like 1️⃣)
    section_pattern = re.compile(r'^#+\s*\d*️?⃣?\s*(.+)$')
    
    # Pattern 5: Table rows with pipe separators (handles "| **1. Text** | col2 | col3 |")
    table_row_pattern = re.compile(r'^\|\s*\*?\*?(\d+)[\.\s\*]*([^|]+?)\*?\*?\s*\|([^|]+)\|([^|]+)\|$')
    
    # Pattern 6: Bold numbered items like "**1. Identify companies**"
    bold_numbered_pattern = re.compile(r'^\*\*(\d+)\.\s*([^*]+)\*\*(.*)$')
    
    in_code_block = False
    in_table = False
    in_pddl_action = False
    current_step_content = []
    current_action_name = None
    action_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            # If exiting a code block with PDDL actions, don't reset state yet
            continue
        
        # Skip empty lines outside of content accumulation
        if not stripped and not current_step_content and not in_pddl_action:
            continue
        
        # Detect section headers
        section_match = section_pattern.match(stripped)
        if section_match:
            current_section = section_match.group(1).strip()
            continue
        
        # Detect table separator rows
        if re.match(r'^\|[\s\-:]+\|', stripped):
            in_table = True
            continue
        
        # Skip PDDL action definitions in code blocks - we want the workflow table instead
        # These are technical definitions, not executable steps for humans
        if in_code_block:
            continue
        
        # Pattern 4: Table rows (like "| **1. Identify** | ... | ... |")
        table_match = table_row_pattern.match(stripped)
        if table_match and in_table and not in_code_block:
            step_num = int(table_match.group(1))
            step_title = table_match.group(2).strip()
            col2 = table_match.group(3).strip()
            col3 = table_match.group(4).strip()
            
            # Build comprehensive step content with all information
            step_parts = []
            
            # Title (e.g., "Identify companies")
            if step_title:
                step_parts.append(f"**{step_title}**")
            
            # What to do / Action (column 2)
            if col2 and col2 != step_title:
                step_parts.append(f"\n**What to do:** {col2}")
            
            # Why it matters / Description (column 3)
            if col3:
                step_parts.append(f"\n**Why it matters:** {col3}")
            
            step_text = "\n".join(step_parts)
            
            steps.append(Step(
                step_id=f"step-{step_num}",
                step_number=step_num,
                step_content=step_text.strip(),
                section="Execution Plan"
            ))
            step_counter = max(step_counter, step_num + 1)
            continue
        
        # Pattern 5: Bold numbered items
        bold_match = bold_numbered_pattern.match(stripped)
        if bold_match and not in_code_block:
            if current_step_content:
                steps.append(Step(
                    step_id=f"step-{step_counter - 1}",
                    step_number=step_counter - 1,
                    step_content='\n'.join(current_step_content).strip(),
                    section=current_section
                ))
                current_step_content = []
            
            step_num = int(bold_match.group(1))
            step_title = bold_match.group(2).strip()
            step_extra = bold_match.group(3).strip()
            
            step_text = step_title
            if step_extra:
                step_text += f"\n{step_extra}"
            
            current_step_content = [step_text]
            step_counter = step_num + 1
            continue
        
        # Pattern 1: Regular numbered list items
        numbered_match = numbered_pattern.match(stripped)
        if numbered_match and not in_code_block:
            # Save previous step if exists
            if current_step_content:
                steps.append(Step(
                    step_id=f"step-{step_counter - 1}",
                    step_number=step_counter - 1,
                    step_content='\n'.join(current_step_content).strip(),
                    section=current_section
                ))
                current_step_content = []
            
            step_num = int(numbered_match.group(1))
            step_text = numbered_match.group(2).strip()
            
            # Look ahead for continuation lines
            current_step_content = [step_text]
            step_counter = step_num + 1
        
        # Pattern 2: Action format
        elif action_pattern.match(stripped) and not in_code_block:
            action_match = action_pattern.match(stripped)
            step_num = int(action_match.group(0).split(':')[0])
            action_content = action_match.group(1)
            comment = action_match.group(2)
            
            step_text = f"({action_content})"
            if comment:
                step_text += f" ; {comment}"
            
            steps.append(Step(
                step_id=f"step-{step_num}",
                step_number=step_num,
                step_content=step_text,
                section=current_section or "Plan"
            ))
            step_counter = max(step_counter, step_num + 1)
        
        # Accumulate continuation lines for current step
        elif current_step_content and not table_match and not in_table:
            # Add continuation only if it's not a new pattern
            if not (numbered_match or section_match or bold_match):
                current_step_content.append(stripped)
    
    # Add the last accumulated step
    if current_step_content:
        steps.append(Step(
            step_id=f"step-{step_counter}",
            step_number=step_counter,
            step_content='\n'.join(current_step_content).strip(),
            section=current_section
        ))
    
    return steps


def call_pddl_model(prompt: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    """Call the PDDL model API."""
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
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling PDDL model: {str(e)}")


def extract_pddl_components(plan_text: str) -> Dict[str, str]:
    """
    Extract PDDL domain, problem, and plan components from the output.
    Follows MIT PDDL BlocksWorld standards from llm-as-pddl-formalizer.
    """
    components = {
        "domain": None,
        "problem": None,
        "plan": None,
        "full_text": plan_text
    }
    
    # Extract domain definition
    domain_match = re.search(r'\(define\s+\(domain[^)]*\).*?\n\)', plan_text, re.DOTALL)
    if domain_match:
        components["domain"] = domain_match.group(0)
    
    # Extract problem definition  
    problem_match = re.search(r'\(define\s+\(problem[^)]*\).*?\n\)', plan_text, re.DOTALL)
    if problem_match:
        components["problem"] = problem_match.group(0)
    
    # Extract plan (action sequence)
    plan_match = re.search(r'(?:PLAN:|Executable Plan|3️⃣)(.*?)(?:---|\Z)', plan_text, re.DOTALL)
    if plan_match:
        components["plan"] = plan_match.group(1).strip()
    
    return components


def validate_pddl_syntax(text: str) -> Dict[str, Any]:
    """
    Basic PDDL syntax validation.
    Checks for common PDDL structures based on MIT BlocksWorld format.
    """
    validation = {
        "is_valid_structure": False,
        "has_domain": False,
        "has_problem": False,
        "has_actions": False,
        "has_predicates": False,
        "errors": []
    }
    
    # Check for domain definition
    if re.search(r'\(define\s+\(domain', text, re.IGNORECASE):
        validation["has_domain"] = True
    
    # Check for problem definition
    if re.search(r'\(define\s+\(problem', text, re.IGNORECASE):
        validation["has_problem"] = True
    
    # Check for actions
    if re.search(r':action\s+\w+', text, re.IGNORECASE):
        validation["has_actions"] = True
    
    # Check for predicates
    if re.search(r':predicates|:precondition|:effect', text, re.IGNORECASE):
        validation["has_predicates"] = True
    
    # Overall structure validation
    validation["is_valid_structure"] = (
        validation["has_domain"] or 
        validation["has_problem"] or 
        (validation["has_actions"] and validation["has_predicates"])
    )
    
    # Check for balanced parentheses
    open_count = text.count('(')
    close_count = text.count(')')
    if open_count != close_count:
        validation["errors"].append(f"Unbalanced parentheses: {open_count} open, {close_count} close")
    
    return validation


def generate_rlhf_dataset(
    session_id: str,
    prompt: str,
    plan_text: str,
    feedback: List[FeedbackItem],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate RLHF training dataset from feedback.
    Follows MIT PDDL BlocksWorld format standards from:
    https://github.com/CassieHuang22/llm-as-pddl-formalizer
    """
    
    # Count ratings
    positive_count = sum(1 for f in feedback if f.rating == "positive")
    negative_count = sum(1 for f in feedback if f.rating == "negative")
    total_steps = len(feedback)
    overall_score = positive_count / total_steps if total_steps > 0 else 0
    
    # Extract PDDL components
    pddl_components = extract_pddl_components(plan_text)
    
    # Validate PDDL syntax
    pddl_validation = validate_pddl_syntax(plan_text)
    
    dataset = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dataset_format": "MIT_PDDL_BlocksWorld_RLHF",
        "reference": "https://github.com/CassieHuang22/llm-as-pddl-formalizer",
        "original_prompt": prompt,
        "model_output": plan_text,
        "pddl_structure": {
            "domain_definition": pddl_components["domain"],
            "problem_definition": pddl_components["problem"],
            "plan_sequence": pddl_components["plan"],
            "validation": pddl_validation
        },
        "model_metadata": {
            "model": MODEL,
            "temperature": metadata.get("temperature", 0.5),
            "max_tokens": metadata.get("max_tokens", 10000),
            "prompt_tokens": metadata.get("prompt_tokens"),
            "completion_tokens": metadata.get("completion_tokens"),
            "total_tokens": metadata.get("total_tokens")
        },
        "human_feedback": [
            {
                "step_id": item.step_id,
                "step_number": item.step_number,
                "step_content": item.step_content,
                "rating": item.rating,
                "reason": item.reason,
                "feedback_quality": "detailed" if item.reason and len(item.reason) > 50 else "basic"
            }
            for item in feedback
        ],
        "aggregated_metrics": {
            "total_steps": total_steps,
            "positive_ratings": positive_count,
            "negative_ratings": negative_count,
            "overall_score": round(overall_score, 3),
            "pddl_validity_score": sum([
                1 if pddl_validation["has_domain"] else 0,
                1 if pddl_validation["has_problem"] else 0,
                1 if pddl_validation["has_actions"] else 0,
                1 if pddl_validation["has_predicates"] else 0
            ]) / 4.0
        },
        "training_metadata": {
            "pipeline_type": "llm-as-formalizer",
            "evaluation_method": "human_feedback",
            "domain_type": "general_planning",
            "can_use_for_training": overall_score >= 0.7 and pddl_validation["is_valid_structure"]
        }
    }
    
    return dataset


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "PDDL RLHF API",
        "version": "1.0.0"
    }


@app.post("/api/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    """
    Generate a PDDL plan from a user prompt.
    Calls the AI model and parses the output into steps.
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Call PDDL model
        response = call_pddl_model(request.prompt, request.temperature, request.max_tokens)
        
        # Extract plan text
        plan_text = response['choices'][0]['message']['content']
        
        # Parse into steps
        steps = parse_steps_from_plan(plan_text)
        
        # Prepare metadata
        metadata = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "prompt_tokens": response.get('usage', {}).get('prompt_tokens'),
            "completion_tokens": response.get('usage', {}).get('completion_tokens'),
            "total_tokens": response.get('usage', {}).get('total_tokens'),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return GeneratePlanResponse(
            session_id=session_id,
            prompt=request.prompt,
            plan_text=plan_text,
            steps=steps,
            metadata=metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/submit-feedback", response_model=SubmitFeedbackResponse)
async def submit_feedback(request: SubmitFeedbackRequest):
    """
    Accept human feedback and generate RLHF training dataset.
    Saves the dataset to disk.
    """
    try:
        # Generate RLHF dataset
        dataset = generate_rlhf_dataset(
            request.session_id,
            request.prompt,
            request.plan_text,
            request.feedback,
            request.metadata
        )
        
        # Save to disk
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"rlhf_session_{timestamp}_{request.session_id[:8]}.json"
        file_path = os.path.join(TRAINING_DATA_DIR, filename)
        
        with open(file_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return SubmitFeedbackResponse(
            success=True,
            dataset=dataset,
            file_path=file_path
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")


@app.get("/api/export-dataset/{session_id}")
async def export_dataset(session_id: str, format: str = "json"):
    """
    Export a specific dataset by session ID.
    Supports json, jsonl, and csv formats.
    """
    # Find the file
    matching_files = [f for f in os.listdir(TRAINING_DATA_DIR) if session_id[:8] in f]
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = os.path.join(TRAINING_DATA_DIR, matching_files[0])
    
    with open(file_path, 'r') as f:
        dataset = json.load(f)
    
    if format == "json":
        return dataset
    elif format == "jsonl":
        # Convert to JSONL format
        lines = [json.dumps(dataset)]
        return {"data": "\n".join(lines)}
    elif format == "csv":
        # Simplified CSV format
        raise HTTPException(status_code=501, detail="CSV format not yet implemented")
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, jsonl, or csv")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

