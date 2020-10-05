-- File with create table statements to initialize database.

-- SQLITE3

-- authorizations table.
CREATE TABLE "authorization" (
	"authorization"	TEXT,
	"maillist"	TEXT,
	"subscriptor"	TEXT,
	PRIMARY KEY("authorization")
);

-- maillists table.
CREATE TABLE "maillists" (
	"maillist"	TEXT,
	"administrator"	TEXT,
	"bounce_list" INTEGER NOT NULL DEFAULT 0 CHECK(bounce_list IN (0,1)),
	"distribution_list"	INTEGER NOT NULL DEFAULT 0 CHECK(distribution_list IN (0,1)),
	"delegated_subscription" INTEGER NOT NULL DEFAULT 0 CHECK(delegated_subscription IN(0,1)),
	"require_subscription_auth" INTEGER NOT NULL DEFAULT 0 CHECK(bounce_list IN (0,1)),
	PRIMARY KEY("maillist")
);

-- subscripions table.
CREATE TABLE "subscriptions" (
	"maillist"	TEXT,
	"subscriptor"	TEXT,
	PRIMARY KEY("maillist","subscriptor")
);
CREATE INDEX "subscriptions_maillists" ON "subscriptions" ( "maillist" );