## File with create table statements to initialize database.

## SQLITE3
# subscripions table.
CREATE TABLE `subscriptions` 
( `maillist` TEXT, `subscriptor` INTEGER, PRIMARY KEY(`maillist`,`subscriptor`) );
CREATE INDEX `maillists` ON `subscriptions` ( `maillist` );
