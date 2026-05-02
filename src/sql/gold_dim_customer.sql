-- Seed a placeholder Unknown customer if not present
-- (sales currently don't capture customer_id; extend later)
INSERT INTO gold.dim_customer (
    customer_id, first_name, last_name,
    membership_tier, join_date, city, region
)
VALUES ('UNKNOWN', 'Unknown', 'Customer', 'Bronze', '2020-01-01', 'Manila', 'NCR')
ON CONFLICT DO NOTHING;