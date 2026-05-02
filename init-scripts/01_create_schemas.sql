-- =============================================
-- SCHEMA SETUP
-- =============================================

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Set default search path
ALTER DATABASE airflow SET search_path TO bronze, silver, gold, public;

ALTER SCHEMA bronze OWNER TO CURRENT_USER;
ALTER SCHEMA silver OWNER TO CURRENT_USER;
ALTER SCHEMA gold OWNER TO CURRENT_USER;