DROP VIEW IF EXISTS datamart_variant_12;

CREATE VIEW datamart_variant_12 AS
SELECT 
    stockcode,
    description,
    invoicedate,
    quantity,
    country,
    total_amount as revenue,
    unitprice
FROM stg_online_retail
WHERE quantity > 0 AND unitprice > 0
GROUP BY 
    stockcode,
    description,
    invoicedate,
    quantity,
    country,
    total_amount,
    unitprice;