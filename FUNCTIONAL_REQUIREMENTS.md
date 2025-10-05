# Functional Requirements: RLHF System for PDDL Planner

## 1. System Overview

A Reinforcement Learning with Human Feedback (RLHF) system that collects human evaluations of PDDL planning outputs to generate training datasets for model improvement.

### 1.1 Architecture
- **Frontend**: npm-based web application (React/Vue/vanilla JS)
- **Backend**: Python API server (Flask/FastAPI)
- **AI Model**: Fireworks AI PDDL model (existing integration)
- **Data Storage**: Training dataset generation and export

---

## 2. Functional Requirements

### 2.1 User Input & Problem Submission

**FR-2.1.1: Problem Input Interface**
- User shall be able to enter a planning problem via a text input field (textarea)
- Input field shall support multi-line text
- Minimum character limit: 10 characters
- Maximum character limit: 5000 characters
- Input validation shall display error messages for invalid input

**FR-2.1.2: Problem Submission**
- User shall be able to submit the problem via a "Generate Plan" button
- Button shall be disabled during API processing
- Loading indicator shall be displayed during plan generation
- Submission shall trigger backend API call to PDDL model

**FR-2.1.3: Configuration Options (Optional)**
- User may optionally adjust temperature (0.0 - 1.0)
- User may optionally adjust max_tokens (1000 - 20000)
- Default values: temperature=0.5, max_tokens=10000

---

### 2.2 Plan Generation & Display

**FR-2.2.1: API Integration**
- Backend shall call Fireworks AI PDDL model with user prompt
- Backend shall parse the model response
- Backend shall extract individual steps/actions from the plan
- Backend shall return structured JSON with:
  - Original prompt
  - Generated plan text
  - Parsed steps array
  - Metadata (tokens used, timestamp)

**FR-2.2.2: Step Extraction**
- System shall intelligently parse the PDDL output into discrete steps
- Steps shall be identified from:
  - Numbered lists (e.g., "1:", "2:", "Step 1:", etc.)
  - Action sequences in PDDL plans
  - Sections with clear action descriptions
- Each step shall have:
  - Step ID (unique identifier)
  - Step number/order
  - Step content/description
  - Associated section (if applicable: domain, problem, plan, deliverable)

**FR-2.2.3: Display Generated Plan**
- Full plan text shall be displayed in a readable format
- Steps shall be displayed as individual, clearly separated cards/sections
- Each step card shall show:
  - Step number
  - Step content
  - Feedback controls (Y/N buttons)
  - Reason input field (conditionally visible)

---

### 2.3 Human Feedback Collection

**FR-2.3.1: Step Evaluation Interface**
- Each step shall have two buttons: "Y" (Yes/Good) and "N" (No/Bad)
- Only one option (Y or N) can be selected per step
- Selected option shall be visually highlighted
- User can change selection before submission

**FR-2.3.2: Negative Feedback Elaboration**
- When "N" is selected, a text input field shall appear below the step
- Reason field shall be required when "N" is selected
- Placeholder text: "Please explain what's wrong with this step..."
- Minimum character limit for reason: 10 characters
- Reason field shall hide when user switches back to "Y"

**FR-2.3.3: Feedback Validation**
- System shall track which steps have been evaluated
- Visual indicators shall show:
  - Completed evaluations (green/check)
  - Pending evaluations (grey/pending)
  - Required reasons missing (red/warning)
- Progress indicator: "X of Y steps evaluated"

**FR-2.3.4: Submit Feedback**
- "Submit Feedback" button shall be available at the bottom
- Button shall be disabled until:
  - All steps have been evaluated (Y or N selected)
  - All "N" selections have reasons provided
- Validation errors shall be clearly displayed
- Confirmation message before submission (optional but recommended)

---

### 2.4 Training Dataset Generation

