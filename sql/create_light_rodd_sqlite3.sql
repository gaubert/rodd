-- create RODD SCHEMA or DATABASE if not there

DROP TABLE if EXISTS products;
DROP TABLE if EXISTS products_formats;
DROP TABLE if EXISTS format_type;
DROP TABLE if EXISTS file_info;
DROP TABLE if EXISTS channels;
DROP TABLE if EXISTS service_dirs;
DROP TABLE if EXISTS servdirs_2_families;
DROP TABLE if EXISTS file_2_servdirs;
DROP TABLE if EXISTS products_2_fileinfo;
DROP TABLE if EXISTS fileinfo_2_distribution;


-- Create the tables

-- users
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    login    VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email    VARCHAR(255) NOT NULL
  );

-- information regarding products
CREATE TABLE IF NOT EXISTS products (
    rodd_id         INTEGER PRIMARY KEY AUTOINCREMENT ,
	internal_id     VARCHAR(256) UNIQUE,
    title           VARCHAR(255) NOT NULL,
    description     VARCHAR(2048) NOT NULL,
	is_disseminated BOOLEAN,
	status          VARCHAR(256)
  );

-- information regarding the distributionTypes
CREATE TABLE IF NOT EXISTS distribution_type (
    dis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    geo  VARCHAR(255) NOT NULL
  );
  
INSERT into distribution_type (name, geo) values("eumetcast-info","world");
INSERT into distribution_type (name, geo) values("gts-info", "world");
INSERT into distribution_type (name, geo) values("direct-info", "world");
INSERT into distribution_type (name, geo) values("geonetcast-info", "world");
INSERT into distribution_type (name, geo) values("data-centre-info", "world");

-- information regarding the file_info
CREATE TABLE IF NOT EXISTS file_info (
    file_id    INTEGER PRIMARY KEY AUTOINCREMENT ,
    name       VARCHAR(255) UNIQUE NOT NULL,
    reg_expr   VARCHAR(255),
	size       VARCHAR(255),
	type       VARCHAR(255) NOT NULL
);

-- information regarding the channels
CREATE TABLE IF NOT EXISTS channels (
    chan_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name                VARCHAR(512) UNIQUE NOT NULL,
    multicast_address   VARCHAR(512),
    min_rate            INTEGER,
    max_rate            INTEGER,
    channel_function    VARCHAR(512),
    pid_EB9             INTEGER,
    pid_AB3             INTEGER,
    pid_NSS             INTEGER
  ); 

-- information regarding the service directories
CREATE TABLE IF NOT EXISTS service_dirs (
    serv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
	chan_id VARCHAR(256) NOT NULL 
);

-- relation between products and file_info
CREATE TABLE IF NOT EXISTS products_2_fileinfo (
    rodd_id INTEGER,
    file_id INTEGER
); 

-- relation between fileinfo and distributions
CREATE TABLE IF NOT EXISTS fileinfo_2_distribution (
    file_id INTEGER,
    dis_id  INTEGER
);
  
-- information regarding file2servdirs
CREATE TABLE IF NOT EXISTS file_2_servdirs (
    file_id INTEGER,
    serv_id INTEGER
); 
  
-- information regarding the families
CREATE TABLE IF NOT EXISTS families (
    fam_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name               VARCHAR(512),
    description        VARCHAR(2048)
  ); 

-- information regarding the families
CREATE TABLE IF NOT EXISTS servdirs_2_families (
    serv_id            INTEGER,
    fam_id             INTEGER
  );
CREATE INDEX IF NOT EXISTS serv2fam_servid_index ON servdirs_2_families (serv_id);
CREATE INDEX IF NOT EXISTS serv2fam_famid_index ON servdirs_2_families (fam_id);
 
 
-- products formats to link the formats and the products
CREATE TABLE IF NOT EXISTS products_formats (
   roddID INTEGER PRIMARY KEY,
   formatTypeID INTEGER
);

-- format type
CREATE TABLE IF NOT EXISTS format_type (
   format_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
   orbit_id INTEGER PRIMARY KEY AUTOINCREMENT,
   name VARCHAR(256)
);

INSERT into orbit_type (name) values("LEO");
INSERT into orbit_type (name) values("GEO");

-- status, instrument, frequency, should be expressed differently
-- for frequency, it will be very difficult



