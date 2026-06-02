from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

static_dir = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/', response_class=FileResponse)
def read_dashboard():
    return static_dir / 'index.html'

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
    try:
        total_sales = query_total_sales(request.salesperson_id, request.month)
        commission_rate = query_commission_rate(request.month)

        if total_sales is None:
            total_sales = 0.0

        commission_amount = total_sales * commission_rate

        return CommissionResponse(
            salesperson_id=request.salesperson_id,
            month=request.month,
            total_sales=total_sales,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Commission calculation failed: {exc}')


def query_total_sales(salesperson_id: int, month: str) -> Optional[float]:
    # Placeholder for the data access layer.
    return 120000.00


def query_commission_rate(month: str) -> float:
    # Placeholder for commission lookup logic.
    if month == '2026-06':
        return 0.05
    return 0.04
