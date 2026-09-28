import os
import json
import config

decoded_path = os.path.join(config.WORKSPACE_DIR, "decoded_requirements.json")
trace_path = os.path.join(config.WORKSPACE_DIR, "traceability_matrix.json")

if os.path.exists(decoded_path):
    print(f"Reading Decoded Requirements: {decoded_path}")
    with open(decoded_path, "r", encoding="utf-8") as f:
        decoded_data = json.load(f)
    print(f"Type: {type(decoded_data)}")
    if isinstance(decoded_data, list):
        print(f"Total Decoded Requirements: {len(decoded_data)}")
        scenarios_count = 0
        scenario_types = {}
        for idx, req in enumerate(decoded_data[:3]):
            print(f"  Req {idx+1}: ID {req.get('requirement_id') or req.get('id')} - {req.get('title')}")
            scenarios = req.get('scenarios', [])
            print(f"    Scenarios Count: {len(scenarios)}")
            for sc in scenarios:
                t = sc.get('scenario_type')
                scenario_types[t] = scenario_types.get(t, 0) + 1
                scenarios_count += 1
        for req in decoded_data[3:]:
            scenarios = req.get('scenarios', [])
            for sc in scenarios:
                t = sc.get('scenario_type')
                scenario_types[t] = scenario_types.get(t, 0) + 1
                scenarios_count += 1
        print(f"Total Scenarios Generated: {scenarios_count}")
        print(f"Scenarios Types Distribution: {scenario_types}")
        print(f"Average Scenarios per Requirement: {scenarios_count / len(decoded_data):.2f}")
else:
    print(f"Decoded Requirements file not found at: {decoded_path}")

if os.path.exists(trace_path):
    print(f"\nReading Traceability Matrix: {trace_path}")
    with open(trace_path, "r", encoding="utf-8") as f:
        trace_data = json.load(f)
    print(f"Keys in trace_data: {list(trace_data.keys())}")
    print(f"Total Requirements in Traceability: {trace_data.get('total_requirements')}")
    print(f"Covered Requirements: {trace_data.get('covered_requirements')}")
    print(f"Coverage Percentage: {trace_data.get('coverage_percentage')}")
    
    matrix = trace_data.get('traceability_matrix', [])
    print(f"Traceability Matrix List Size: {len(matrix)}")
    if matrix:
        print("First 3 items in Traceability Matrix:")
        for idx, item in enumerate(matrix[:3]):
            print(f"  - Req ID {item.get('requirement_id')}: Title '{item.get('requirement_title')}' - Status: {item.get('status')}")
            print(f"    Linked Test Cases: {len(item.get('linked_testcases', []))}")
            for tc in item.get('linked_testcases', []):
                print(f"      - TC ID: {tc.get('testcase_id')}, Steps: {len(tc.get('steps', []))}, Val: {len(tc.get('validations', []))}")
else:
    print(f"Traceability Matrix file not found at: {trace_path}")
