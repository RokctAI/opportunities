# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import requests
import json
import argparse
import sys
import base64

def load_monorepo_env(custom_path=None):
    """
    Recovers the JULES_API_KEY.
    1. If MONOREPO_PAT is present, fetches from GitHub API (CI Mode).
    2. Fallback to local hunting (Local Mode).
    """
    # --- 1. REMOTE CI MODE (GitHub API) ---
    pat = os.environ.get("MONOREPO_PAT")
    if pat:
        if os.environ.get("GITHUB_ACTIONS"):
            print("🚀 [CI] MONOREPO_PAT found. Fetching keys from RokctAI/monorepo via API...")
        
        url = "https://api.github.com/repos/RokctAI/monorepo/contents/.env/production.env"
        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3.raw"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                parse_env_content(resp.text)
                if os.environ.get("GITHUB_ACTIONS"):
                    print("✅ [CI] Keys successfully recovered from remote Monorepo.")
                return True
            else:
                print(f"⚠️ [CI] Remote fetch failed (Status: {resp.status_code}). Falling back to local...")
        except Exception as e:
            print(f"⚠️ [CI] Remote API error: {e}")

    # --- 2. LOCAL FALLBACK MODE ---
    env_paths = []
    if custom_path: env_paths.append(custom_path)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    env_paths.append(os.path.join(workspace_root, "Monorepo", ".env", "production.env"))
    env_paths.append(os.path.join(workspace_root, ".env", "production.env"))
    env_paths.append(os.path.join(os.getcwd(), ".env", "production.env"))

    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    parse_env_content(f.read())
                return True
            except: pass
    return False

def parse_env_content(content):
    """Parses .env content for keys."""
    for line in content.splitlines():
        if "JULES_API_KEY=" in line or "AGENT_API_KEY=" in line:
            val = line.replace("export ", "").strip().split("=", 1)[1].strip("'\" ")
            key_name = "JULES_API_KEY" if "JULES_API_KEY" in line else "AGENT_API_KEY"
            os.environ[key_name] = val

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
        if title:
            payload["title"] = title
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_session(self, session_id):
        url = f"{BASE_URL}/sessions/{session_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def main():
    parser = argparse.ArgumentParser(description="Delegate tasks to an AI Agent (Remote-Vault Aware).")
    parser.add_argument("--api-key", help="Agent API Key (overrides vault)")
    parser.add_argument("--env-file", help="Local path to production.env (Fallback)")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create Session
    create_parser = subparsers.add_parser("create", help="Create a new Agent session")
    create_parser.add_argument("--prompt", required=True, help="User prompt/task for the Agent")
    create_parser.add_argument("--repo", required=True, help="Full source name (e.g., 'RokctAI/opportunities')")
    create_parser.add_argument("--branch", default="main", help="Starting branch")
    create_parser.add_argument("--title", help="Session title")
    create_parser.add_argument("--require-approval", action="store_true", help="Require plan approval")
    create_parser.add_argument("--automation-mode", default="AUTO_CREATE_PR", help="Automation mode")

    # Get Status
    status_parser = subparsers.add_parser("status", help="Get session status")
    status_parser.add_argument("--id", required=True, help="Session ID")

    args = parser.parse_args()

    # Priority: 1. Arg, 2. Env Var (already loaded), 3. Remote Vault (API), 4. Local File
    api_key = args.api_key or os.environ.get("AGENT_API_KEY") or os.environ.get("JULES_API_KEY")
    
    if not api_key:
        load_monorepo_env(args.env_file)
        api_key = os.environ.get("AGENT_API_KEY") or os.environ.get("JULES_API_KEY")

    if not api_key:
        print("❌ Error: API Key missing. Remote Vault fetch failed and no local env found.")
        sys.exit(1)

    cli = AgentCLI(api_key)

    try:
        if args.command == "create":
            repo = args.repo
            if not repo.startswith("sources/"):
                repo = f"sources/github/{repo}"
                
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
        if hasattr(e, 'response') and e.response is not None:
            print(f"Details: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
