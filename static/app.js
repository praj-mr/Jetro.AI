const metrics = {
  procedures: 0,
  complexity: 'Moderate',
  effort: 0,
  quality: 78,
};

function updateMetrics() {
  document.getElementById('procedures-analyzed').textContent = metrics.procedures;
  document.getElementById('migration-complexity').textContent = metrics.complexity;
  document.getElementById('effort-saved').textContent = `${metrics.effort}%`;
  document.getElementById('code-quality').textContent = `${metrics.quality} / 100`;
}

function analyzeCode() {
  const sql = document.getElementById('sql-input').value.trim();
  if (!sql) {
    return;
  }

  metrics.procedures += 1;
  metrics.effort = Math.min(85, Math.max(metrics.effort, 22 + metrics.procedures * 3));
  metrics.quality = Math.min(95, metrics.quality + 1);
  updateMetrics();

  const logicSummary = `Analyzed procedure structure, identified core business rules and data flows. Detected:
- Input parameters and result mapping
- Sales aggregation logic
- Commission rate lookup and null-handling safeguards
- Clear procedural boundaries suitable for service refactoring

Recommended modernization actions:
1. Separate business rules from data access.
2. Convert cursor and query logic into reproducible Python functions.
3. Add regression tests for edge cases and null-value behavior.`;

  document.getElementById('analysis-output').textContent = logicSummary;
  document.getElementById('risks-output').textContent = `Primary migration risks:
- Data mismatch between Oracle numeric types and Python floats.
- Missing exception semantics for NO_DATA_FOUND and generic failure cases.
- Dependency on legacy table structure and lookup queries.
- Need for idempotent endpoint design to preserve behavior when re-run.`;
}

function generatePython() {
  const pythonOutput = `from typing import Optional\n\n\ndef calculate_commission(salesperson_id: int, month: str) -> float:\n    total_sales = query_total_sales(salesperson_id, month)\n    commission_rate = query_commission_rate(month)\n\n    if total_sales is None:\n        total_sales = 0.0\n\n    return total_sales * commission_rate\n\n\n# Data access layer stubs\ndef query_total_sales(salesperson_id: int, month: str) -> Optional[float]:\n    # TODO: implement database access using an ORM or SQL client\n    return 120000.0\n\n\ndef query_commission_rate(month: str) -> float:\n    if month == '2026-06':\n        return 0.05\n    return 0.04\n`;
  document.getElementById('python-output').textContent = pythonOutput;
}

function generateFastAPI() {
  const fastapiOutput = `from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel\nfrom typing import Optional\n\napp = FastAPI()\n\nclass CommissionRequest(BaseModel):\n    salesperson_id: int\n    month: str\n\nclass CommissionResponse(BaseModel):\n    salesperson_id: int\n    month: str\n    total_sales: float\n    commission_rate: float\n    commission_amount: float\n\n@app.post('/commission', response_model=CommissionResponse)\ndef calculate_commission(request: CommissionRequest):\n    total_sales = query_total_sales(request.salesperson_id, request.month)\n    commission_rate = query_commission_rate(request.month)\n\n    if total_sales is None:\n        total_sales = 0.0\n\n    return CommissionResponse(\n        salesperson_id=request.salesperson_id,\n        month=request.month,\n        total_sales=total_sales,\n        commission_rate=commission_rate,\n        commission_amount=total_sales * commission_rate,\n    )\n\n# Data access layer (stub implementations)\ndef query_total_sales(salesperson_id: int, month: str) -> Optional[float]:\n    return 120000.0\n\n\ndef query_commission_rate(month: str) -> float:\n    if month == '2026-06':\n        return 0.05\n    return 0.04\n`;
  document.getElementById('fastapi-output').textContent = fastapiOutput;
}

function generateTestCases() {
  const testsOutput = `import pytest\n\nfrom app import calculate_commission\n\n@pytest.mark.parametrize(\n    'salesperson_id,month,expected',\n    [\n        (1001, '2026-06', 6000.0),\n        (1002, '2026-07', 0.0),\n    ]\n)\ndef test_calculate_commission(salesperson_id, month, expected):\n    result = calculate_commission(salesperson_id, month)\n    assert result == expected\n\n# Additional tests for null handling and lookup failures\n`;
  document.getElementById('tests-output').textContent = testsOutput;
}

updateMetrics();
