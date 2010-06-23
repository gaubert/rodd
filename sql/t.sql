use rodd;

DROP TABLE IF EXISTS format_type;
DROP TABLE IF EXISTS products_formats;


CREATE TABLE IF NOT EXISTS products_formats (
   roddID INTEGER PRIMARY KEY,
   formatTypeID INTEGER
);

CREATE TABLE IF NOT EXISTS format_type (
   formatTypeID INTEGER AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(256),
   description VARCHAR(1024)
);
