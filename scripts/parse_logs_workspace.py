import os
import json
import glob
import config

chats_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini", "tmp", "hackathon", "chats"))
jsonl_files = glob.glob(os.path.join(chats_dir, "*.jsonl"))

if not jsonl_files:
    print(f"[-] No session log files found in: {chats_dir}")
    path = ""
else:
    # Sort files by modification time (most recent first)
    jsonl_files.sort(key=os.path.getmtime, reverse=True)
    path = jsonl_files[0]
    print(f"[*] Parsing most recent session log: {path}")

if path and os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            
            # If there's an active gemini response, print it
            if data.get("type") == "gemini":
                print(f"[{idx}] GEMINI (timestamp: {data.get('timestamp')})")
                if "thoughts" in data:
                    print("  Thoughts:")
                    for th in data["thoughts"]:
                        print(f"    - {th.get('subject')}: {th.get('description')[:120]}")
                if "content" in data and data["content"]:
                    print(f"  Content: {str(data['content'])[:500]}")
                if "toolCalls" in data:
                    print("  Tool Calls:")
                    for tc in data["toolCalls"]:
                        print(f"    - {tc.get('name')}")
                print("-" * 60)