**FR-2.4.1: Dataset Format**
- System shall generate RLHF training data in JSON format
- Dataset structure:
  ```json
  {
    "session_id": "unique-session-id",
    "timestamp": "ISO-8601 timestamp",
    "original_prompt": "user input",
    "model_output": "full model response",
    "model_metadata": {
      "model": "model-name",
      "temperature": 0.5,
      "max_tokens": 10000,
      "prompt_tokens": 160,
      "completion_tokens": 2613
    },
    "feedback": [
      {
        "step_id": "step-1",
        "step_number": 1,
        "step_content": "...",
        "rating": "positive|negative",
        "reason": "optional reason if negative"
      }
    ],
    "aggregated_metrics": {
      "total_steps": 12,
      "positive_ratings": 10,
      "negative_ratings": 2,
      "overall_score": 0.833
    }
  }
  ```

**FR-2.4.2: Alternative Dataset Formats**
- System shall support multiple export formats:
  - JSON (primary)
  - JSONL (one record per line for training)
  - CSV (flattened format)
- Each format shall preserve all feedback data

**FR-2.4.3: Dataset Display**
- Generated dataset shall be displayed in a separate section/panel
- Display options:
  - Formatted JSON with syntax highlighting
  - Collapsible sections for readability
  - Copy to clipboard button
  - Download button for each format

---

### 2.5 Data Persistence & Export

**FR-2.5.1: Dataset Storage**
- Backend shall save each feedback session to disk
- Filename format: `rlhf_session_{timestamp}_{session_id}.json`
- Storage location: `./training_data/` directory
- System shall create directory if it doesn't exist

**FR-2.5.2: Dataset Export**
- User shall be able to download the dataset
- Download formats: JSON, JSONL, CSV
- Filename shall include timestamp for easy tracking
- Frontend shall handle file download via browser

**FR-2.5.3: Session History (Optional - Future Enhancement)**
- System may maintain a list of past feedback sessions
- User may view/export historical sessions
- Bulk export of all sessions in a single file

---

### 2.6 User Experience & Interface

**FR-2.6.1: Responsive Design**
- UI shall be responsive and work on desktop browsers
- Minimum supported resolution: 1024x768
- Mobile support: optional but recommended

**FR-2.6.2: Visual Feedback**
- Loading states for all async operations
- Success/error messages for all actions
- Toast notifications for important events
- Clear visual hierarchy

**FR-2.6.3: Error Handling**
- API errors shall display user-friendly messages
- Network errors shall suggest retry
- Validation errors shall highlight specific fields
- System shall not crash on errors

**FR-2.6.4: Accessibility**
- Proper semantic HTML
- Keyboard navigation support
- ARIA labels for interactive elements
- Sufficient color contrast

---

### 2.7 Backend API Endpoints

**FR-2.7.1: Generate Plan Endpoint**
- **Method**: POST
- **Path**: `/api/generate-plan`
- **Request Body**:
  ```json
  {
    "prompt": "string (required)",
    "temperature": 0.5,
    "max_tokens": 10000
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "string",
    "prompt": "string",
    "plan_text": "string",
    "steps": [array of parsed steps],
    "metadata": {object}
  }
  ```
- **Status Codes**: 200 (success), 400 (validation), 500 (server error)

**FR-2.7.2: Submit Feedback Endpoint**
- **Method**: POST
- **Path**: `/api/submit-feedback`
- **Request Body**:
  ```json
  {
    "session_id": "string",
    "prompt": "string",
    "plan_text": "string",
    "feedback": [array of feedback objects],
    "metadata": {object}
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "dataset": {generated dataset object},
    "file_path": "string"
  }
  ```
- **Status Codes**: 200 (success), 400 (validation), 500 (server error)

**FR-2.7.3: Export Dataset Endpoint (Optional)**
- **Method**: GET
- **Path**: `/api/export-dataset/{session_id}`
- **Query Params**: `format=json|jsonl|csv`
- **Response**: File download
- **Status Codes**: 200 (success), 404 (not found)

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Plan generation shall complete within 30 seconds (API dependent)
- UI shall remain responsive during API calls
- Dataset generation shall complete within 1 second

### 3.2 Security
- API key shall be stored securely in backend environment variables
- No sensitive data in frontend code
- Input sanitization to prevent injection attacks
- CORS configuration for frontend-backend communication

### 3.3 Reliability
- System shall handle API failures gracefully
- Feedback data shall not be lost on error
- Auto-save draft feedback (optional enhancement)

