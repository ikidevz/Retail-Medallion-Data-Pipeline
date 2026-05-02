-- Seed a No Promo placeholder if not present
INSERT INTO gold.dim_promotion (
    promo_id, promo_name, promo_type,
    discount_rate, start_date, end_date
)
VALUES ('NO_PROMO', 'No Promotion', 'NONE', 0.00, '2000-01-01', '9999-12-31')
ON CONFLICT DO NOTHING;