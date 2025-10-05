# 🏗️ MIT PDDL Integration Architecture

## System Architecture with MIT Standards

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE (React)                          │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Input Form │  │ Step Cards │  │  Feedback  │  │  Dataset   │       │
│  │            │  │            │  │ Collection │  │  Display   │       │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘       │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼ HTTP/REST API
┌─────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              POST /api/generate-plan                              │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │  1. Receive user prompt                                     │  │  │
│  │  │  2. Call Fireworks AI PDDL Model ───────────────────┐       │  │  │
│  │  │  3. Receive PDDL output                             │       │  │  │
│  │  │  4. Parse steps with parse_steps_from_plan()        │       │  │  │
│  │  │  5. Return structured JSON                          │       │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              POST /api/submit-feedback                            │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │  MIT PDDL INTEGRATION PIPELINE                             │  │  │
│  │  │                                                             │  │  │
│  │  │  ┌───────────────────────────────────────────────────────┐ │  │  │
│  │  │  │ 1. extract_pddl_components()                          │ │  │  │
│  │  │  │    ├─ Extract domain: (define (domain ...))           │ │  │  │
│  │  │  │    ├─ Extract problem: (define (problem ...))         │ │  │  │
│  │  │  │    └─ Extract plan: 0: (action ...) 1: (action ...)   │ │  │  │
│  │  │  └───────────────────────────────────────────────────────┘ │  │  │
│  │  │                          ▼                                  │  │  │
│  │  │  ┌───────────────────────────────────────────────────────┐ │  │  │
│  │  │  │ 2. validate_pddl_syntax()                             │ │  │  │
│  │  │  │    ├─ Check domain definition                         │ │  │  │
│  │  │  │    ├─ Check problem definition                        │ │  │  │
│  │  │  │    ├─ Check actions (:action)                         │ │  │  │
│  │  │  │    ├─ Check predicates (:predicates, :precondition)   │ │  │  │
│  │  │  │    └─ Validate parentheses balance                    │ │  │  │
│  │  │  └───────────────────────────────────────────────────────┘ │  │  │
│  │  │                          ▼                                  │  │  │
│  │  │  ┌───────────────────────────────────────────────────────┐ │  │  │
│  │  │  │ 3. generate_rlhf_dataset()                            │ │  │  │
│  │  │  │    ├─ Collect human feedback                          │ │  │  │
│  │  │  │    ├─ Calculate metrics (positive/negative ratings)   │ │  │  │
│  │  │  │    ├─ Calculate PDDL validity score                   │ │  │  │
│  │  │  │    ├─ Determine training suitability                  │ │  │  │
│  │  │  │    └─ Format MIT PDDL BlocksWorld structure           │ │  │  │
│  │  │  └───────────────────────────────────────────────────────┘ │  │  │
│  │  │                          ▼                                  │  │  │
│  │  │  ┌───────────────────────────────────────────────────────┐ │  │  │
│  │  │  │ 4. Save to training_data/                             │ │  │  │
│  │  │  │    └─ rlhf_session_YYYYMMDD_HHMMSS_uuid.json          │ │  │  │
│  │  │  └───────────────────────────────────────────────────────┘ │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Fireworks AI PDDL Model     │
                     │  (External API)              │
                     └──────────────────────────────┘
```

---

## Data Flow: MIT PDDL Format

```
User Input                   AI Model Output                 MIT PDDL Dataset
─────────────────           ───────────────────────         ─────────────────

