# Agentic AI Requirements-to-Test Traceability Pipeline

This repository contains a portable, read-only analysis pipeline that extracts software requirements, generates test scenarios, maps requirements to ETM test cases, and exports the results to Excel.

The master orchestrator runs three stages:

1. **Agent 1 - Requirement Decoder:** Reads requirements from DNG or a local Excel/CSV file and generates positive, negative, and boundary scenarios.
2. **Agent 2 - Traceability Mapper:** Compares the decoded requirements with an ETM test-case PDF and records coverage, test-case IDs, objectives, steps, and validations.
3. **Agent 3 - Excel Report Generator:** Converts the traceability JSON into a formatted `traceability_report.xlsx` workbook.

The pipeline only reads from DNG and ETM. Its generated JSON and Excel files are written locally.

## Repository Structure

```text
Agentic_AI/
├── README.md
├── How to Use Scripts.txt       # Restructuring notes and historical usage guidance
├── agents/                      # Gemini CLI agent definitions
│   ├── master-orchestrator.md
│   ├── requirement-decoder.md
│   ├── traceability-mapper.md
│   └── excel-report-generator.md
├── scripts/
│   ├── config.py                # Shared paths and DNG/Gemini configuration
│   ├── agent_0_master_orchestrator.py
│   ├── agent_1_requirement_understanding.py
│   ├── agent_2_traceability_mapper.py
│   ├── agent_3_excel_report_generator.py
│   ├── analyze_mcu_sheet.py     # Inspect workbook headings and MCU ranges
│   ├── check_mcu_columns.py     # Inspect workbook columns and section values
│   ├── copy_scripts.py          # Copy/deployment helper
│   ├── extract_run_timings.py   # Inspect Gemini run timings
│   ├── parse_logs_workspace.py   # Inspect Gemini chat logs
│   └── read_temp_outputs.py     # Summarize generated JSON outputs
└── workspace/                   # Runtime outputs; created automatically
    ├── decoded_requirements.json
    ├── traceability_matrix.json
    └── traceability_report.xlsx
```

## Prerequisites

- Windows with Python 3.x available as `python`.
- Node.js and the Gemini CLI:

  ```powershell
  npm install -g @google/gemini-cli
  ```

- Python packages:

  ```powershell
  python -m pip install openpyxl requests urllib3
  ```

- For Gemini agent invocation, copy the files from `agents\` to `%USERPROFILE%\.gemini\agents\`.
- For online DNG mode, the DNG `oslcquery.exe` executable must be available at the location resolved by `scripts\config.py`.

## Run the Complete Pipeline

Run commands from the `scripts` directory, or provide paths explicitly.

### Offline mode

Offline mode uses a local `.xlsx` or `.csv` requirements file and does not query DNG. The ETM PDF is still required for mapping.

```powershell
cd D:\FIT\Agentic_AI\scripts
python .\agent_0_master_orchestrator.py `
  --offline `
  --input-file "D:\path\MCU_Update_Requirement.xlsx" `
  --section "MCU" `
  --test-pdf "D:\path\Iveco_Mcu_Update.pdf"
```

### Online mode

Online mode queries DNG using the project, component, configuration, module, and section values supplied on the command line.

```powershell
cd D:\FIT\Agentic_AI\scripts
$env:DNG_USERNAME = "your_username"
$env:DNG_PASSWORD = "your_password"
python .\agent_0_master_orchestrator.py `
  --project "NEO" `
  --component "NEO" `
  --config "DNG NEO Stream" `
  --module "SWRS Update" `
  --section "MCU" `
  --test-pdf "D:\path\Iveco_Mcu_Update.pdf"
```

Use `python .\agent_0_master_orchestrator.py --help` for all options. Defaults are `NEO` for project and component, `DNG NEO Stream` for configuration, and `MCU` for section. `--test-pdf` is required.

## Run Individual Stages

The stages can also be run independently when intermediate files already exist:

```powershell
python .\agent_1_requirement_understanding.py --offline `
  --input-file "D:\path\requirements.xlsx" --section "MCU"

python .\agent_2_traceability_mapper.py `
  --req-json "..\workspace\decoded_requirements.json" `
  --test-pdf "D:\path\Iveco_Mcu_Update.pdf" `
  --output "..\workspace\traceability_matrix.json"

python .\agent_3_excel_report_generator.py `
  --input-json "..\workspace\traceability_matrix.json" `
  --output-excel "..\workspace\traceability_report.xlsx"
```

## Generated Artifacts

All orchestrated outputs are stored in `workspace`, whose path is resolved by `config.py` relative to this repository:

- `decoded_requirements.json`: requirement IDs, titles, functional scope, and generated scenarios.
- `traceability_matrix.json`: total and covered requirement counts, coverage percentage, and linked ETM test cases.
- `traceability_report.xlsx`: formatted Excel report with requirement status, mapped test cases, and coverage status.

## Inspection Utilities

The utility scripts do not run the full pipeline. They help inspect inputs and existing outputs:

- `analyze_mcu_sheet.py <workbook>` lists headings and requirements in the MCU section.
- `check_mcu_columns.py <workbook>` reports workbook columns and section values.
- `read_temp_outputs.py` summarizes JSON files in `workspace`.
- `parse_logs_workspace.py` and `extract_run_timings.py` inspect local Gemini session logs.

Example:

```powershell
python .\analyze_mcu_sheet.py "D:\path\MCU_Update_Requirement.xlsx"
python .\read_temp_outputs.py
```

## Configuration Notes

`scripts\config.py` calculates the repository base path, creates `workspace` when needed, resolves the Gemini CLI from `%APPDATA%`, and reads these optional environment variables:

- `DNG_SERVER` (defaults to `https://rb-alm-20-p.de.bosch.com`)
- `DNG_USERNAME`
- `DNG_PASSWORD`

Do not commit credentials or downloaded source documents to this repository.
