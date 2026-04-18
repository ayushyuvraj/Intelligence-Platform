# RegRadar Tracking & Progress Commands
## How to Track Your Development

**Purpose:** Centralized commands for tracking progress across all tools  
**Updated:** April 15, 2026  
**Status:** Ready to Use

---

## 🎯 QUICK STATUS COMMANDS

### Check Current Day Status
```bash
# Read the progress tracker
cat .claude/memory/PROGRESS_TRACKER.md

# Or in conversation with Claude:
"What day are we on and what's the current status?"
# Claude reads PROGRESS_TRACKER.md automatically
```

### Check Current Metrics
```bash
# Run tests and get coverage
pytest --cov=src --cov-report=term-missing

# Check frontend coverage
npm run test

# Run linter
pylint src/
eslint frontend/src/

# Type check
mypy src/
```

### Check Overall Progress
```bash
# What's complete:
git log --oneline | head -20

# What's in progress:
git status

# What branch are we on:
git branch --show-current
```

---

## 📋 TASK TRACKING WITH CLAUDE

### Create a Task
```
You: "Create task: Implement SEBI scraper with edge case handling"

Claude uses TaskCreate and creates a trackable task
Claude shows task ID you can reference later
```

### Check All Tasks
```
You: "List all tasks"
or
You: "/tasks"

Claude shows all current tasks:
- Task ID
- Status (pending, in_progress, completed)
- Description
```

### Update Task Status
```
You: "Mark task [ID] as in_progress"
Claude updates automatically

You: "Mark task [ID] as completed"
Claude updates and shows next available task
```

### Get Next Task
```
You: "What's next?"

Claude reads:
1. PROGRESS_TRACKER.md (current day)
2. EXECUTION_ROADMAP.md (what's planned)
3. Task list (what's not started)

Shows you the next task to work on
```

---

## 📊 DAILY TRACKING WORKFLOW

### At Session Start
```
1. Claude loads .claude/memory/PROGRESS_TRACKER.md
2. You ask: "What day are we on?"
3. Claude tells you current day and status
4. You continue from where you left off
```

### At Start of Day
```
1. Read EXECUTION_ROADMAP.md for today's tasks
2. Create tasks for today's work
3. Track time spent per task
4. Log notes and issues
```

### During Development
```
1. Work on current task
2. Write tests as you go
3. Commit frequently with clear messages
4. Pre-commit hook validates quality
```

### At End of Day
```
1. Update PROGRESS_TRACKER.md:
   - Mark completed tasks
   - Update completion percentage
   - Add notes learned
   - Log issues found
   - Update metrics

2. Update git with final commits
3. Create summary of day's work
```

---

## 🔄 PHASE/SPRINT/DAY TRACKING

### Current Phase (Phase 1: MVP)
```
Status: In Progress
Duration: 10 working days
Progress: [========                    ] X%
Completion Expected: 2 weeks from start date

Track in: .claude/memory/PROGRESS_TRACKER.md → "CURRENT STATUS SNAPSHOT"
```

### Current Sprint (Sprint 1: Days 1-10)
```
Sprint Duration: 2 weeks
Sprint Goals: Complete Phase 1 MVP
Sprint Status: [day count] / 10 days complete

Track in: .claude/memory/PROGRESS_TRACKER.md → "PHASE 1 BREAKDOWN"
```

### Current Day (Variable)
```
Today's Tasks: See EXECUTION_ROADMAP.md
Deliverables: See EXECUTION_ROADMAP.md
Success Criteria: See EXECUTION_ROADMAP.md
Time Budget: 8 hours

Track in: .claude/memory/PROGRESS_TRACKER.md → "[Day #] section"
```

---

## 📈 PROGRESS DASHBOARD (Claude Code Task System)

### View All Tasks
```
Command: "Show all tasks"
or "/tasks"

Claude shows:
- Total tasks: [count]
- Completed: [count]
- In Progress: [count]
- Pending: [count]
- Overall %: [percentage]
```

### Task Details
```
Command: "Get details on task [TASK_ID]"

Claude shows:
- Task description
- Status
- Dependencies
- Estimated time
- Actual time spent
- Blockers
```

### Create New Task
```
You: "Create task for Day 3: Implement SEBI scraper"

Claude:
- Creates task with ID
- Links to EXECUTION_ROADMAP.md
- Marks dependencies
- Returns task ID for tracking
```

### Mark Task Complete
```
You: "Mark task [TASK_ID] as complete"

Claude:
- Updates task status
- Logs completion time
- Shows next available task
- Updates memory
```

---

## 📝 DAILY LOG TEMPLATE

Use this template at end of each day:

```
## Day [X] - [Date] Summary

**Status:** ✅ Completed / 🔄 In Progress / ⏳ Blocked

**Tasks Completed:**
- [Task 1] ✅
- [Task 2] ✅
- [Task 3] 🔄

**Deliverables Met:**
- ✅ [Deliverable 1]
- ✅ [Deliverable 2]
- 🔄 [Deliverable 3]

**Time Spent:** [X] hours
**Actual vs Planned:** On track / Ahead / Behind

**Code Quality:**
- Test Coverage: [X]%
- Linter Score: [X]/10
- Type Check: Pass / Fail
- Performance: [details]

**Issues Found:**
- [Issue 1]: [Severity] → [Resolution]
- [Issue 2]: [Severity] → [Resolution]

**Notes & Learnings:**
- [Key learning 1]
- [Key learning 2]
- [Approach for tomorrow]

**Metrics:**
- Lines of code: [X]
- Tests written: [X]
- Bugs fixed: [X]
- Performance improvement: [%]

**Next Day:**
- First task: [from EXECUTION_ROADMAP.md]
- Expected completion: [hours]
```

---

## 🎯 TRACKING CHECKLIST

