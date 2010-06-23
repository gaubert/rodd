-- create RODD SCHEMA or DATABASE if not there
DROP SCHEMA IF EXISTS rodd; 
CREATE SCHEMA IF NOT EXISTS rodd;

USE RODD;

-- GRANT ALL PRIVILEGES on rodd.* to 'rodd@localhost' IDENTIFIED BY 'ddor';
-- GRANT ALL PRIVILEGES on rodd.* to 'rodd@localhost.localdomain' IDENTIFIED BY 'ddor';

-- Drop all tables

DROP TABLE if EXISTS products;
DROP TABLE if EXISTS products_formats;
DROP TABLE if EXISTS format_type;


-- Create the tables

-- information regarding the products
CREATE TABLE IF NOT EXISTS products (
    roddID INTEGER AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    onEumetcast BOOLEAN DEFAULT FALSE,
    onGts BOOLEAN DEFAULT FALSE,
    onMsgDirect BOOLEAN DEFAULT FALSE,
    generalComments VARCHAR(1024),
	internalID VARCHAR(256),
	acronym VARCHAR(512),
	aka VARCHAR(256),
	source VARCHAR(256),
	category VARCHAR(256),
	channel VARCHAR(1024),
	descKeywordDiscipline VARCHAR(256),
	descKeywordPlace VARCHAR(256),
	dissemination VARCHAR(1024),
	hrpt_dir BOOLEAN DEFAULT FALSE,
    filesize VARCHAR(1024),
	oicd VARCHAR(256),
	frequency VARCHAR(256),
	instrument VARCHAR(512),
	link VARCHAR(1024),
	regularExpr VARCHAR(1024),
	namingConvention VARCHAR(1024),
	orbitType INTEGER,
	parameter VARCHAR(256),
	provider VARCHAR(256),
	referenceFile VARCHAR(512),
	resolution INTEGER,
	resources VARCHAR(512),
	satellite VARCHAR(256),
	status VARCHAR(256)
  );

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
   name VARCHAR(256),
);

INSERT into orbit_type (name) values("LEO");
INSERT into orbit_type (name) values("GEO");

-- status, instrument, frequency, should be expressed differently
-- for frequency, it will be very difficult

