import os

# Base directory is the scripts folder (e.g., D:\Hackathon\Agentic_AI\scripts)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root directory (e.g., D:\Hackathon)
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

# Local workspace directory for all temporary runtime and output files (e.g., D:\Hackathon\Agentic_AI\workspace)
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "workspace"))
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Path to the DNG oslcquery.EXE executable
OSLCQUERY_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "pmt-server", "pmt-mcp-servers", "mcp", "dng", ".venv", "Scripts", "oslcquery.exe"))

# Path to gemini.cmd CLI wrapper resolved dynamically for any user profile
appdata = os.environ.get("APPDATA")
if appdata:
    GEMINI_CMD = os.path.join(appdata, "npm", "gemini.cmd")
else:
    GEMINI_CMD = "gemini.cmd"

# DNG Connection configurations
DNG_SERVER_RAW = os.getenv("DNG_SERVER", "https://rb-alm-20-p.de.bosch.com")
DNG_SERVER = DNG_SERVER_RAW.rstrip("/")
if DNG_SERVER.endswith("/rm"):
    DNG_SERVER = DNG_SERVER[:-3]
elif DNG_SERVER.endswith("rm"):
    DNG_SERVER = DNG_SERVER[:-2]
DNG_SERVER = DNG_SERVER.rstrip("/")

DNG_USERNAME = os.getenv("DNG_USERNAME")
DNG_PASSWORD = os.getenv("DNG_PASSWORD")
