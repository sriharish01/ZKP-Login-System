CREATE DATABASE ZKP; 

USE ZKP;

CREATE TABLE USERS(
	id int(11) NOT NULL AUTO_INCREMENT,
	username varchar(60) NOT NULL,
	password char(128) NOT NULL,
    email varchar(120) NOT NULL,
	PRIMARY KEY (id)
);



