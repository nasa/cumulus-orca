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

```
SELECT * FROM orca.performance_check_multiple
//WHERE key0 > 'key0 50' OR (key0 = 'key0 50' AND key1 > 'key1 98' OR (key0 = 'key0 50' AND key1 = 'key1 98' AND key2 > 'key2 60'))
ORDER BY key0 ASC, key1 ASC, key2 ASC
LIMIT 100
```

### Cursors
`decode_cursor` and `encode_cursor` in the graphql project.