### Daily (Every Day)
- [ ] Read current day tasks (EXECUTION_ROADMAP.md)
- [ ] Create tasks for today's work
- [ ] Track time per task
- [ ] Run tests before commit
- [ ] Update PROGRESS_TRACKER.md at end of day

### Weekly (Friday)
- [ ] Review week's progress
- [ ] Update memory files
- [ ] Check if on track for timeline
- [ ] Log lessons learned
- [ ] Plan next week

### At Phase End
- [ ] All tasks completed ✅
- [ ] Test coverage 80%+ ✅
- [ ] Zero critical bugs ✅
- [ ] Performance benchmarks met ✅
- [ ] Documentation complete ✅
- [ ] Ready for next phase ✅

---

## 📊 METRICS TO TRACK DAILY

### Code Quality Metrics
```bash
# Track these daily
pytest --cov=src --cov-report=term-missing
# Expected: Coverage increasing (target 80%+)

pylint src/ --exit-zero
# Expected: Score increasing (target 8.0+)

mypy src/
# Expected: Type check passing
```

### Performance Metrics
```bash
# Track these weekly
# Feed load time (target: <2s)
# API response time (target: <500ms)
# Database query time (target: <200ms)

# Log in PROGRESS_TRACKER.md
```

### Development Velocity
```
Track:
- Lines of code written
- Tests written
- Bugs fixed
- Features completed
- Time spent per task
```

---

## 🚨 BLOCKER TRACKING

### Log a Blocker
```
You: "I'm blocked on [issue]. Create blocker: [description]"

Claude:
- Creates blocker task
- Marks status as BLOCKED
- Suggests workarounds
- Tracks resolution
```

### Check Blockers
```
You: "Show all blockers"

Claude shows:
- Blocker description
- When identified
- Severity
- Proposed resolution
- Status
```

### Resolve Blocker
```
You: "Blocker [ID] resolved: [solution]"

Claude:
- Updates blocker status
- Logs resolution
- Unblocks dependent tasks
- Continues development
```

---

## 📞 QUICK COMMANDS REFERENCE

### Status Checks
```
"What day are we on?"
"What's the current status?"
"Show all tasks"
"What's next?"
"Are we on track?"
"What's blocking us?"
```

### Task Management
```
"Create task: [description]"
"List all pending tasks"
"Start task [ID]"
"Complete task [ID]"
"What's blocking this task?"
```

### Progress Tracking
```
"Update progress tracker"
"What's our completion percentage?"
"How much time spent today?"
"Compare actual vs planned"
"Show metrics dashboard"
```

### Issue Tracking
```
"Log issue: [description]"
"Show all issues"
"Resolve issue [ID]"
"Mark issue [ID] as critical"
"What's the workaround for [issue]?"
```

### Daily Standup
```
"Daily standup"
"What did we complete?"
"What's in progress?"
"What's next?"
"Any blockers?"
```

---

## 🔗 INTEGRATION POINTS

### Memory System
- **PROGRESS_TRACKER.md** - Updated daily with day/task status
- **project_context.md** - Updated weekly with phase progress
- **development_standards.md** - Reference for quality checks

### Task System (Claude Code)
- Create task for each day's work
- Update task status as you progress
- Mark complete when deliverables met

### Git Commits
- Use format: `[PHASE#-DAY#-TASK] Description`
- Commit frequently (multiple per day)
- Pre-commit hook validates quality

### Metrics Tracking
- Daily: Test coverage, linter score
- Weekly: Performance metrics, velocity
- Phase-end: Overall quality metrics

---

## 📈 TRACKING EXAMPLES

### Example: Check Status (Start of Day)
```
You: "Hi Claude, what day are we on and what should I work on?"

Claude:
1. Reads PROGRESS_TRACKER.md → "Day 3"
2. Reads EXECUTION_ROADMAP.md → Day 3 tasks
3. Checks task list → Pending tasks for Day 3
4. Responds: "We're on Day 3 of 10 (30% complete). 
   Today's focus: SEBI Scraper.
   Your tasks:
   1. Base scraper class (2h)
   2. SEBI RSS parser (2h)
   3. Error handling (2h)
   4. Testing (2h)
   
   Start with task 1: Base scraper class"
```

### Example: Log Progress (End of Day)
```
You: "Day 3 complete. SEBI scraper working, error handling done,
     tests written. Coverage at 85%. Ready for RBI scraper tomorrow.
     1 issue: need better timeout handling for slow feeds."

Claude:
1. Updates PROGRESS_TRACKER.md:
   - Mark Day 3 as ✅ Complete
   - Update metrics (coverage 85%)
   - Add notes about timeout issue
   - Update progress bar (30% → 40%)

2. Creates task for Day 4: RBI Scraper

3. Confirms: "Great! Day 3 complete, on track.
   Tomorrow: RBI scraper implementation.
   Blocker from today (timeout handling) will be addressed in improved retry logic."
```

### Example: Weekly Review
```
You: "End of week summary. Days 1-5 complete. Ready for Phase 2 planning."

Claude:
1. Reviews PROGRESS_TRACKER.md
2. Summarizes Week 1 achievements
3. Updates project_context.md with progress
4. Prepares Phase 2 planning
5. Confirms: "Week 1 complete: 50% progress.
   Backend core complete (DB, scrapers, AI).
   Week 2: Frontend & integration.
   On schedule for Phase 1 launch in 10 days."
```

---

## ✅ BEFORE YOU START

1. ✅ Read EXECUTION_ROADMAP.md (today's plan)
2. ✅ Understand PROGRESS_TRACKER.md (how to update)
3. ✅ Know the commands above
4. ✅ Start Day 1 with clear task list
5. ✅ Update tracker at end of each day

---

**Ready to start building!** 🚀

