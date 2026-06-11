# compliance-silent
import os, sys, subprocess

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = current_dir
    while repo_root:
        if os.path.exists(os.path.join(repo_root, ".rokct")):
            break
        parent = os.path.dirname(repo_root)
        if parent == repo_root:
            break
        repo_root = parent
    
    scripts_dir = os.path.join(repo_root, "scripts")
    rel_path = os.path.relpath(os.path.abspath(__file__), scripts_dir)
    target = os.path.join(repo_root, ".rokct", "skills", "opportunities_registry", "scripts", rel_path)
    
    if not os.path.exists(target):
        print(f"Error: Target script not found in .rokct skill path: {target}", file=sys.stderr)
        print("Please run initiate.py first to fetch skills.", file=sys.stderr)
        sys.exit(1)
        
    res = subprocess.run([sys.executable, target] + sys.argv[1:])
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