"I have 3 blocks         →  Domain Definition:            →  {
A, B, C. A is on             (define (domain                   "dataset_format":
table, B on A,                blocksworld)                       "MIT_PDDL_BlocksWorld_RLHF",
C on B. I want               (:action unstack ...)            
C on table, B on           Problem Definition:                "pddl_structure": {
C, A on B."                  (define (problem                    "domain_definition": "...",
                               blocks-3-0)                      "problem_definition": "...",
                             Plan Sequence:                     "plan_sequence": "...",
                               0: (unstack C B)                 "validation": {
                               1: (putdown C)                     "is_valid_structure": true,
                               2: (unstack B A)                   "has_domain": true,
                               3: (stack B C)                     "has_actions": true,
                               4: (pickup A)                      ...
                               5: (stack A B)                   }
                                                              },
    ↓                          ↓                              
                                                              "human_feedback": [
Human Feedback             Validation Results                  {
─────────────────          ──────────────────                    "step_id": "step-1",
Step 1: 👍                 ✅ Domain: found                      "rating": "positive",
Step 2: 👍                 ✅ Problem: found                     ...
Step 3: 👎                 ✅ Actions: found                   },
  "Should check            ✅ Predicates: found                  {
   preconditions"          ✅ Syntax: valid                      "step_id": "step-3",
Step 4: 👍                                                       "rating": "negative",
Step 5: 👍                 PDDL Validity: 1.0                   "reason": "Should check...",
Step 6: 👍                 Overall Score: 0.833                 "feedback_quality": "detailed"
                           Can Use: true                        }
                                                              ],
                                                              
                                                              "aggregated_metrics": {
                                                                "pddl_validity_score": 1.0,
                                                                "overall_score": 0.833
                                                              },
                                                              
                                                              "training_metadata": {
                                                                "can_use_for_training": true
                                                              }
                                                            }
```

---

## MIT PDDL Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    PDDL Plan Output                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Domain Definition                                       │    │
│  │ ─────────────────                                       │    │
│  │ (define (domain blocksworld)                           │    │
│  │   (:requirements :strips)                              │    │
│  │   (:predicates (on ?x ?y) (clear ?x) ...)             │    │
│  │   (:action pickup ... )                                │    │
│  │   (:action unstack ... )                               │    │
│  │   (:action putdown ... )                               │    │
│  │   (:action stack ... )                                 │    │
│  │ )                                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                         ▼ extract_pddl_components()             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Problem Definition                                      │    │
│  │ ──────────────────                                      │    │
│  │ (define (problem blocks-3-0)                           │    │
│  │   (:domain blocksworld)                                │    │
│  │   (:objects A B C - block)                             │    │
│  │   (:init (on A table) (on B A) (on C B) ...)          │    │
│  │   (:goal (and (on C table) (on B C) (on A B)))        │    │
│  │ )                                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                         ▼ validate_pddl_syntax()                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Plan Sequence                                           │    │
│  │ ─────────────                                           │    │
│  │ 0: (unstack C B)  ; Remove C from B                    │    │
│  │ 1: (putdown C)    ; Place C on table                   │    │
│  │ 2: (unstack B A)  ; Remove B from A                    │    │
│  │ 3: (stack B C)    ; Place B on C                       │    │
│  │ 4: (pickup A)     ; Pick up A from table               │    │
│  │ 5: (stack A B)    ; Place A on B                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Validation Results                                      │    │
│  │ ──────────────────                                      │    │
│  │ ✅ has_domain: true                                    │    │
│  │ ✅ has_problem: true                                   │    │
│  │ ✅ has_actions: true                                   │    │
│  │ ✅ has_predicates: true                                │    │
│  │ ✅ balanced_parens: true                               │    │
│  │ ─────────────────                                       │    │
│  │ PDDL Validity Score: 1.0                               │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Training Suitability Decision Tree

```
                    ┌─────────────────────┐
                    │  Generated Dataset  │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │  Calculate Overall Score       │
              │  (positive / total feedback)   │
              └────────────┬───────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         Score >= 0.7          Score < 0.7
                │                     │
                ▼                     ▼
    ┌───────────────────┐     ┌─────────────────┐
    │ Check PDDL Valid  │     │ can_use_for_    │
    └─────────┬─────────┘     │ training: FALSE │
              │               └─────────────────┘
     ┌────────┴────────┐
     │                 │
     ▼                 ▼
  Valid            Invalid
     │                 │
     ▼                 ▼
┌─────────────┐  ┌─────────────────┐
│ can_use_for │  │ can_use_for_    │
│ training:   │  │ training: FALSE │
│ TRUE ✅     │  └─────────────────┘
└─────────────┘

Legend:
  Overall Score >= 0.7    = 70%+ positive human feedback
  PDDL Valid = true       = Valid PDDL structure detected
  can_use_for_training    = Dataset suitable for model training
