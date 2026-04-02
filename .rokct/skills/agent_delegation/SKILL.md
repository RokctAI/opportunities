---
name: Agent Delegation
description: Automates the offloading of repetitive or large-scale coding tasks to an AI agent (e.g., Jules).
---

# Agent Delegation Skill

This skill allows you to delegate complex refactoring, migration, or repetitive coding tasks to an AI agent.

## Prerequisites
- **API Key**: Must have a valid `AGENT_API_KEY` (or `JULES_API_KEY`) configured in the environment or a `.env` file accessible to the script.
- **Dependencies**: Requires `requests` and `python-dotenv`.

## Decision Framework (Self-Guideline)
Evaluate at the start of every session or mid-task:
- **Delegate (Agent)**: Bulk refactors, library migrations, repetitive boilerplate, sub-repo isolated work, mid-task error fixes, and lateral/off-topic ideas.
- **Direct (Antigravity)**: Architecture design, UI/UX polish, multi-repo sync, complex discovery.

## How to Use

### 1. Identify a Delegetable Task
Tasks suitable for the Agent include:
- Large-scale string/type migrations (e.g., Int ID to String ID).
- Database library migrations (e.g., Hive to Drift).
- Boilerplate generation across many files.
- Refactoring legacy patterns into modern standards.

### 2. Run the Delegation Script
Use the provided Python script to create a session:

```bash
python .rokct/skills/agent_delegation/scripts/delegate_to_agent.py create \
  --repo "sources/github/RokctAI/Spazafy" \
  --prompt "Your detailed task description here" \
  --title "Feature/Task Name"
```

### 3. Monitor Status
The Agent works asynchronously. Check progress:

```bash
python .rokct/skills/agent_delegation/scripts/delegate_to_agent.py status --id "SESSION_ID"
```

### 4. Approve Plans (Optional)
By default, sessions are auto-approved. To require approval, use the `--require-approval` flag during creation. If enabled, approve the latest plan:

```bash
python .rokct/skills/jules_delegation/scripts/delegate_to_jules.py approve --id "SESSION_ID"
```

## Best Practices
- **Be Specific**: Provide clear, technical instructions in the prompt.
- **Source Format**: Always use the full source name (e.g., `sources/github/Owner/Repo`).
- **Context**: Mentioning specific file paths or patterns helps Jules narrow its scope.