### 3.4 Maintainability
- Code shall follow language-specific best practices
- Clear separation of concerns (frontend/backend)
- Comprehensive error logging
- Documentation for setup and deployment

---

## 4. User Workflow

```
1. User enters planning problem in text area
   ↓
2. User clicks "Generate Plan"
   ↓
3. System calls PDDL model API
   ↓
4. System parses response into steps
   ↓
5. System displays plan with step-by-step cards
   ↓
6. User evaluates each step (Y or N)
   ↓
7. For N ratings, user provides reason
   ↓
8. System validates all feedback is complete
   ↓
9. User clicks "Submit Feedback"
   ↓
10. System generates RLHF training dataset
    ↓
11. System displays formatted dataset
    ↓
12. User can copy or download dataset
    ↓
13. System saves dataset to training_data/ directory
```

---

## 5. Future Enhancements (Out of Scope for MVP)

- **Multi-session comparison**: Compare feedback across multiple sessions
- **Analytics dashboard**: Visualize feedback trends and model performance
- **Collaborative feedback**: Multiple users providing feedback on same plan
- **Real-time collaboration**: Live feedback with multiple evaluators
- **Advanced step editing**: Allow users to suggest improved step text
- **Batch processing**: Upload multiple prompts for evaluation
- **Model fine-tuning**: Automated retraining pipeline with collected data
- **A/B testing**: Compare outputs from different model versions
- **Feedback templates**: Pre-defined reason categories for faster input

---

## 6. Technical Stack Recommendations

### Frontend
- **Framework**: React (with Vite) or Vue.js 3
- **UI Library**: Tailwind CSS or Material-UI
- **HTTP Client**: Axios or Fetch API
- **State Management**: React Context API or Zustand (for React)

### Backend
- **Framework**: FastAPI (recommended) or Flask
- **CORS**: fastapi-cors or flask-cors
- **Environment**: python-dotenv for config
- **Validation**: Pydantic (FastAPI) or marshmallow (Flask)

### Development Tools
- **Package Manager**: npm/pnpm (frontend), pip/poetry (backend)
- **Linting**: ESLint (frontend), pylint/black (backend)
- **Testing**: Jest (frontend), pytest (backend)

---

## 7. Development Phases

### Phase 1: Backend API (Core)
- Set up Python backend with FastAPI/Flask
- Implement `/api/generate-plan` endpoint
- Implement step parsing logic
- Test API with curl/Postman

### Phase 2: Frontend UI (Core)
- Set up npm project with React/Vue
- Create input form and plan generation UI
- Display parsed steps
- Implement feedback collection UI

### Phase 3: Dataset Generation (Core)
- Implement `/api/submit-feedback` endpoint
- Generate RLHF training dataset
- Display dataset on frontend
- Save to disk

### Phase 4: Polish & Enhancement
- Add export functionality
- Improve error handling
- Add validation and user feedback
- Style and UX improvements
- Testing and bug fixes

---

## 8. Success Criteria

The system will be considered successful when:
1. ✅ User can input a problem and generate a plan
2. ✅ All steps are clearly displayed and parseable
3. ✅ User can provide Y/N feedback on each step
4. ✅ User can provide reasons for negative feedback
5. ✅ System validates feedback completion
6. ✅ RLHF training dataset is generated correctly
7. ✅ Dataset is displayed and downloadable
8. ✅ Data is persisted to disk
9. ✅ System handles errors gracefully
10. ✅ UI is intuitive and responsive

---

## 9. Open Questions & Decisions Needed

1. **Frontend Framework**: React, Vue, or vanilla JS?
2. **Backend Framework**: FastAPI or Flask?
3. **Step Parsing Strategy**: How to handle various PDDL output formats?
   - Should we parse PDDL syntax specifically?
   - Should we use regex for numbered lists?
   - Should we use LLM to parse the output into steps?
4. **Dataset Schema**: Should we follow a specific RLHF format (e.g., OpenAI's format)?
5. **Authentication**: Do we need user accounts or is it single-user?
6. **Deployment**: Local development only or production deployment needed?

---

**Document Version**: 1.0  
**Last Updated**: October 5, 2025  
**Status**: Draft - Awaiting User Approval

