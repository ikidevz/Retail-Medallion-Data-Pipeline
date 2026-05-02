-- =============================================
-- SCHEMA SETUP
-- =============================================

-- Create the pipeline database
CREATE DATABASE retail_pipeline;

-- Connect to retail_pipeline
\c retail_pipeline

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Set default search path on pipeline DB
ALTER DATABASE retail_pipeline SET search_path TO bronze, silver, gold, public;

ALTER SCHEMA bronze OWNER TO CURRENT_USER;
ALTER SCHEMA silver OWNER TO CURRENT_USER;
ALTER SCHEMA gold OWNER TO CURRENT_USER;