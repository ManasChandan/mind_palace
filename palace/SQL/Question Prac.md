## https://leetcode.com/problems/combine-two-tables/

```sql
select b.firstName, b.lastName, a.city, a.state
from Person as b
left join Address as a on b.personId = a.personId
```

**Dot operator performs faster**

## https://leetcode.com/problems/second-highest-salary/

```sql
SELECT MAX(salary) AS "SecondHighestSalary" 
FROM Employee 
WHERE salary < (SELECT max(salary) FROM Employee); 
```

My approach was a union all operation. 

```sql
select null as secondhighest where note exist(
    select * from src
    where dense_row_num = 2 
)
limit 1
```

**Aggregates return null if all the rows are filtered out**

## https://leetcode.com/problems/nth-highest-salary/description/

```sql
CREATE OR REPLACE FUNCTION NthHighestSalary(N INT) RETURNS TABLE (Salary INT) AS $$
BEGIN
  RETURN QUERY (
    -- Write your PostgreSQL query statement below.
    SELECT (
        SELECT DISTINCT e.salary
      FROM Employee e
      ORDER BY e.salary DESC
      -- If N < 1, we use an impossible OFFSET or force NULL
      LIMIT 1 OFFSET (CASE WHEN N > 0 THEN N - 1 ELSE (SELECT COUNT(*)+2 from Employee) END)
    )

  );
END;
$$ LANGUAGE plpgsql;
```

```sql
CREATE OR REPLACE FUNCTION NthHighestSalary(N INT) RETURNS TABLE (Salary INT) AS $$
BEGIN
  RETURN QUERY (
    -- Write your PostgreSQL query statement below.
    select distinct e.salary
    from (
        select distinct e2.salary, 
            dense_rank() over (order by e2.salary desc) as rnk
        from employee e2 
    ) e
    where e.rnk = N

  );
END;
$$ LANGUAGE plpgsql;
```

The SQL OFFSET clause is used to skip a specified number of rows in a query result set before starting to return the actual results.

SELECT... LIMIT/OFFSET,Empty Set (0 rows)

SELECT... WHERE,Empty Set (0 rows)

SELECT MAX()...,NULL (1 row)

SELECT (SELECT...),NULL (1 row)

## https://leetcode.com/problems/rank-scores/

```sql
-- Write your PostgreSQL query statement below
SELECT score, DENSE_RANK() OVER (ORDER BY SCORE DESC) AS rank
FROM Scores ORDER BY rank;
```
