-- Real-world PL/SQL examples for legacy transaction processing, reporting, and master data synchronization.

CREATE OR REPLACE PROCEDURE process_order_payment(
    p_order_id IN NUMBER,
    p_payment_amount IN NUMBER,
    p_processed_date IN DATE,
    p_result OUT VARCHAR2)
AS
    v_order_total NUMBER;
    v_balance_due NUMBER;
BEGIN
    SELECT total_amount, balance_due
      INTO v_order_total, v_balance_due
      FROM orders
     WHERE order_id = p_order_id
       AND order_status = 'CONFIRMED';

    IF v_balance_due IS NULL THEN
        v_balance_due := v_order_total;
    END IF;

    IF p_payment_amount <= 0 THEN
        p_result := 'INVALID_PAYMENT_AMOUNT';
        RETURN;
    END IF;

    IF p_payment_amount > v_balance_due THEN
        p_result := 'OVERPAYMENT_NOT_ALLOWED';
        RETURN;
    END IF;

    UPDATE orders
       SET balance_due = v_balance_due - p_payment_amount,
           last_payment_date = p_processed_date,
           order_status = CASE
                             WHEN v_balance_due - p_payment_amount = 0 THEN 'PAID'
                             ELSE 'PARTIAL'
                           END
     WHERE order_id = p_order_id;

    INSERT INTO order_payments(order_id, payment_amount, payment_date)
    VALUES(p_order_id, p_payment_amount, p_processed_date);

    p_result := 'PAYMENT_PROCESSED';
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_result := 'ORDER_NOT_FOUND';
    WHEN OTHERS THEN
        p_result := 'PAYMENT_ERROR:' || SQLERRM;
END process_order_payment;
/

CREATE OR REPLACE PROCEDURE generate_monthly_sales_report(
    p_report_month IN VARCHAR2,
    p_report_date IN DATE,
    p_result OUT VARCHAR2)
AS
BEGIN
    INSERT INTO monthly_sales_reports(report_month, report_date, total_sales, total_orders, created_at)
    SELECT p_report_month,
           p_report_date,
           SUM(amount),
           COUNT(DISTINCT order_id),
           SYSDATE
      FROM sales_transactions
     WHERE TO_CHAR(transaction_date, 'YYYY-MM') = p_report_month
       AND transaction_status = 'COMPLETED';

    p_result := 'REPORT_GENERATED';
EXCEPTION
    WHEN OTHERS THEN
        p_result := 'REPORT_ERROR:' || SQLERRM;
END generate_monthly_sales_report;
/

CREATE OR REPLACE PROCEDURE sync_customer_master(
    p_customer_id IN NUMBER,
    p_source_status IN VARCHAR2,
    p_result OUT VARCHAR2)
AS
BEGIN
    MERGE INTO customer_master tgt
    USING (
        SELECT customer_id, customer_name, address, email, phone, status
          FROM customer_staging
         WHERE customer_id = p_customer_id
           AND source_status = p_source_status
    ) src
    ON (tgt.customer_id = src.customer_id)
    WHEN MATCHED THEN
      UPDATE SET tgt.customer_name = src.customer_name,
                 tgt.address = src.address,
                 tgt.email = src.email,
                 tgt.phone = src.phone,
                 tgt.status = src.status,
                 tgt.updated_at = SYSDATE
    WHEN NOT MATCHED THEN
      INSERT (customer_id, customer_name, address, email, phone, status, created_at)
      VALUES (src.customer_id, src.customer_name, src.address, src.email, src.phone, src.status, SYSDATE);

    p_result := 'CUSTOMER_SYNCED';
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_result := 'CUSTOMER_NOT_FOUND';
    WHEN OTHERS THEN
        p_result := 'SYNC_ERROR:' || SQLERRM;
END sync_customer_master;
/