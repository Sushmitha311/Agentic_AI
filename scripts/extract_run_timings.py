import os
import json
import re
from datetime import datetime
import config

# Resolve chats_dir dynamically relative to the user's gemini home directory
chats_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini", "tmp", "hackathon", "chats"))

def parse_iso(ts):
    if not ts:
        return None
    ts = ts.replace("Z", "")
    if "." in ts:
        base, ms = ts.split(".")
        ms = ms[:6]
        ts = f"{base}.{ms}"
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
    else:
        fmt = "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(ts, fmt)

print("Scanning chats for tool calls and executions...")

for root, dirs, files in os.walk(chats_dir):
    for f in files:
        if f.endswith(".jsonl"):
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, chats_dir)
            
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                for line_idx, line in enumerate(file):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                    
                    # Look for tool calls or stdout logs in the chat
                    if "type" in data and data["type"] == "gemini":
                        thoughts = data.get("thoughts", [])
                        for th in thoughts:
                            desc = th.get("description", "")
                            if "master" in desc.lower() or "orchestrator" in desc.lower() or "agent_1" in desc.lower() or "agent_2" in desc.lower():
                                print(f"[{rel_path}][L{line_idx}] {th.get('timestamp')} - Thought ({th.get('subject')}): {desc[:150]}")
                    
                    if "toolCalls" in data:
                        for tc in data["toolCalls"]:
                            print(f"[{rel_path}][L{line_idx}] Tool Call: {tc.get('name')} with arguments {str(tc.get('args'))[:150]}")
