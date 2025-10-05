# MIT PDDL BlocksWorld Integration

This document explains how the RLHF system integrates MIT's PDDL BlocksWorld standards from the [llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer) repository.

## 📚 Reference Repository

**GitHub**: [CassieHuang22/llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer)

This repository provides:
- Standard PDDL dataset formats (BlocksWorld, Barman, Logistics, Mystery BlocksWorld)
- Ground truth PDDL files
- Multiple templating levels (heavily templated, moderately templated, natural)
- LLM-as-Formalizer and LLM-as-Planner pipelines
- VAL-based evaluation methods

---

## 🎯 Integration Features

Our RLHF system now incorporates MIT PDDL standards in the following ways:

### 1. **PDDL Structure Extraction**

The backend automatically extracts and validates three key PDDL components:

```python
pddl_structure = {
    "domain_definition": "(define (domain ...)",  # Domain with actions, predicates
    "problem_definition": "(define (problem ...)", # Problem with objects, init, goal
    "plan_sequence": "0: (action1 ...) 1: (action2 ...)", # Executable plan
    "validation": {...}  # Syntax validation results
}
```

### 2. **PDDL Syntax Validation**

Based on MIT BlocksWorld format, the system validates:
- ✅ Domain definition presence
- ✅ Problem definition presence
- ✅ Action definitions (`:action`)
- ✅ Predicates (`:predicates`, `:precondition`, `:effect`)
- ✅ Balanced parentheses
- ✅ Overall PDDL structure validity

### 3. **Enhanced Dataset Format**

The RLHF dataset now includes:

```json
{
  "dataset_format": "MIT_PDDL_BlocksWorld_RLHF",
  "reference": "https://github.com/CassieHuang22/llm-as-pddl-formalizer",
  
  "pddl_structure": {
    "domain_definition": "...",
    "problem_definition": "...",
    "plan_sequence": "...",
    "validation": {
      "is_valid_structure": true,
      "has_domain": true,
      "has_problem": true,
      "has_actions": true,
      "has_predicates": true,
      "errors": []
    }
  },
  
  "aggregated_metrics": {
    "total_steps": 12,
    "positive_ratings": 10,
    "negative_ratings": 2,
    "overall_score": 0.833,
    "pddl_validity_score": 1.0
  },
  
  "training_metadata": {
    "pipeline_type": "llm-as-formalizer",
    "evaluation_method": "human_feedback",
    "domain_type": "general_planning",
    "can_use_for_training": true
  }
}
```

---

## 📊 PDDL Validity Scoring

The system calculates a `pddl_validity_score` (0.0 - 1.0) based on:

| Component | Weight |
|-----------|--------|
| Domain definition present | 0.25 |
| Problem definition present | 0.25 |
| Actions defined | 0.25 |
| Predicates/preconditions/effects | 0.25 |

**Score 1.0** = Complete, valid PDDL structure  
**Score 0.75** = Missing one component  
**Score 0.5** = Missing two components  
**Score < 0.5** = Incomplete PDDL structure

---

## 🎓 Training Data Quality

Datasets are marked as `can_use_for_training: true` when:
1. ✅ `overall_score >= 0.7` (70%+ positive human feedback)
2. ✅ `pddl_validation.is_valid_structure == true` (valid PDDL syntax)

This ensures only high-quality, properly formatted PDDL plans are used for model training.

---

## 🔍 PDDL Component Extraction

### Domain Definition
```lisp
(define (domain blocksworld)
  (:requirements :strips)
  (:predicates
    (on ?x ?y)
    (ontable ?x)
    (clear ?x)
    (handempty)
    (holding ?x))
  (:action pick-up
    :parameters (?x)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (not (ontable ?x)) (not (clear ?x)) 
                 (not (handempty)) (holding ?x)))
  ; ... more actions
)
```

### Problem Definition
```lisp
(define (problem blocks-4-0)
  (:domain blocksworld)
  (:objects a b c d)
  (:init (clear c) (clear d) (ontable a) 
         (ontable b) (on c a) (on d b) (handempty))
  (:goal (and (on d c) (on c b) (on b a)))
)
```

### Plan Sequence
```
0: (pick-up c)       ; Pick up block c
1: (stack c d)       ; Stack c on d
2: (pick-up b)       ; Pick up block b
3: (put-down b)      ; Put b on table
; ... more steps
```

---

## 🧪 Example Dataset

