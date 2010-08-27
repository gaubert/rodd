-- create RODD SCHEMA or DATABASE if not there
DROP SCHEMA IF EXISTS RODD; 
CREATE SCHEMA IF NOT EXISTS RODD;

USE RODD;

GRANT ALL PRIVILEGES on RODD.* to rodd@'localhost' IDENTIFIED BY 'ddor';
GRANT ALL PRIVILEGES on RODD.* to rodd@'localhost.localdomain' IDENTIFIED BY 'ddor';
-- add access from tclogin1
GRANT ALL PRIVILEGES on RODD.* to rodd@'10.11.0.130' IDENTIFIED BY 'ddor';

-- Drop all tables

DROP TABLE if EXISTS products;
DROP TABLE if EXISTS products_formats;
DROP TABLE if EXISTS format_type;


-- Create the tables

-- information regarding products
CREATE TABLE IF NOT EXISTS products (
    roddID INTEGER AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
	internalID VARCHAR(256),
	regularExpr VARCHAR(1024),
	status VARCHAR(256)
  );
  
-- information regarding the service directories
CREATE TABLE IF NOT EXISTS service_dirs (
    servID INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
	chanID VARCHAR(256)
  );

-- information regarding the service directories
CREATE TABLE IF NOT EXISTS products_2_servdirs (
    roddID INTEGER,
    servID INTEGER
  ); 
  
-- information regarding the channels
CREATE TABLE IF NOT EXISTS channels (
    chanID               INTEGER AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(1024),
    multicastAddress   VARCHAR(512),
    minRate            DOUBLE,
    maxRate            DOUBLE,
    channelFunction    VARCHAR(512),
    pidEB9             INTEGER,
    pidAB3             INTEGER,
    pidNSS             INTEGER
  ); 
  
-- information regarding the families
CREATE TABLE IF NOT EXISTS families (
    famID              INTEGER AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(512),
    description        VARCHAR(2048)
  ); 

-- information regarding the families
CREATE TABLE IF NOT EXISTS servdirs_2_families (
    servID             INTEGER,
    famID              INTEGER
  );
CREATE INDEX serv2fam_servid_index ON servdirs_2_families (servID);
CREATE INDEX serv2fam_famid_index ON servdirs_2_families (famID);
 
 
-- products formats to link the formats and the products
CREATE TABLE IF NOT EXISTS products_formats (
   roddID INTEGER PRIMARY KEY,
   formatTypeID INTEGER
);

-- format type
CREATE TABLE IF NOT EXISTS format_type (
   formatTypeID INTEGER AUTO_INCREMENT PRIMARY KEY,
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
   orbitID INTEGER AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(256)
);

INSERT into orbit_type (name) values("LEO");
INSERT into orbit_type (name) values("GEO");

-- status, instrument, frequency, should be expressed differently
-- for frequency, it will be very difficult



