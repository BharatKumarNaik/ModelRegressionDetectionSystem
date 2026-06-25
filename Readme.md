Developer Changes Prompt/Model
          │
          ▼

 GitHub Action Triggered

          │
          ▼

 Load Golden Dataset

          │
          ▼

 Execute Test Cases (Async)

          │
          ▼

 Collect Metrics
    - Exact Match
    - LLM Judge Score
    - Latency
    - Token Usage

          │
          ▼

 Compare Against Baseline

          │
          ▼

 Regression Detected?

    YES            NO
     │              │
     ▼              ▼

 Email Alert     Pass CI
 Fail Pipeline