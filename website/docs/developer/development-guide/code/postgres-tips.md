---
id: postgres-tips
title: Postgres Paging
description: Tips on writing efficient Postgres queries.
---

## Paging
It will not always be feasible/desired to return all results at once.
In this case, results should be returned one 'page' at a time, with cursors included to allow customers to easily request the next page.

### Sample Table
Code in the following sections will be based off of the following table:
```
CREATE TABLE "orca"."test_table"  ( 
	"key0"	int4 NULL,
	"key1"	int4 NULL,
	"key2"	int4 NULL 
	)
GO
ALTER TABLE "orca"."test_table"
	ADD CONSTRAINT "test_uniqueness"
	UNIQUE ("key0", "key1", "key2")
```

Adjust code as needed to match your table.

### Page Retrieval
The initial impulse for retrieving a page may be to `SKIP` the number of entries from previous pages.
However, this requires the query to process all of the previous entries, and is therefore non-performant on large datasets.

A better option is to apply a `WHERE` clause that picks up after the previous query.
For example, following from a page where the final entry was `key0: 50, key1: 98, key2: 60`, retrieving the next page of size `100` would look like:
```
SELECT * FROM orca.performance_check_multiple
WHERE key0 >= 50 AND (key0 > 50 OR (key1 >= 98 AND (key1 > 98 OR (key2 > 60))))
ORDER BY key0 ASC, key1 ASC, key2 ASC
LIMIT 100
```
Note that the order of the keys in the `WHERE` and `ORDER BY` clauses must be identical in this example.
The filter should eliminate all of the previously retrieved rows.

In the event of a descending order, flip the signs and order:
```
SELECT * FROM orca.performance_check_multiple
WHERE key0 <= 50 AND (key0 < 50 OR (key1 <= 98 AND (key1 < 98 OR (key2 < 60))))
ORDER BY key0 DESC, key1 DESC, key2 DESC
LIMIT 100
```

In the event the user requests the previous page, flip the signs and order, then reverse the order of results.
```
SELECT * FROM (
	SELECT * FROM orca.performance_check_multiple
	WHERE key0 <= 50 AND (key0 < 50 OR (key1 <= 98 AND (key1 < 98 OR (key2 < 60))))
	ORDER BY key0 ASC, key1 ASC, key2 ASC
	LIMIT 100
) results
ORDER BY key0 ASC, key1 ASC, key2 ASC
```

# todo: bidirectional

### Cursors
`decode_cursor` and `encode_cursor` in the graphql project can be used to encode and decode arbitrary dictionaries for use in future queries.
In our example table, this would consist of `key0`, `key1`, and `key2` to be able to enforce paging uniqueness.
These cursors point to individual elements.
At minimum, users should be given a `start_cursor` and an `end_cursor` for any page they retrieve.
The customer can then make a request with `order: 'Ascending', cursor: {their end_cursor}, direction: 'Next'` to get the page past the end_cursor,
or `order: 'Ascending', cursor: {their start_cursor}, direction: 'Previous'` to get the page before the start_cursor.
