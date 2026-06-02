from datetime import date
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, select, update, insert

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/modernization"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI(title='AI Migration Assistant API')

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(12, 2), nullable=False)
    balance_due = Column(Numeric(12, 2), nullable=False)
    last_payment_date = Column(Date)
    order_status = Column(String(20), nullable=False)

class OrderPayment(Base):
    __tablename__ = 'order_payments'

    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    payment_amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)

class SalesTransaction(Base):
    __tablename__ = 'sales_transactions'

    transaction_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_status = Column(String(20), nullable=False)

class MonthlySalesReport(Base):
    __tablename__ = 'monthly_sales_reports'

    report_id = Column(Integer, primary_key=True)
    report_month = Column(String(7), nullable=False)
    report_date = Column(Date, nullable=False)
    total_sales = Column(Numeric(14, 2), nullable=False)
    total_orders = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

class CustomerMaster(Base):
    __tablename__ = 'customer_master'

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False)
    address = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

class CustomerStaging(Base):
    __tablename__ = 'customer_staging'

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False)
    address = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    status = Column(String(50), nullable=False)
    source_status = Column(String(50), nullable=False)

class PaymentRequest(BaseModel):
    payment_amount: float = Field(..., gt=0)
    processed_date: date

class PaymentResponse(BaseModel):
    order_id: int
    payment_amount: float
    remaining_balance: float
    order_status: str
    message: str

class SalesReportResponse(BaseModel):
    report_month: str
    report_date: date
    total_sales: float
    total_orders: int

class CustomerSyncRequest(BaseModel):
    customer_id: int
    source_status: str

class CustomerSyncResponse(BaseModel):
    customer_id: int
    status: str
    message: str

@app.post('/orders/{order_id}/process-payment', response_model=PaymentResponse)
def process_order_payment(order_id: int, payload: PaymentRequest):
    with SessionLocal() as session:
        order = session.get(Order, order_id)
        if not order or order.order_status != 'CONFIRMED':
            raise HTTPException(status_code=404, detail='Order not found or not in confirmed state')

        balance_due = order.balance_due or order.total_amount
        if payload.payment_amount > balance_due:
            raise HTTPException(status_code=400, detail='Payment amount exceeds outstanding balance')

        order.balance_due = balance_due - payload.payment_amount
        order.last_payment_date = payload.processed_date
        order.order_status = 'PAID' if order.balance_due == 0 else 'PARTIAL'
        session.add(order)

        payment = OrderPayment(
            order_id=order_id,
            payment_amount=payload.payment_amount,
            payment_date=payload.processed_date,
        )
        session.add(payment)
        session.commit()

        return PaymentResponse(
            order_id=order_id,
            payment_amount=payload.payment_amount,
            remaining_balance=float(order.balance_due),
            order_status=order.order_status,
            message='PAYMENT_PROCESSED',
        )

@app.post('/reports/monthly-sales', response_model=SalesReportResponse)
def generate_monthly_sales_report(report_month: str = Query(..., regex='^\\d{4}-\\d{2}$')):
    report_date = date.today()
    with SessionLocal() as session:
        query = select(
            func.coalesce(func.sum(SalesTransaction.amount), 0).label('total_sales'),
            func.count(func.distinct(SalesTransaction.order_id)).label('total_orders'),
        ).where(
            func.to_char(SalesTransaction.transaction_date, 'YYYY-MM') == report_month,
            SalesTransaction.transaction_status == 'COMPLETED',
        )

        result = session.execute(query).one()
        total_sales = float(result.total_sales or 0)
        total_orders = int(result.total_orders or 0)

        report = MonthlySalesReport(
            report_month=report_month,
            report_date=report_date,
            total_sales=total_sales,
            total_orders=total_orders,
            created_at=func.now(),
        )
        session.add(report)
        session.commit()

        return SalesReportResponse(
            report_month=report_month,
            report_date=report_date,
            total_sales=total_sales,
            total_orders=total_orders,
        )

@app.post('/customers/sync', response_model=CustomerSyncResponse)
def sync_customer_master(payload: CustomerSyncRequest):
    with SessionLocal() as session:
        staging = session.get(CustomerStaging, payload.customer_id)
        if not staging or staging.source_status != payload.source_status:
            raise HTTPException(status_code=404, detail='Customer staging record not found')

        customer = session.get(CustomerMaster, payload.customer_id)
        if customer:
            customer.customer_name = staging.customer_name
            customer.address = staging.address
            customer.email = staging.email
            customer.phone = staging.phone
            customer.status = staging.status
            customer.updated_at = func.now()
            message = 'CUSTOMER_UPDATED'
        else:
            customer = CustomerMaster(
                customer_id=staging.customer_id,
                customer_name=staging.customer_name,
                address=staging.address,
                email=staging.email,
                phone=staging.phone,
                status=staging.status,
                created_at=func.now(),
            )
            session.add(customer)
            message = 'CUSTOMER_CREATED'

        session.commit()
        return CustomerSyncResponse(
            customer_id=payload.customer_id,
            status=customer.status,
            message=message,
        )

# Note: In a production conversion, add transaction management, error translation,
# logging, and model validation for database fields.