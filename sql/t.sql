use rodd;

DROP TABLE IF EXISTS format_type;


CREATE TABLE IF NOT EXISTS format_type (
   formatTypeID INTEGER  NOT NULL AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(256),
   description VARCHAR(1024)
--   PRIMARY KEY(formatTypeID)
);

