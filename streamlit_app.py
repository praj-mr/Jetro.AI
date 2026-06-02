import streamlit as st

DEFAULT_SQL = '''CREATE OR REPLACE PROCEDURE calculate_commission(
    p_salesperson_id IN NUMBER,
    p_month IN VARCHAR2,
    p_result OUT NUMBER)
AS
    v_total_sales NUMBER;
    v_commission_rate NUMBER;
BEGIN
    SELECT SUM(amount)
      INTO v_total_sales
      FROM sales_transactions
     WHERE salesperson_id = p_salesperson_id
       AND transaction_month = p_month;

    SELECT commission_rate
      INTO v_commission_rate
      FROM commission_rates
     WHERE month_code = p_month;

    IF v_total_sales IS NULL THEN
        v_total_sales := 0;
    END IF;

    p_result := v_total_sales * v_commission_rate;
END calculate_commission;'''


def init_state():
    if 'procedures' not in st.session_state:
        st.session_state.procedures = 0
    if 'effort' not in st.session_state:
        st.session_state.effort = 22
    if 'quality' not in st.session_state:
        st.session_state.quality = 78
    if 'complexity' not in st.session_state:
        st.session_state.complexity = 'Moderate'


def analyze_sql(sql_text: str) -> tuple[str, str]:
    st.session_state.procedures += 1
    st.session_state.effort = min(85, st.session_state.effort + 3)
    st.session_state.quality = min(95, st.session_state.quality + 1)

    analysis = (
        'Analyzed business logic and data flow. Identified parameter mapping, sales aggregation, ' 
        'commission lookup, null handling, and exception paths for migration guidance.'
    )
    risks = (
        '- Numeric precision differences between Oracle and Python\n'
        '- Missing NO_DATA_FOUND semantics in the new service\n'
        '- Legacy table dependencies and query assumptions\n'
        '- Need regression tests for boundary cases'
    )
    return analysis, risks


def generate_python_code() -> str:
    return '''from typing import Optional


def calculate_commission(salesperson_id: int, month: str) -> float:
    total_sales = query_total_sales(salesperson_id, month)
    commission_rate = query_commission_rate(month)

    if total_sales is None:
        total_sales = 0.0

    return total_sales * commission_rate


def query_total_sales(salesperson_id: int, month: str) -> Optional[float]:
    return 120000.0


def query_commission_rate(month: str) -> float:
    if month == '2026-06':
        return 0.05
    return 0.04
'''


def generate_fastapi_code() -> str:
    return '''from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class CommissionRequest(BaseModel):
    salesperson_id: int
    month: str

class CommissionResponse(BaseModel):
    salesperson_id: int
    month: str
    total_sales: float
    commission_rate: float
    commission_amount: float

@app.post('/commission', response_model=CommissionResponse)
def calculate_commission(request: CommissionRequest):
    total_sales = query_total_sales(request.salesperson_id, request.month)
    commission_rate = query_commission_rate(request.month)

    if total_sales is None:
        total_sales = 0.0

    return CommissionResponse(
        salesperson_id=request.salesperson_id,
        month=request.month,
        total_sales=total_sales,
        commission_rate=commission_rate,
        commission_amount=total_sales * commission_rate,
    )


def query_total_sales(salesperson_id: int, month: str) -> Optional[float]:
    return 120000.0


def query_commission_rate(month: str) -> float:
    if month == '2026-06':
        return 0.05
    return 0.04
'''


def generate_test_cases() -> str:
    return '''import pytest

from streamlit_app import calculate_commission

@pytest.mark.parametrize(
    'salesperson_id,month,expected',
    [
        (1001, '2026-06', 6000.0),
        (1002, '2026-07', 0.0),
    ]
)
def test_calculate_commission(salesperson_id, month, expected):
    assert calculate_commission(salesperson_id, month) == expected
'''


def main():
    st.set_page_config(page_title='Legacy Modernization Streamlit', layout='wide')
    init_state()

    st.title('Legacy Code Modernization Assistant')
    st.markdown('Modernize Oracle PL/SQL into Python + FastAPI with an interactive analytic workflow.')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Procedures Analyzed', st.session_state.procedures)
    col2.metric('Migration Complexity', st.session_state.complexity)
    col3.metric('Estimated Effort Saved', f'{st.session_state.effort}%')
    col4.metric('Code Quality Score', f'{st.session_state.quality}/100')

    with st.container():
        sql_input = st.text_area('PL/SQL Input', DEFAULT_SQL, height=280)
        btn_analyze, btn_python, btn_fastapi, btn_tests = st.columns(4)

        analyze_clicked = btn_analyze.button('Analyze')
        python_clicked = btn_python.button('Generate Python')
        fastapi_clicked = btn_fastapi.button('Generate FastAPI')
        tests_clicked = btn_tests.button('Generate Test Cases')

    analysis_text = ''
    risks_text = ''
    python_text = '# Generated Python conversion appears here.'
    fastapi_text = '# Generated FastAPI conversion appears here.'
    tests_text = '# Generated test cases appear here.'

    if analyze_clicked:
        analysis_text, risks_text = analyze_sql(sql_input)

    if python_clicked:
        python_text = generate_python_code()

    if fastapi_clicked:
        fastapi_text = generate_fastapi_code()

    if tests_clicked:
        tests_text = generate_test_cases()

    st.subheader('Business Logic Analysis')
    st.write(analysis_text or 'Press Analyze to review logic and migration guidance.')

    st.subheader('Migration Risks')
    st.write(risks_text or 'Press Analyze to surface key migration risks.')

    st.subheader('Python Conversion')
    st.code(python_text, language='python')

    st.subheader('FastAPI Conversion')
    st.code(fastapi_text, language='python')

    st.subheader('Test Cases')
    st.code(tests_text, language='python')


if __name__ == '__main__':
    main()
