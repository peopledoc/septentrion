 -- comment
--
 --
SELECT * from foo;

--

--meta-psql:do-until-0

WITH author_data AS (
    SELECT
        store_book.id as book_id,
        store_book.author_id as author_id,
        store_book.author_first_name as first_name,
        store_book.author_last_name as last_name
    FROM store_book
        LEFT JOIN store_author
            ON store_author.id = store_book.author_id
        LEFT JOIN book_authorinfo
            ON book_authorinfo.book_id = store_book.id

    WHERE store_author.id IS NOT NULL
        AND book_authorinfo.book_id IS NULL
    LIMIT 5000
)
INSERT INTO book_authorinfo (
    book_id,
    author_id,
    first_name,
    last_name
)
SELECT author_data.*
FROM author_data;


--meta-psql:done
SELECT * from foo;
 --
