import os
import sys
import json
import re
import argparse
import subprocess

# Config/Constants
# ==============================================================================
import config

TEMP_DIR = config.WORKSPACE_DIR
DEFAULT_REQ_JSON = os.path.join(TEMP_DIR, "decoded_requirements.json")
DEFAULT_OUTPUT_JSON = os.path.join(TEMP_DIR, "traceability_matrix.json")

def load_decoded_requirements(json_path: str) -> list:
    """Loads and validates the decoded requirements JSON file from Agent 1."""
    if not os.path.exists(json_path):
        print(f"[-] Error: Decoded requirements file not found at: {json_path}")
        print("[*] Please run Agent 1 first to generate this file.")
        sys.exit(1)
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                # If wrapped, extract list
                if isinstance(data, dict) and "requirements" in data:
                    data = data["requirements"]
                else:
                    data = [data]
            return data
    except Exception as e:
        print(f"[-] Error reading JSON requirements: {e}")
        sys.exit(1)

def map_traceability_with_llm(requirements: list, pdf_path: str) -> dict:
    """Uses Gemini CLI to read the testcases PDF, map requirements, and build matrix."""
    print(f"[*] Initializing LLM comparison against testcases PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"[-] Error: ETM testcases PDF file not found at: {pdf_path}")
        sys.exit(1)

    # Copy PDF to allowed workspace temporary directory to pass security constraints
    copied_temp = False
    local_pdf_path = os.path.join(TEMP_DIR, os.path.basename(pdf_path))
    if os.path.abspath(pdf_path) != os.path.abspath(local_pdf_path):
        print(f"[*] Copying PDF to allowed workspace path: {local_pdf_path}")
        import shutil
        try:
            shutil.copy2(pdf_path, local_pdf_path)
            pdf_path = local_pdf_path
            copied_temp = True
        except Exception as e:
            print(f"[-] Warning: Failed to copy PDF to temp directory: {e}")

    # Split requirements into batches of 8 to prevent context bloating and generation timeouts
    batch_size = 8
    batches = [requirements[i:i + batch_size] for i in range(0, len(requirements), batch_size)]
    total_batches = len(batches)
    
    all_traceability_matrix = []
    
    for idx, batch in enumerate(batches):
        batch_num = idx + 1
        print(f"[*] Processing Traceability Mapping Batch {batch_num} of {total_batches}...")
        
        req_payload = []
        for req in batch:
            req_payload.append({
                "requirement_id": req.get("requirement_id") or req.get("id"),
                "title": req.get("title")
            })
            
        prompt = f"""
You are the "Traceability & Mapping Agent" (Agent 2) in a safety-critical automotive systems test engineering pipeline.
Your mission is to analyze the attached ETM Test Cases PDF, understand its test objectives/steps/validations, and map them to our list of software requirements to calculate coverage.

Perform the following tasks:
1. Parse the attached ETM testcases PDF document.
2. Identify any test cases, their unique IDs, objectives, steps, and validation targets.
3. Compare the test cases in the PDF against this subset of requirements:
{json.dumps(req_payload, indent=2)}
4. Determine if each requirement in this subset is covered by at least one testcase or is "Missing".

You MUST output your response STRICTLY as a valid JSON array matching this schema:
[
  {{
    "requirement_id": "string (the requirement ID)",
    "requirement_title": "string (the requirement title)",
    "status": "string ('Covered' or 'Missing')",
    "linked_testcases": [
      {{
        "testcase_id": "string (the ETM testcase ID/Name, or 'N/A' if missing)",
        "objective": "string (objectives extracted from test case, or 'N/A' if missing)",
        "steps": ["string (actions/steps of the testcase, or empty if missing)"],
        "validations": ["string (verification criteria/validation targets, or empty if missing)"]
      }}
    ]
  }}
]

Ensure the ETM PDF file is analyzed by using the attached file token: @{pdf_path}

Output ONLY raw valid JSON array. Do not wrap in backticks or markdown formatting.
"""
        
        temp_prompt_path = os.path.join(TEMP_DIR, f"temp_traceability_prompt_{batch_num}.txt")
        try:
            with open(temp_prompt_path, "w", encoding="utf-8") as pf:
                pf.write(prompt)

            cmd = [
                config.GEMINI_CMD,
                "-p", f"Analyze requirements in @{temp_prompt_path} and map against test cases PDF in @{pdf_path}. Output strictly raw valid JSON array."
            ]
            
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
            
            # Clean up temp prompt file
            try:
                os.remove(temp_prompt_path)
            except Exception:
                pass
                
            if res.returncode != 0:
                print(f"[-] Gemini CLI call failed for batch {batch_num}. Exit Code: {res.returncode}")
                print(f"[-] STDERR: {res.stderr}")
                continue
                
            llm_response = res.stdout.strip()
            
            # Isolate JSON array
            json_match = re.search(r'(\[.*\])', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = llm_response
                
            # Clean up unescaped newlines/carriages inside JSON string fields
            def replace_newlines(match):
                return match.group(0).replace('\n', '\\n').replace('\r', '\\r')
            json_str = re.sub(r'"(?:[^"\\]|\\.)*"', replace_newlines, json_str)
                
            batch_matrix = json.loads(json_str)
            if isinstance(batch_matrix, list):
                all_traceability_matrix.extend(batch_matrix)
                print(f"[+] Successfully mapped Batch {batch_num} of {total_batches}.")
            else:
                print(f"[-] Warning: Batch {batch_num} did not return a valid list.")
                
        except Exception as e:
            print(f"[-] Failed to process batch {batch_num}: {e}")
            if 'res' in locals():
                print(f"[-] STDOUT: {res.stdout}")
            continue

    # Clean up copied PDF
    if copied_temp:
        try:
            os.remove(pdf_path)
        except Exception:
            pass

    # Compile final metrics
    total_reqs = len(all_traceability_matrix)
    covered_reqs = sum(1 for r in all_traceability_matrix if r.get("status") == "Covered")
    cov_pct = f"{int((covered_reqs / total_reqs) * 100)}%" if total_reqs > 0 else "0%"
    
    final_result = {
        "total_requirements": total_reqs,
        "covered_requirements": covered_reqs,
        "coverage_percentage": cov_pct,
        "traceability_matrix": all_traceability_matrix
    }
    
    return final_result

def main():
    parser = argparse.ArgumentParser(description="Agent 2: Traceability & Mapping Agent")
    parser.add_argument("--req-json", default=DEFAULT_REQ_JSON, help="Path to decoded requirements JSON from Agent 1")
    parser.add_argument("--test-pdf", required=True, help="Path to the ETM downloaded testcases PDF file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_JSON, help="Path to output traceability matrix JSON")
    args = parser.parse_args()

    print("[*] Running Agent 2: Traceability & Mapping Pipeline")
    print(f"[*] Decoded Requirements Input: {args.req_json}")
    print(f"[*] ETM Testcases PDF Input: {args.test_pdf}")
    print(f"[*] Traceability Matrix Output: {args.output}")

    # Step 1: Load inputs
    requirements = load_decoded_requirements(args.req_json)
    print(f"[+] Loaded {len(requirements)} requirements successfully.")

    # Step 2: Call Gemini CLI to parse PDF and match requirements
    matrix_result = map_traceability_with_llm(requirements, args.test_pdf)

    # Step 3: Write structured output
    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(matrix_result, out, indent=2)

    # Step 4: Display Summary report
    print("\n" + "="*50)
    print("📋 COVERAGE & TRACEABILITY SUMMARY REPORT")
    print("="*50)
    print(f"Total Requirements:       {matrix_result.get('total_requirements')}")
    print(f"Covered Requirements:     {matrix_result.get('covered_requirements')}")
    print(f"Requirements Coverage %:  {matrix_result.get('coverage_percentage')}")
    print("-"*50)
    print(f"[+] Traceability Matrix saved to: {args.output}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
