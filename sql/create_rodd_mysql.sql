-- create RODD SCHEMA or DATABASE if not there
DROP SCHEMA IF EXISTS rodd; 
CREATE SCHEMA IF NOT EXISTS rodd;

USE RODD;

-- Drop all tables

DROP TABLE if EXISTS products;


-- Create the tables
CREATE TABLE IF NOT EXISTS products (
    roddid INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    onEumetcast BOOLEAN DEFAULT FALSE,
    onGts BOOLEAN DEFAULT FALSE,
    onMsgDirect BOOLEAN DEFAULT FALSE,
    generalComments VARCHAR(1024)
  );