Here's what a complete MIT PDDL-formatted RLHF dataset looks like:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-05T19:30:00.000Z",
  "dataset_format": "MIT_PDDL_BlocksWorld_RLHF",
  "reference": "https://github.com/CassieHuang22/llm-as-pddl-formalizer",
  
  "original_prompt": "I have 4 blocks. Block A is on the table, B is on A, C is on B. I want C on the table, B on C, and A on B.",
  
  "model_output": "(define (domain blocksworld)...)",
  
  "pddl_structure": {
    "domain_definition": "(define (domain blocksworld)...)",
    "problem_definition": "(define (problem blocks-4-0)...)",
    "plan_sequence": "0: (unstack c b)\n1: (put-down c)...",
    "validation": {
      "is_valid_structure": true,
      "has_domain": true,
      "has_problem": true,
      "has_actions": true,
      "has_predicates": true,
      "errors": []
    }
  },
  
  "model_metadata": {
    "model": "accounts/colin-fbf68a/models/pddl-gpt-oss-model",
    "temperature": 0.5,
    "max_tokens": 10000,
    "total_tokens": 2500
  },
  
  "human_feedback": [
    {
      "step_id": "step-1",
      "step_number": 1,
      "step_content": "(unstack c b)",
      "rating": "positive",
      "reason": null,
      "feedback_quality": "basic"
    },
    {
      "step_id": "step-2",
      "step_number": 2,
      "step_content": "(put-down c)",
      "rating": "positive",
      "reason": null,
      "feedback_quality": "basic"
    },
    {
      "step_id": "step-3",
      "step_number": 3,
      "step_content": "(pick-up b)",
      "rating": "negative",
      "reason": "Should unstack B from A first before picking it up, as the precondition requires the block to be on the table",
      "feedback_quality": "detailed"
    }
  ],
  
  "aggregated_metrics": {
    "total_steps": 8,
    "positive_ratings": 6,
    "negative_ratings": 2,
    "overall_score": 0.75,
    "pddl_validity_score": 1.0
  },
  
  "training_metadata": {
    "pipeline_type": "llm-as-formalizer",
    "evaluation_method": "human_feedback",
    "domain_type": "blocksworld",
    "can_use_for_training": true
  }
}
```

---

## 🔄 Compatibility with MIT Dataset

Our RLHF datasets are compatible with the MIT repository's evaluation pipeline:

### 1. Export as PDDL Files

You can extract the domain and problem definitions:

```python
import json

# Load RLHF dataset
with open('rlhf_session_20250105_abc123.json') as f:
    data = json.load(f)

# Save domain
with open('domain.pddl', 'w') as f:
    f.write(data['pddl_structure']['domain_definition'])

# Save problem
with open('p01.pddl', 'w') as f:
    f.write(data['pddl_structure']['problem_definition'])
```

### 2. Run VAL Validator

Follow MIT's evaluation method:

```bash
# Install VAL (follow MIT repo instructions)
validate domain.pddl p01.pddl plan.txt
```

### 3. Compare with Ground Truth

Our datasets can be compared against MIT's ground truth PDDL files for accuracy evaluation.

---

## 📈 Use Cases

### For Model Training
- Filter datasets with `can_use_for_training: true`
- Use `human_feedback` to create preference pairs
- Train reward models based on ratings
- Fine-tune with RLHF/DPO/PPO

### For Evaluation
- Compare `pddl_validity_score` across model versions
- Analyze common error patterns in negative feedback
- Benchmark against MIT ground truth datasets

### For Research
- Study correlation between human feedback and PDDL validity
- Analyze which PDDL components receive negative ratings
- Compare heavily vs. moderately vs. natural templating styles

---

## 🔗 Related MIT Datasets

Our system is designed to work with these MIT PDDL datasets:

| Dataset | Description | Files |
|---------|-------------|-------|
| BlocksWorld-100 | Classic blocks domain | 100 problems |
| Mystery BlocksWorld-100 | Obfuscated blocks domain | 100 problems |
| Barman-100 | Bartending domain | 100 problems |
| Logistics-100 | Transportation domain | 100 problems |

Each with three templating levels:
- **Heavily Templated**: PDDL-like natural language
- **Moderately Templated**: Explicit preconditions/effects
- **Natural**: Human-like descriptions

---

## 🚀 Future Enhancements

Potential MIT PDDL integration improvements:

- [ ] Automatic domain type detection (BlocksWorld, Barman, etc.)
- [ ] VAL validator integration for automatic plan validation
- [ ] Ground truth comparison for accuracy metrics
- [ ] Support for all MIT templating levels
- [ ] Batch import from MIT dataset format
- [ ] Export to MIT-compatible JSONL format
- [ ] Integration with PDDL solvers (Fast Downward, etc.)
- [ ] Visualization of PDDL plans (block stacking diagrams)

---

## 📚 References

1. **MIT Repository**: [llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer)
2. **PDDL Standard**: [planning.wiki](https://planning.wiki/)
3. **VAL Tools**: [VAL GitHub](https://github.com/KCL-Planning/VAL)
4. **Fast Downward**: [Fast Downward Planner](https://www.fast-downward.org/)

---

## ✅ Summary

The RLHF system now:
- ✅ Follows MIT PDDL BlocksWorld standards
- ✅ Extracts domain, problem, and plan components
- ✅ Validates PDDL syntax
- ✅ Calculates PDDL validity scores
- ✅ Flags datasets suitable for training
- ✅ References MIT repository
- ✅ Compatible with MIT evaluation pipeline
- ✅ Includes training metadata for research

**Your RLHF datasets are now research-grade and compatible with academic PDDL evaluation standards!** 🎓

---

*Last Updated: October 5, 2025*  
*Based on: [CassieHuang22/llm-as-pddl-formalizer](https://github.com/CassieHuang22/llm-as-pddl-formalizer)*