```

---

## MIT Repository Compatibility

```
┌──────────────────────────────────────────────────────────────────┐
│            MIT llm-as-pddl-formalizer Repository                 │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ BlocksWorld│  │  Barman    │  │ Logistics  │  │ Mystery  │ │
│  │ -100       │  │  -100      │  │ -100       │  │ Blocks   │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                  │
│  Ground Truth PDDL + Textual Descriptions                       │
│                                                                  │
│  Evaluation Pipeline:                                           │
│  ├─ LLM-as-Formalizer                                          │
│  ├─ LLM-as-Planner                                             │
│  └─ VAL Validator                                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Compatible Format
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              Our RLHF System (Enhanced)                          │
│                                                                  │
│  Same Format:                                                   │
│  ├─ Domain/Problem/Plan structure                              │
│  ├─ PDDL syntax validation                                     │
│  └─ Compatible with VAL                                        │
│                                                                  │
│  Additional Features:                                           │
│  ├─ Human feedback collection                                  │
│  ├─ RLHF dataset generation                                    │
│  ├─ Quality scoring                                            │
│  └─ Training suitability flags                                 │
└──────────────────────────────────────────────────────────────────┘
                             │
                             │ Can Export To
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              Standard PDDL Files                                 │
│                                                                  │
│  domain.pddl    ← Domain definition                             │
│  problem.pddl   ← Problem instance                              │
│  plan.txt       ← Action sequence                               │
│                                                                  │
│  └─ Usable with: VAL, Fast Downward, other planners            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Dataset Quality Metrics

```
┌─────────────────────────────────────────────────────────────┐
│                    Quality Dimensions                        │
└─────────────────────────────────────────────────────────────┘

1. Human Feedback Quality (Overall Score)
   ────────────────────────────────────────
   
   Positive Ratings
   ──────────────── = Overall Score
   Total Steps
   
   Example: 10 positive / 12 total = 0.833 (83.3%)

2. PDDL Structure Quality (PDDL Validity Score)
   ─────────────────────────────────────────────
   
   Points Awarded:
   • Has domain definition     → +0.25
   • Has problem definition    → +0.25
   • Has action definitions    → +0.25
   • Has predicates/effects    → +0.25
   ────────────────────────────────
   Total Score: 0.0 - 1.0

3. Feedback Detail Quality
   ────────────────────────
   
   Feedback Length:
   • > 50 chars    → "detailed"
   • ≤ 50 chars    → "basic"

4. Training Suitability (Boolean)
   ───────────────────────────────
   
   can_use_for_training = 
     (overall_score >= 0.7) AND 
     (pddl_validation.is_valid_structure == True)

┌─────────────────────────────────────────────────────────────┐
│                    Quality Ranges                            │
├─────────────────────────────────────────────────────────────┤
│  Excellent  │ Overall: 0.9-1.0 │ PDDL: 1.0  │ ✅ Use       │
│  Good       │ Overall: 0.7-0.9 │ PDDL: 0.75+│ ✅ Use       │
│  Fair       │ Overall: 0.5-0.7 │ PDDL: 0.5+ │ ⚠️  Review   │
│  Poor       │ Overall: < 0.5   │ PDDL: < 0.5│ ❌ Don't Use │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Summary

### ✅ What We Integrated

1. **MIT PDDL Structure**
   - Domain/Problem/Plan extraction
   - Follows BlocksWorld format
   - Compatible with academic tools

2. **Validation System**
   - PDDL syntax checking
   - Structure validation
   - Error detection

3. **Quality Metrics**
   - Human feedback scoring
   - PDDL validity scoring
   - Training suitability flags

4. **Documentation**
   - References to MIT repository
   - Dataset format specifications
   - Compatibility notes

### 🎯 Why It Matters

- **Academic Use**: Compatible with research standards
- **Tool Integration**: Works with VAL, Fast Downward
- **Quality Control**: Automatic filtering of bad examples
- **Reproducibility**: Standard format enables comparison

---

*Architecture follows [MIT llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer) standards*

