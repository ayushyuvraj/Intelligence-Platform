# .claude Directory - Claude Code Configuration & Automation

This directory contains all Claude Code configuration, hooks, and cross-session memory for the RegRadar project.

## Structure

```
.claude/
├── settings.json              # Claude Code configuration
├── memory/                    # Persistent cross-session memory
│   ├── MEMORY.md             # Memory index
│   ├── project_context.md    # Project overview & status
│   ├── development_standards.md # Quality standards
│   └── (other memory files)
├── hooks/                     # Git hooks for automation
│   ├── pre-commit            # Runs before each commit
│   ├── pre-push              # Runs before push
│   └── post-merge            # Runs after merge
└── README.md                 # This file
```

## Usage

### For Claude Code
Claude will automatically:
1. Load memory from `memory/` at session start
2. Execute hooks from `hooks/` at appropriate times
3. Apply settings from `settings.json`
4. Update memory as work progresses

### For Developers
- **Check Memory:** Review `memory/MEMORY.md` and `memory/project_context.md` for project status
- **Configure Behavior:** Edit `settings.json` to change Claude's behavior
- **Setup Hooks:** Run `git config core.hooksPath .claude/hooks` to enable automation

## Key Features

### 🧠 Persistent Memory
Cross-session knowledge base that persists between conversations:
- Project context and timeline
- Development standards and quality gates
- Technical decisions and rationale
- Performance metrics and progress
- User feedback and issues
- Architecture decisions

**Check at session start:** What's the current status? What was I working on?

### 🔧 Automated Hooks
Git hooks for quality assurance:
- **pre-commit:** Format code, lint, check types, run tests
- **pre-push:** Verify tests pass, no secrets exposed
- **post-merge:** Run integration tests

**Setup:** `git config core.hooksPath .claude/hooks`

### ⚙️ Configuration
Central configuration in `settings.json`:
- Model selection (default, fast, thinking mode)
- Code quality standards (formatter, linter)
- Testing requirements (coverage, framework)
- Performance targets
- Security policies
- Monitoring configuration
- AI assistant preferences

### 📊 Quality Metrics
Tracked and enforced:
- Test coverage: 80%+ required
- Response times: <2s feed, <500ms API
- Code complexity: max cyclomatic complexity 10
- Type hints: required
- Documentation: docstrings required
- Error handling: every external call

## Memory System

### How It Works
1. Claude reads memory at session start from `memory/` files
2. Memory provides context for decisions
3. Claude updates memory as work progresses
4. Next session has full context of previous work

### What's Stored
- **project_context.md** - Current project status, timeline, tech stack
- **development_standards.md** - Code quality, testing, security standards
- **MEMORY.md** - Index and quick reference
- (Work in progress files added as needed)

### Example Memory Query
When you ask Claude: "What's the current status?"
Claude checks `memory/project_context.md` and responds with current phase, completed features, blockers.

## Settings.json Configuration

### Critical Settings
```json
{
  "code_quality": {
    "formatter": {"python": "black", "javascript": "prettier"},
    "linter": {"python": "pylint", "javascript": "eslint"},
    "type_checker": {"python": "mypy", "javascript": "typescript"}
  },
  "testing": {
    "coverage": {
      "minimum_percentage": 80,
      "fail_on_lower": true
    }
  },
  "ai_assistant": {
    "voice": "direct",
    "include_error_handling": true,
    "include_tests": true,
    "verify_code_works": "always"
  }
}
```

### Performance Targets
```json
{
  "performance": {
    "target_feed_load_time_ms": 2000,
    "target_api_response_time_ms": 500,
    "target_database_query_time_ms": 200
  }
}
```

### Quality Gates
```json
{
  "quality_gates": {
    "minimum_coverage": 80,
    "maximum_complexity": 10,
    "require_type_hints": true,
    "require_docstrings": true,
    "require_error_handling": true
  }
}
```

## Hooks Setup

### Enable Hooks
```bash
git config core.hooksPath .claude/hooks
chmod +x .claude/hooks/*
```

### Example Hook (pre-commit)
Runs before each commit:
```bash
#!/bin/bash
# Format code
black src/
prettier --write .

# Lint
pylint src/
eslint src/

# Type check
mypy src/

# Run tests
pytest --cov=src --cov-report=term-missing
COVERAGE=$(grep -oP 'TOTAL\s+\K[0-9]+' .coverage.txt || echo "0")
if [ "$COVERAGE" -lt 80 ]; then
  echo "Coverage below 80%: $COVERAGE%"
  exit 1
fi
```

## Best Practices

### 1. Update Memory Regularly
After each major milestone:
```bash
# Check what you accomplished
git log --oneline -10

# Update memory
# Edit .claude/memory/project_context.md with progress
```

### 2. Review Performance
Daily:
```bash
# Check performance metrics
curl http://localhost:8000/health

# View logs
tail -f logs/app.json

# Check test coverage
pytest --cov=src --cov-report=term-missing
```

### 3. Leverage Memory in Conversations
Start with: "Based on the project context, ..."
Claude will check memory automatically.

### 4. Use Specific Commands
Instead of "Build the scraper," say:
"Implement SEBI RSS scraper with edge case handling for network timeouts, malformed XML, missing fields. Include error logging and deduplication. Target: <5s to scrape 50 latest circulars."

### 5. Verify Before Reporting Done
Claude's checklist before completing tasks:
- ✅ Code written and tested
- ✅ Tests pass locally
- ✅ Edge cases handled
- ✅ Error handling complete
- ✅ Documentation done
- ✅ Performance benchmarks met

## Troubleshooting

### Hooks Not Running
```bash
# Check if hooks are enabled
git config core.hooksPath

# Enable if not set
git config core.hooksPath .claude/hooks

# Make executable
chmod +x .claude/hooks/*
```

### Memory Out of Date
- Memory is read-only during execution
- Update by creating/editing files in `memory/`
- Include timestamp when updating: "Last updated: April 15, 2026"

### Tests Failing Before Commit
```bash
# Debug locally
pytest -vv test_that_failed.py

# Fix the issue
# Run full test suite
pytest --cov=src --cov-report=term-missing

# Commit only when tests pass
git add .
git commit -m "[PHASE1-DAY#-TASK] description"
```

## Integration with Claude Code Features

### /plan Command
Creates implementation plan using current project context from memory.

### /review Command  
Code review checklist using development standards from memory.

### /loop Command
Recurring task that updates memory with progress.

### Slash Commands
See CLAUDE.md for all available commands and when to use them.

## Monitoring & Alerts

Configure in settings.json:
- Error rate alerts (>1%)
- Performance regression (>10%)
- Test failure notifications
- Security vulnerability alerts
- Coverage drop alerts

## Next Steps

1. **Enable hooks:** `git config core.hooksPath .claude/hooks`
2. **Review memory:** Check `memory/project_context.md`
3. **Understand standards:** Read `memory/development_standards.md`
4. **Configure Claude:** Review `settings.json`
5. **Start development:** Run `docker-compose up` and begin Phase 1

---

**Last Updated:** April 15, 2026  
**Owner:** Ayush Yuvraj  
**Status:** Ready for Development

