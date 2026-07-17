from datetime import datetime
from src.config.settings import REPORT_DIR
import os

class ReportGenerator:
    def __init__(self, regression_report):
        self.report = regression_report

    def generate_html(self,):
        total_tests = len(self.report)
        sql_regressions = 0
        answer_regressions = 0
        latency_regressions = 0
        token_regressions = 0
        overall_regressions = 0

        for tc in self.report:
            if tc["sql_match"]["regression"]:
                sql_regressions += 1
            if tc["answer_similarity"]["regression"]:
                answer_regressions += 1
            if tc["latency"]["regression"]:
                latency_regressions += 1
            if tc["tokens"]["regression"]:
                token_regressions += 1
            if tc["overall_regression"]:
                overall_regressions += 1

        pass_rate = (
            (total_tests - overall_regressions)
            / total_tests
            * 100
        )

        html = f"""
<!DOCTYPE html>
<html>
<head>

<title>Model Regression Report</title>

<style>

body{{
font-family:Arial;
background:#f5f5f5;
padding:30px;
}}

h1{{
text-align:center;
}}

.summary{{
display:flex;
gap:20px;
margin-bottom:30px;
}}

.card{{
background:white;
padding:20px;
border-radius:10px;
box-shadow:0 2px 8px rgba(0,0,0,.1);
flex:1;
text-align:center;
}}

table{{
width:100%;
border-collapse:collapse;
background:white;
}}

th{{
background:#1f2937;
color:white;
padding:12px;
}}

td{{
padding:10px;
text-align:center;
border-bottom:1px solid #ddd;
}}

.regression{{
color:red;
font-weight:bold;
}}

.ok{{
color:green;
font-weight:bold;
}}

</style>

</head>

<body>

<h1>LLM Regression Report</h1>

<p>
Generated :
{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
</p>

<div class="summary">

<div class="card">
<h2>{total_tests}</h2>
<p>Total Tests</p>
</div>

<div class="card">
<h2>{pass_rate:.2f}%</h2>
<p>Pass Rate</p>
</div>

<div class="card">
<h2>{overall_regressions}</h2>
<p>Overall Regressions</p>
</div>

<div class="card">
<h2>{sql_regressions}</h2>
<p>SQL Regressions</p>
</div>

<div class="card">
<h2>{answer_regressions}</h2>
<p>Answer Regressions</p>
</div>

<div class="card">
<h2>{latency_regressions}</h2>
<p>Latency Regressions</p>
</div>

<div class="card">
<h2>{token_regressions}</h2>
<p>Token Regressions</p>
</div>
</div>

<table>
<tr>
    <th>ID</th>
    <th>SQL Match</th>
    <th>SQL Result</th>
    <th>Answer</th>
    <th>Latency</th>
    <th>Tokens</th>
    <th>Overall</th>
</tr>
"""

        for tc in self.report:
            sql = (
                "❌"
                if tc["sql_match"]["regression"]
                else "✅"
            )
            sql_result = (
                "❌"
                if tc["sql_result"]["regression"]
                else "✅"
            )
            answer = (
                "❌"
                if tc["answer_similarity"]["regression"]
                else "✅"
            )
            latency = (
                "❌"
                if tc["latency"]["regression"]
                else "✅"
            )
            token = (
                "❌"
                if tc["tokens"]["regression"]
                else "✅"
            )
            overall = (
                "<span class='regression'>FAILED</span>"
                if tc["overall_regression"]
                else "<span class='ok'>PASSED</span>"
            )
            html += f"""
<tr>
<td>{tc['id']}</td>
<td>
{sql}
<br>
{tc['sql_match']['baseline']:.2f}
→
{tc['sql_match']['current']:.2f}
</td>

<td>
    {sql_result}
    <br>
    {tc['sql_result']['baseline']:.2f}
    →
    {tc['sql_result']['current']:.2f}
</td>

<td>
{answer}
<br>
{tc['answer_similarity']['baseline']:.2f}
→
{tc['answer_similarity']['current']:.2f}
</td>
<td>{latency}</td>
<td>{token}</td>
<td>{overall}</td>
</tr>
"""

        html += """
</table>
</body>
</html>
"""
        file_name = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.html"
        output_file = os.path.join(REPORT_DIR,file_name)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Report saved to {output_file}")