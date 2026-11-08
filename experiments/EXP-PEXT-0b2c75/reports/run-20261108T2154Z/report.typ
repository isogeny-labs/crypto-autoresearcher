#set page(paper: "a4", margin: 15mm)
#set text(size: 9pt)
#text(size: 15pt, weight: "bold")[Run report: EXP-PEXT-0b2c75]
#image("graph.svg", width: 100%)

#text("Hypothesis H-PEXT-ad0073; goal GOAL-PEXT-4a1d6b. Run RUN-PEXT-8c15bf; trial regression. Raw records: experiments/EXP-PEXT-0b2c75/runs/RUN-PEXT-8c15bf")

#text("6 planned trials, 1 attempted, 0 output-validated, 5 dependent trials not launched. Process exit 0; no timeout. Supervisor status: invalid_output; independent output checker did not run. The driver manifest says completed_valid, which is not supervisor acceptance.")

#text("Failure: driver manifest run.code.commit='817c782d25bfe62af22f3639dd53fc267f8bb89c' contradicts the launch authority's '69c7a6aaec914916af6a3a967ccb93ac4b00da1f'")

#text("This session committed the earlier SEMBIN report during execution, changing HEAD. The invalid attempt is preserved. No frozen plan or existing output was modified.")

#text("Authority commit: 69c7a6aaec914916af6a3a967ccb93ac4b00da1f; driver commit: 817c782d25bfe62af22f3639dd53fc267f8bb89c; driver dirty state: False")

#text("Measured wall time 3.135 s; CPU 4.538 s; peak RSS 232861696 bytes. Host 4521696e89cd; Python 3.12.14; rustc 1.99.1 (58cf8f9c3 2026-10-13).")

#text("Seed 20261101; threads 4. Parameters and declared controls are unchanged from trial-plan.json. This was the regression/control stage. No independent certificate validation or uncertainty assessment completed.")

#text("Exact command: [\"python3\", \"experiments/EXP-PEXT-0b2c75/implementation/run.py\", \"trial\", \"--run-dir\", \"/workspace/crypto-autoresearcher/experiments/EXP-PEXT-0b2c75/runs/RUN-PEXT-8c15bf\", \"--run-id\", \"RUN-PEXT-8c15bf\", \"--trial-id\", \"regression\", \"--plan\", \"experiments/EXP-PEXT-0b2c75/trial-plan.json\"]")

#text("Raw outputs: regression.json, raw-result.json, R-n5-q3.jsonl, R-fix-n5-q3.jsonl. All log and environment files are retained beside execution-receipt.json. The diagram shows the execution sequence because there are no comparative measurements.")

#text("Next diagnostic: reconcile this invalid attempt through experiment preparation; isolate future execution from commits to HEAD. Do not reuse the immutable run directory.")

#text("Operational sources checked: README.md, the run skill, selected trial plan, specification and implementation. No new scientific method, novelty claim or mathematical literature assessment is made. Canonical scientific graphs are unchanged; the report records an infrastructure failure.")