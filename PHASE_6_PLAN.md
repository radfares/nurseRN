# Phase 6: Backend API Layer

**Status:** PLANNED
**Target:** FastAPI REST wrapper around validators & agents
**Effort:** 8-12 hours
**Dependencies:** Phase 5 complete ✅

## API Endpoints

### Project Management
```
POST   /api/projects                    Create project
GET    /api/projects                    List projects
POST   /api/projects/{id}/activate      Switch active project
GET    /api/projects/{id}               Get project details
```

### Validators
```
POST   /api/validators/sample-size      Validate sample size
POST   /api/validators/timeline         Validate timeline
POST   /api/validators/budget           Validate budget
```

### PICOT Scoring
```
POST   /api/picot/score                 Score PICOT question
POST   /api/picot/save                  Save PICOT to database
```

### Agents
```
POST   /api/agents/{name}/run           Run any agent
GET    /api/agents/{name}/status        Check agent status
```

## Tech Stack
```
Framework: FastAPI
Database: SQLite (via project_manager.py)
Server: Uvicorn
Auth: None (local use initially)
```

## Request/Response Format

### Sample Size Validation
```json
POST /api/validators/sample-size
{
  "n": 100,
  "unit_beds": 30,
  "duration_months": 6,
  "effect_size": 0.5
}

Response:
{
  "valid": true,
  "issues": [],
  "execution_time": 0.02
}
```

### PICOT Scoring
```json
POST /api/picot/score
{
  "picot": "In adult patients with diabetes..."
}

Response:
{
  "overall_score": 85,
  "specificity_score": 20,
  "measurability_score": 17,
  "achievability_score": 16,
  "relevance_score": 17,
  "timebound_score": 15,
  "grade": "Good",
  "feedback": "Minor revisions needed"
}
```

## Implementation Checklist

- [ ] Create `api.py` (FastAPI app)
- [ ] Wire validators to endpoints (copy-paste validation logic)
- [ ] Wire PICOT scorer to endpoint
- [ ] Add project management endpoints
- [ ] Add error handling (try/except, HTTP status codes)
- [ ] Add request validation (Pydantic models)
- [ ] Test all endpoints with curl/Postman
- [ ] Update requirements.txt (fastapi, uvicorn)
- [ ] Create API documentation (FastAPI auto-generates)
- [ ] Update CLAUDE.md with API section

## Run Command
```bash
uvicorn api:app --reload
# API available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

## Testing
```bash
pytest tests/api/              # New API tests (TDD)
curl -X POST http://localhost:8000/api/validators/sample-size \
  -H "Content-Type: application/json" \
  -d '{"n": 100, "unit_beds": 30, "duration_months": 6, "effect_size": 0.5}'
```

---

# Phase 7: Frontend UI

**Status:** PLANNED
**Target:** React web app for PICOT builder + validators
**Effort:** 20-40 hours
**Dependencies:** Phase 6 complete ✅

## Tech Stack
```
Framework: React 18
Styling: Tailwind CSS
State: Zustand
Forms: React Hook Form
API: Axios
Routing: React Router v6
Package Manager: npm
```

## Core Pages

### 1. Dashboard
- List all projects
- Switch active project
- Create new project button

### 2. PICOT Builder (Main)
- Form: Population, Intervention, Comparison, Outcome, Timeframe
- Real-time PICOT scorer feedback
- Grade display + improvement suggestions
- Save button

### 3. Validators Panel
- Sample Size: slider for n, capacity bar
- Timeline: date picker, feasibility indicator
- Budget: cost breakdown, per-patient display
- All show ✅/❌ with actionable suggestions

### 4. Workflow Status
- Pipeline visualization: PICOT → Search → Validate → Write
- Progress bar
- Results display

### 5. Literature Search
- Display search results
- Citation validation status
- Selected/rejected indicators

## Components Structure
```
src/
├── components/
│   ├── ProjectSelector.tsx
│   ├── PICOTForm.tsx
│   ├── ValidatorPanel.tsx
│   ├── WorkflowStatus.tsx
│   └── SearchResults.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── PICOTBuilder.tsx
│   └── Validators.tsx
├── services/
│   └── api.ts                 (Axios config)
└── App.tsx
```

## Setup
```bash
npx create-react-app frontend
cd frontend
npm install tailwindcss zustand react-hook-form axios react-router-dom
```

## Run
```bash
npm start
# App available at: http://localhost:3000
```

## Backend Integration
```typescript
// services/api.ts
const API = axios.create({
  baseURL: 'http://localhost:8000/api'
});

export const validateSampleSize = (data) => API.post('/validators/sample-size', data);
export const scorePICOT = (picot) => API.post('/picot/score', { picot });
```

---

## Timeline

| Phase | Week | Hours | Status |
|-------|------|-------|--------|
| **Phase 5** | 1 | 28 | ✅ COMPLETE |
| **Phase 6** | 2 | 8-12 | 🔄 NEXT |
| **Phase 7** | 3-4 | 20-40 | ⏳ AFTER |

## Total Implementation: ~48-60 hours (6-8 days)

---

**Created:** 2025-12-07
**Updated:** Phase 5 completion
**Owner:** nurseRN Development Team
