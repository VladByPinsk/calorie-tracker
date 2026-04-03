-- Creates all service databases and enables pgvector extension

CREATE DATABASE auth_db;
CREATE DATABASE user_db;
CREATE DATABASE food_db;
CREATE DATABASE diary_db;
CREATE DATABASE analytics_db;
CREATE DATABASE notification_db;

-- Enable pgvector in food_db (used for semantic food search)
\connect food_db
CREATE EXTENSION IF NOT EXISTS vector;

\connect auth_db
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\connect user_db
CREATE EXTENSION IF NOT EXISTS pgcrypto;
