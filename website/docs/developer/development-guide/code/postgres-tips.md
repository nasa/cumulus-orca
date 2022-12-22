---
id: postgres-tips
title: Postgres Paging
description: Tips on writing efficient Postgres queries.
---

## Limit
Users may wish to adjust the number of results they receive to adjust memory usage, processing time, etc.
However, this `limit` value should have an upper bound, to avoid users requesting far too much data at once.
In GraphQL in particular, the webserver may have limits on how much data is returned via HTTP requests.

## Paging
It will not always be feasible/desired to return all results at once.
In this case, results should be returned one 'page' at a time, with cursors included to allow customers to easily request the next page.

### Sample Table
Code in the following sections will be based off of the following table:
```
CREATE TABLE "orca"."test_table"  ( 
    "key0"    int4 NULL,
    "key1"    int4 NULL,
    "key2"    int4 NULL 
    )
GO
ALTER TABLE "orca"."test_table"
    ADD CONSTRAINT "test_uniqueness"
    UNIQUE ("key0", "key1", "key2")
```

Adjust code as needed to match your table.

If you wish to do performance testing with the sample table, run the following code:
```
do $$
begin
    for i in 1..100 loop
        for j in 1..100 loop
            for k in 1..100 loop
                INSERT INTO orca.test_table(key0, key1, key2) VALUES(i, j, 'k);
            end loop;
        end loop;
    end loop;
end; $$
```

### Page Retrieval
The initial impulse for retrieving a page may be to `SKIP` the number of entries from previous pages, utilizing `LIMIT` and `OFFSET` like the following:
```
SELECT
    *
FROM
    orca.test_table
ORDER BY 
    key0,
    Key1,
    key2
LIMIT 100
OFFSET 20000
```

However, this requires the query to process all of the entries that are not returned due to the `OFFSET`, and is therefore non-performant on large datasets.

A better option is to apply a `WHERE` clause that picks up after the previous query.
When applied via indexed columns, this eliminates the need for the database to process elements that are outside of the requested page, drastically improving the performance of the query on large datasets.
In the examples below, assume that the row we will be paging from is `key0: 50, key1: 98, key2: 60`

#### Next Page (Default)
Retrieving the next page of `limit` 100 would look like:
```
SELECT
    * 
FROM
    orca.test_table
WHERE
    key0 >= 50
    AND
        (key0 > 50
        OR
            (key1 >= 98
            AND
                (key1 > 98
                OR
                    (key2 > 60)
                )
            )
        )
ORDER BY 
    key0 ASC, 
	key1 ASC, 
	key2 ASC
LIMIT 100
```
Which will return data in the format:
```
key0     key1     key2    
-------  -------  ------- 
50       98       61      
50       98       62
50       98       63
  ... TRUNCATED ...
50       99       58      
50       99       59 
50       99       60 
```

Note that the order of the keys in the `WHERE` and `ORDER BY` clauses must be identical in this example.
The filter should eliminate all of the previously retrieved rows.

#### Previous Page
In the event the user requests the previous page, modify the default query by flipping the signs and `ORDER`, then reversing the `ORDER` of results.
```
SELECT * FROM (
    SELECT
		* 
	FROM
		orca.test_table
	WHERE
		key0 <= 50
		AND
			(key0 < 50
			OR
				(key1 <= 98
				AND
					(key1 < 98
					OR
						(key2 < 60)
					)
				)
			)
	ORDER BY 
		key0 DESC, 
		key1 DESC, 
		key2 DESC
	LIMIT 100
) results
ORDER BY key0 ASC, key1 ASC, key2 ASC
```

### Cursors
`decode_cursor` and `encode_cursor` in the graphql project can be used to encode and decode arbitrary dictionaries for use in future queries.
In our example table, this would consist of `key0`, `key1`, and `key2` to be able to enforce paging uniqueness.
These cursors point to individual elements.
At minimum, users should be given a `start_cursor` and an `end_cursor` for any page they retrieve.
The customer can then make a request with `cursor: {their end_cursor}, direction: 'Next', limit: 100` to get the page past the end_cursor,
or `cursor: {their start_cursor}, direction: 'Previous', limit: 100` to get the page before the start_cursor.

#### No Cursor
If no cursor is specified, behavior depends on `direction`.
- If `direction` is `Next`, get the first page of results using standard ordering.
- If `direction` is `Previous`, get the last page of results using inverted ordering.
This allows users to retrieve either the first or last page of results, effectively allowing them to begin at the start or end of the record-set and page from there.
This is particularly helpful in cases where the query is ordered by date, and users may want to look at events in chronological order, or may only want to look at the most recent events.
