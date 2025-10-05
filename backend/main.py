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
    Handles multiple formats:
    1. PDDL action blocks with ; Action: headers
    2. Numbered sections (## 1. Title)
    3. Table rows with steps
    4. Simple numbered lists
    """
    steps = []
    step_counter = 1
    
    # Try Strategy 1: Extract PDDL action blocks from code blocks
    pddl_actions = extract_pddl_actions(plan_text)
    if pddl_actions:
        return pddl_actions
    
    # Try Strategy 2: Extract numbered sections (## N.)
    numbered_sections = extract_numbered_sections(plan_text)
    if numbered_sections:
        return numbered_sections
    
    # Try Strategy 3: Extract from workflow tables
    table_steps = extract_table_steps(plan_text)
    if table_steps:
        return table_steps
    
    # Try Strategy 4: Simple numbered list extraction
    numbered_list = extract_numbered_list(plan_text)
    if numbered_list:
        return numbered_list
    
    # Fallback: Return the whole text as one step
    return [Step(
        step_id="step-1",
        step_number=1,
        step_content=plan_text,
        section="Complete Plan"
    )]


def extract_pddl_actions(plan_text: str) -> List[Step]:
    """Extract PDDL action blocks from ```pddl or ```lisp code blocks with explanations."""
    steps = []
    step_counter = 1
    lines = plan_text.split('\n')
    
    in_code_block = False
    code_block_end = -1
    action_names = []
    action_contents = {}
    
    # First pass: Extract all PDDL actions from code blocks
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track code blocks (pddl or lisp)
        if stripped.startswith('```'):
            if 'pddl' in stripped.lower() or 'lisp' in stripped.lower():
                in_code_block = True
            elif in_code_block:
                in_code_block = False
                code_block_end = i
            continue
        
        if not in_code_block:
            continue
        
        # Look for (:action definitions directly
        if '(:action' in line:
            # Extract action name (handle both regular and non-breaking hyphens)
            action_name_match = re.search(r'\(:action\s+([\w\-\u2011]+)', line)
            if action_name_match:
                action_name = action_name_match.group(1)
                action_names.append(action_name)
                
                # Found an action! Collect it
                action_lines = []
                
                # Look backwards for any comment that might describe this action
                for j in range(max(0, i-3), i):
                    if lines[j].strip().startswith(';'):
                        action_lines.append(lines[j])
                
                # Add the action line itself
                action_lines.append(line)
                paren_depth = line.count('(') - line.count(')')
                
                # Continue collecting lines until parentheses balance
                j = i + 1
                while j < len(lines) and paren_depth > 0:
                    action_lines.append(lines[j])
                    paren_depth += lines[j].count('(') - lines[j].count(')')
                    j += 1
                
                # Look for explanation comment after the action
                while j < len(lines) and lines[j].strip().startswith(';'):
                    action_lines.append(lines[j])
                    j += 1
                
                # Save this action
                action_text = '\n'.join(action_lines).strip()
                if action_text:
                    action_contents[action_name] = action_text
    
    # Second pass: Look for explanations after the code block
    explanations = {}
    if code_block_end > 0:
        # Look for the "Explanation of the plan" section
        for i in range(code_block_end, len(lines)):
            line = lines[i]
            # Check for numbered list items that match our action names
            for action_name in action_names:
                # Match patterns like "1. **Collect SEC filings**" or "1. Collect SEC filings"
                # Convert hyphenated action names to match various formats
                readable_name = action_name.replace('-', ' ').title()
                
                patterns = [
                    rf'\d+\.\s*\*\*.*{re.escape(readable_name)}.*\*\*',
                    rf'\d+\.\s*{re.escape(readable_name)}',
                    rf'\d+\.\s*\*\*.*{re.escape(action_name)}.*\*\*',
                    rf'\d+\.\s*{re.escape(action_name)}'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Found explanation for this action
                        explanation_lines = [line]
                        # Collect the explanation text (usually follows with a dash or colon)
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j].strip()
                            # Stop if we hit the next numbered item
                            if re.match(r'^\d+\.', next_line):
                                break
                            # Include lines that are part of the explanation
                            if next_line.startswith(('–', '-', '*', '•')) or next_line == '' or (j == i + 1):
                                if next_line:
                                    explanation_lines.append(lines[j])
                                j += 1
                            else:
                                break
                        
                        explanations[action_name] = '\n'.join(explanation_lines)
                        break
    
    # Combine PDDL code with explanations
    for action_name in action_names:
        if action_name in action_contents:
            step_content = action_contents[action_name]
            
            # Add explanation if available
            if action_name in explanations:
                step_content += "\n\n**Explanation:**\n" + explanations[action_name]
            
            steps.append(Step(
                step_id=f"step-{step_counter}",
                step_number=step_counter,
                step_content=step_content,
                section=f"PDDL Action: {action_name}"
            ))
            step_counter += 1
    
    return steps


def extract_numbered_sections(plan_text: str) -> List[Step]:
    """Extract complete numbered sections like ## 1. Title."""
    steps = []
    section_pattern = re.compile(r'^##\s*(\d+)[\.\s️⃣]+(.+)$')
    lines = plan_text.split('\n')
    
    current_num = None
    current_title = None
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        match = section_pattern.match(stripped)
        
        if match:
            if current_num and current_lines:
                content = '\n'.join(current_lines).strip()
                steps.append(Step(
                    step_id=f"step-{current_num}",
                    step_number=current_num,
                    step_content=f"## {current_num}. {current_title}\n\n{content}",
                    section=current_title
                ))
            
            current_num = int(match.group(1))
            current_title = match.group(2).strip()
            current_lines = []
        elif current_num and not (stripped.startswith('##') and not match):
            current_lines.append(line.rstrip())
    
    if current_num and current_lines:
        content = '\n'.join(current_lines).strip()
        steps.append(Step(
            step_id=f"step-{current_num}",
            step_number=current_num,
            step_content=f"## {current_num}. {current_title}\n\n{content}",
            section=current_title
        ))
    
    return steps


def extract_table_steps(plan_text: str) -> List[Step]:
    """Extract steps from markdown tables."""
    steps = []
    table_row = re.compile(r'^\|\s*\*?\*?(\d+)[\.\s\*]*([^|]+?)\*?\*?\s*\|([^|]+)\|([^|]+)\|$')
    lines = plan_text.split('\n')
    in_table = False
    
    for line in lines:
        if re.match(r'^\|[\s\-:]+\|', line.strip()):
            in_table = True
            continue
        
        if in_table:
            match = table_row.match(line)
            if match:
                num = int(match.group(1))
                title = match.group(2).strip()
                col2 = match.group(3).strip()
                col3 = match.group(4).strip()
                
                content = f"**{title}**\n\n**What to do:** {col2}\n\n**Why it matters:** {col3}"
                steps.append(Step(
                    step_id=f"step-{num}",
                    step_number=num,
                    step_content=content,
                    section="Workflow"
                ))
    
    return steps


def extract_numbered_list(plan_text: str) -> List[Step]:
    """Extract simple numbered list items."""
    steps = []
    numbered = re.compile(r'^(\d+)[\.\:\)]\s+(.+)$')
    lines = plan_text.split('\n')
    
    for line in lines:
        match = numbered.match(line.strip())
        if match:
            num = int(match.group(1))
            content = match.group(2).strip()
            steps.append(Step(
                step_id=f"step-{num}",
                step_number=num,
                step_content=content,
                section="Steps"
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

