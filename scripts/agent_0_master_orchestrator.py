import subprocess
import sys
import os
import argparse
import config

def run_pipeline(project, component, config_name, module, section, test_pdf, offline=False, input_file=None):
    # Paths resolved dynamically using config
    req_decoder_script = os.path.join(config.BASE_DIR, "agent_1_requirement_understanding.py")
    trace_mapper_script = os.path.join(config.BASE_DIR, "agent_2_traceability_mapper.py")
    excel_generator_script = os.path.join(config.BASE_DIR, "agent_3_excel_report_generator.py")
    
    decoded_reqs_json = os.path.join(config.WORKSPACE_DIR, "decoded_requirements.json")
    trace_matrix_json = os.path.join(config.WORKSPACE_DIR, "traceability_matrix.json")
    final_excel_report = os.path.join(config.WORKSPACE_DIR, "traceability_report.xlsx")
    
    python_exe = sys.executable  # Uses current environment python

    # ==========================================
    # STEP 1: Execute Agent 1 (Requirement Decoder)
    # ==========================================
    print("\n--- [Orchestrator] Triggering Agent 1: Requirement Extraction ---")
    agent_1_cmd = [
        python_exe, req_decoder_script,
        "--section", section
    ]
    if offline:
        agent_1_cmd.append("--offline")
        if input_file:
            agent_1_cmd.extend(["--input-file", input_file])
    else:
        agent_1_cmd.extend([
            "--project", project,
            "--component", component,
            "--config", config_name,
        ])
        if module:
            agent_1_cmd.extend(["--module", module])
            
    print(f"[*] Running command: {' '.join(agent_1_cmd)}")
    subprocess.run(agent_1_cmd, check=True)

    # ==========================================
    # STEP 2: Execute Agent 2 (Traceability Mapper)
    # ==========================================
    print("\n--- [Orchestrator] Triggering Agent 2: Traceability Mapping ---")
    agent_2_cmd = [
        python_exe, trace_mapper_script,
        "--req-json", decoded_reqs_json,
        "--test-pdf", test_pdf,
        "--output", trace_matrix_json
    ]
    print(f"[*] Running command: {' '.join(agent_2_cmd)}")
    subprocess.run(agent_2_cmd, check=True)

    # ==========================================
    # STEP 3: Execute Agent 3 (Excel Report Generator)
    # ==========================================
    print("\n--- [Orchestrator] Triggering Agent 3: Excel Report Generation ---")
    agent_3_cmd = [
        python_exe, excel_generator_script,
        "--input-json", trace_matrix_json,
        "--output-excel", final_excel_report
    ]
    print(f"[*] Running command: {' '.join(agent_3_cmd)}")
    subprocess.run(agent_3_cmd, check=True)

    print("\n========================================================")
    print("🎉 [Orchestrator] Pipeline executed successfully!")
    print(f"📁 Excel Report saved to: {final_excel_report}")
    print("========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Agent 0: Master Orchestrator Agent")
    parser.add_argument("--project", default="NEO", help="DNG Project Area Name")
    parser.add_argument("--component", default="NEO", help="DNG Component Name")
    parser.add_argument("--config", default="DNG NEO Stream", help="DNG Configuration/Stream Name")
    parser.add_argument("--module", default=None, help="DNG Module Title")
    parser.add_argument("--section", default="MCU", help="The section heading title to extract")
    parser.add_argument("--test-pdf", required=True, help="Absolute path to the ETM downloaded testcases PDF file")
    parser.add_argument("--offline", action="store_true", help="Bypass DNG connection and run offline")
    parser.add_argument("--input-file", default=None, help="Path to local Excel/CSV for offline mode")
    
    args = parser.parse_args()
    
    run_pipeline(
        project=args.project,
        component=args.component,
        config_name=args.config,
        module=args.module,
        section=args.section,
        test_pdf=args.test_pdf,
        offline=args.offline,
        input_file=args.input_file
    )

if __name__ == "__main__":
    main()
