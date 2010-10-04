-- create RODD SCHEMA or DATABASE if not there
DROP SCHEMA IF EXISTS RODD; 
CREATE SCHEMA IF NOT EXISTS RODD;

USE RODD;

GRANT ALL PRIVILEGES on RODD.* to rodd@'localhost' IDENTIFIED BY 'ddor';
GRANT ALL PRIVILEGES on RODD.* to rodd@'localhost.localdomain' IDENTIFIED BY 'ddor';
-- add access from tclogin1
GRANT ALL PRIVILEGES on RODD.* to rodd@'10.11.0.130' IDENTIFIED BY 'ddor';
GRANT ALL PRIVILEGES on RODD.* to rodd@'tclogin1' IDENTIFIED BY 'ddor';

-- Drop all tables

DROP TABLE if EXISTS products;
DROP TABLE if EXISTS products_formats;
DROP TABLE if EXISTS format_type;
DROP TABLE if EXISTS file_info;


-- Create the tables

-- users
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER AUTO_INCREMENT PRIMARY KEY,
    login    VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email    VARCHAR(255) NOT NULL
  );

-- information regarding products
CREATE TABLE IF NOT EXISTS products (
    rodd_id         INTEGER AUTO_INCREMENT PRIMARY KEY,
	internal_id     VARCHAR(256) UNIQUE,
    title           VARCHAR(255) NOT NULL,
    description     VARCHAR(2048) NOT NULL,
	is_disseminated BOOLEAN,
	status          VARCHAR(256)
  );

-- information regarding the distributionTypes
CREATE TABLE IF NOT EXISTS distribution_type (
    dis_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
  );
  
INSERT into distribution_type (name) values("EUMETCAST"),("GTS"),("DIRECT"),("GEONETCAST"),("ARCHIVE");

-- information regarding the file_info
CREATE TABLE IF NOT EXISTS file_info (
    file_id    INTEGER AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) UNIQUE NOT NULL,
    reg_expr   VARCHAR(255),
	size       VARCHAR(255),
	type       VARCHAR(255) NOT NULL
);

-- information regarding the channels
CREATE TABLE IF NOT EXISTS channels (
    chan_id             INTEGER AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(512) UNIQUE NOT NULL,
    multicast_address   VARCHAR(512),
    min_rate            DOUBLE,
    max_rate            DOUBLE,
    channel_function    VARCHAR(512),
    pid_EB9             INTEGER,
    pid_AB3             INTEGER,
    pid_NSS             INTEGER
  ); 

-- information regarding the service directories
CREATE TABLE IF NOT EXISTS service_dirs (
    serv_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
	chan_id VARCHAR(256) NOT NULL
);

-- information regarding the distribution
CREATE TABLE IF NOT EXISTS products_2_distribution (
    rodd_id INTEGER,
    dis_id INTEGER
); 

-- information to create relation between products and fileinfos for products using EUMETCAST
CREATE TABLE IF NOT EXISTS products_2_eumetcast (
    rodd_id INTEGER,
    file_id INTEGER
);

-- information to create relation between products and fileinfos for products using GTS
CREATE TABLE IF NOT EXISTS products_2_gts (
    rodd_id INTEGER,
    file_id INTEGER
);

-- information to create relation between products and fileinfos for products using GEONETCAST
CREATE TABLE IF NOT EXISTS products_2_geonetcast (
    rodd_id INTEGER,
    file_id INTEGER
);

-- information to create relation between products and fileinfos for products using DATA CENTRE
CREATE TABLE IF NOT EXISTS products_2_data_centre (
    rodd_id INTEGER,
    file_id INTEGER
);
  
-- information regarding file2servdirs
CREATE TABLE IF NOT EXISTS file_2_servdirs (
    file_id INTEGER,
    serv_id INTEGER
); 
  
-- information regarding the families
CREATE TABLE IF NOT EXISTS families (
    fam_id              INTEGER AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(512),
    description        VARCHAR(2048)
  ); 

-- information regarding the families
CREATE TABLE IF NOT EXISTS servdirs_2_families (
    serv_id            INTEGER,
    fam_id             INTEGER
  );
CREATE INDEX serv2fam_servid_index ON servdirs_2_families (serv_id);
CREATE INDEX serv2fam_famid_index ON servdirs_2_families (fam_id);
 
 
-- products formats to link the formats and the products
CREATE TABLE IF NOT EXISTS products_formats (
   roddID INTEGER PRIMARY KEY,
   formatTypeID INTEGER
);

-- format type
CREATE TABLE IF NOT EXISTS format_type (
   format_id INTEGER AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(256),
   description VARCHAR(1024)
);

-- insert the different format types
INSERT into format_type (name) values("AAPP");
INSERT into format_type (name,description) values("ASCII","ASCII file");
INSERT into format_type (name) values("AWX");
INSERT into format_type (name,description) values("BZIP2-BUFR","Bzip2 compressed BUFR");
INSERT into format_type (name) values("BUFR");
INSERT into format_type (name) values("GEOTIFF");
INSERT into format_type (name) values("GIF");
INSERT into format_type (name) values("GRIB");
INSERT into format_type (name) values("HDF");
INSERT into format_type (name) values("HDF5");
INSERT into format_type (name) values("HDF-EOS");
INSERT into format_type (name,description) values("BZIP2-HRPT","Raw HRPT bzip2 compressed");
INSERT into format_type (name,description) values("HRIT","Lossless wavelet compressed");
INSERT into format_type (name) values("JPEG");
INSERT into format_type (name) values("Lossy JPEG");
INSERT into format_type (name,description) values("LRIT","Wavelet compressed");
INSERT into format_type (name) values("MPEG");
INSERT into format_type (name) values("Native Binary");
INSERT into format_type (name) values("NetCDF");
INSERT into format_type (name) values("PFS");
INSERT into format_type (name) values("PNG");
INSERT into format_type (name) values("Shape");
INSERT into format_type (name,description) values("LRIT-WMO","WMO GTS in LRIT");

-- orbit type
CREATE TABLE IF NOT EXISTS orbit_type (
   orbit_id INTEGER AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(256)
);

INSERT into orbit_type (name) values("LEO");
INSERT into orbit_type (name) values("GEO");

-- status, instrument, frequency, should be expressed differently
-- for frequency, it will be very difficult



