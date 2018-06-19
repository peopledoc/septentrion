BEGIN;

    CREATE TABLE "north_app_reader" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(100) NOT NULL
    );
    CREATE TABLE "north_app_book_readers" (
        "id" serial NOT NULL PRIMARY KEY,
        "book_id" integer NOT NULL,
        "reader_id" integer NOT NULL,
        UNIQUE ("book_id", "reader_id")
    );
    ALTER TABLE "north_app_book_readers"
        ADD CONSTRAINT "north_app_book_re_book_id_687d69bb6cc91963_fk_north_app_book_id"
        FOREIGN KEY ("book_id") REFERENCES "north_app_book_wip" ("id") DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE "north_app_book_readers"
        ADD CONSTRAINT "north_app_boo_reader_id_1ba7f4169d70a099_fk_north_app_reader_id"
        FOREIGN KEY ("reader_id") REFERENCES "north_app_reader" ("id") DEFERRABLE INITIALLY DEFERRED;
    CREATE INDEX "north_app_book_readers_0a4572cc"
        ON "north_app_book_readers" ("book_id");
    CREATE INDEX "north_app_book_readers_74a171c1"
        ON "north_app_book_readers" ("reader_id");

COMMIT;
