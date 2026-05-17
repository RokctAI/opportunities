#!/usr/bin/env python3
"""
Thin wrapper — delegates to the shared copy in The-Rokct-Protocol.
All existing workflow paths (relative to CWD) are preserved.
"""
import os
import sys

# Walk from this file to find The-Rokct-Protocol
# This file lives at: .rokct/scripts/agent_delegation/delegate_to_agent.py
_here = os.path.dirname(os.path.abspath(__file__))
# .rokct/  = 3 dirname levels up (agent_delegation → scripts → .rokct/)
_workspace = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
# The-Rokct-Protocol is a sibling of workspace
_workspace_parent = os.path.dirname(_workspace)

_thenr = os.path.join(
    _workspace_parent, "The-Rokct-Protocol", "core", "skills",
    "agent_delegation", "scripts", "delegate_to_agent.py"
)

if not os.path.exists(_thenr):
    # Fallback: search upward for The-Rokct-Protocol
    _search = _workspace
    for _ in range(5):
        _candidate = os.path.join(_search, "The-Rokct-Protocol", "core",
                                  "skills", "agent_delegation",
                                  "scripts", "delegate_to_agent.py")
        if os.path.exists(_candidate):
            _thenr = _candidate
            break
        _parent = os.path.dirname(_search)
        if _parent == _search:
            break
        _search = _parent

if not os.path.exists(_thenr):
    print(f"Error: shared delegate_to_agent.py not found (checked {_thenr})",
          file=sys.stderr)
    sys.exit(1)

# Insert shared script dir so 'import delegate_to_agent' works cleanly
_shared_dir = os.path.dirname(_thenr)
if _shared_dir not in sys.path:
    sys.path.insert(0, _shared_dir)

# Import the shared module and call its main() with our argv
import delegate_to_agent  # noqa: E402
sys.exit(delegate_to_agent.main())
