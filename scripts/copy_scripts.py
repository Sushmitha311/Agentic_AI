import os
import shutil
import config

# Resolve source and destination dynamically using the current user's profile and config
src_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini", "agents", "scripts"))
dst_dir = os.path.abspath(os.path.join(config.PROJECT_ROOT, "agents_scripts"))

if os.path.exists(src_dir):
    print(f"Source directory exists: {src_dir}")
    print("Files in source:")
    print(os.listdir(src_dir))
    
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    print(f"Successfully copied scripts to {dst_dir}")
else:
    print(f"Source directory NOT found: {src_dir}")
    parent = os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini"))
    if os.path.exists(parent):
        print(f"Parent directory {parent} exists. Contents:")
        print(os.listdir(parent))
    else:
        print(f"Parent directory {parent} NOT found.")
