-- File with create table statements to initialize database.

-- SQLITE3

-- subscripions table.
CREATE TABLE `subscriptions` 
( `maillist` TEXT, `subscriptor` INTEGER, PRIMARY KEY(`maillist`,`subscriptor`) );
CREATE INDEX `subscriptions_maillists` ON `subscriptions` ( `maillist` );

-- private lists table.
CREATE TABLE `private`
( `maillist` TEXT, `administrator` INTEGER, PRIMARY KEY(`maillist`,`administrator`) );
CREATE INDEX `private_maillist` ON `private` ( `maillist` );

-- authorizations table.
CREATE TABLE `authorization`
( `authorization` TEXT, `maillist` TEXT, `subscriptor` INTEGER, PRIMARY KEY(`authorization`) );


