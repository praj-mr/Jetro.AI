CREATE OR REPLACE PROCEDURE calculate_commission(
    p_salesperson_id IN NUMBER,
    p_month         IN VARCHAR2,
    p_result        OUT NUMBER)
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

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_result := 0;
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20001, 'Commission calculation failed: ' || SQLERRM);
END calculate_commission;
/