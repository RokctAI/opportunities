# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import json
import argparse
import sys

def load_monorepo_env(custom_path=None):
    """
    Recovers the JULES_API_KEY from the central Monorepo.
    Priority 1: Remote Vault (GitHub API via MONOREPO_PAT)
    Priority 2: Local Hunting (Monorepo sibling folder)
    """
    # --- 1. REMOTE CI MODE (GitHub API) ---
    pat = os.environ.get("MONOREPO_PAT")
    if pat:
        url = "https://api.github.com/repos/RokctAI/monorepo/contents/.env/production.env"
        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3.raw"
        }
        try:
            # We fetch as RAW plain text
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                if parse_env_content(resp.text):
                    return True
        except Exception as e:
            print(f"⚠️ Vault fetch error: {e}")

    # --- 2. LOCAL FALLBACK MODE ---
    env_paths = []
    if custom_path: env_paths.append(custom_path)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_paths.append(os.path.join(workspace_root, "Monorepo", ".env", "production.env"))
    env_paths.append(os.path.join(workspace_root, ".env", "production.env"))

    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    parse_env_content(f.read())
                return True
            except: pass
    return False

def parse_env_content(content):
    """Parses .env content for keys. Priority: JULES then AGENT."""
    lines = content.splitlines()
    found = False
    
    # Pass 1: JULES_API_KEY
    for line in lines:
        if "JULES_API_KEY=" in line:
            val = line.replace("export ", "").strip().split("=", 1)[1].strip("'\" ")
            os.environ["JULES_API_KEY"] = val
            found = True
            break
            
    # Pass 2: AGENT_API_KEY (if JULES not found)
    if not found:
        for line in lines:
            if "AGENT_API_KEY=" in line:
                val = line.replace("export ", "").strip().split("=", 1)[1].strip("'\" ")
                os.environ["AGENT_API_KEY"] = val
                found = True
                break
    return found

BASE_URL = "https://jules.googleapis.com/v1alpha"

class AgentCLI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }

    def create_session(self, prompt, source_repo, automation_mode="AUTO_CREATE_PR", title=None, branch="main", require_approval=False):
        url = f"{BASE_URL}/sessions"
        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": source_repo,
                "githubRepoContext": {
                    "startingBranch": branch
                }
            },
            "automationMode": automation_mode,
            "requirePlanApproval": require_approval
        }
        if title: payload["title"] = title
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_session(self, session_id):
        url = f"{BASE_URL}/sessions/{session_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def main():
    parser = argparse.ArgumentParser(description="Delegate tasks to an AI Agent (Silent Vault Mode).")
    parser.add_argument("--api-key", help="Explicit API Key")
    parser.add_argument("--env-file", help="Local env file (Fallback)")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create Session
    create_parser = subparsers.add_parser("create", help="Create session")
    create_parser.add_argument("--prompt", required=True)
    create_parser.add_argument("--repo", required=True)
    create_parser.add_argument("--branch", default="main")
    create_parser.add_argument("--title")
    create_parser.add_argument("--require-approval", action="store_true")
    create_parser.add_argument("--automation-mode", default="AUTO_CREATE_PR")

    # Get Status
    status_parser = subparsers.add_parser("status", help="Get status")
    status_parser.add_argument("--id", required=True)

    args = parser.parse_args()

    # Force Vault Priority: Try to load from Monorepo first if MONOREPO_PAT is present
    if os.environ.get("MONOREPO_PAT"):
        load_monorepo_env(args.env_file)

    # Resolve Key
    api_key = args.api_key or os.environ.get("JULES_API_KEY") or os.environ.get("AGENT_API_KEY")

    # Final fallback: If still no key, try local env search one last time
    if not api_key and not os.environ.get("MONOREPO_PAT"):
        load_monorepo_env(args.env_file)
        api_key = os.environ.get("JULES_API_KEY") or os.environ.get("AGENT_API_KEY")

    if not api_key:
        print("❌ Error: Delegation Failed. Key vault unreachable.")
        sys.exit(1)

    cli = AgentCLI(api_key)

    try:
        if args.command == "create":
            repo = args.repo
            if not repo.startswith("sources/"): repo = f"sources/github/{repo}"
            result = cli.create_session(args.prompt, repo, title=args.title, branch=args.branch,
                                     require_approval=args.require_approval, automation_mode=args.automation_mode)
            print(json.dumps(result, indent=2))
        elif args.command == "status":
            result = cli.get_session(args.id)
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
