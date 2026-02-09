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

## https://leetcode.com/problems/consecutive-numbers/

```sql
-- Write your PostgreSQL query statement below
WITH lags as (
    SELECT
        *, 
        LAG(num) OVER (ORDER BY id) as lag_num_1, 
        LAG(num, 2) OVER (ORDER BY id) as lag_num_2
    FROM
        Logs
)

SELECT distinct(lag_num_2) as  ConsecutiveNums from
lags where num = lag_num_1 and num = lag_num_2;
```

| Feature | Option 1 (Self-Joins) | Option 2 (Window Functions) |
| --- | --- | --- |
| **Logic** | Joins the table to itself three times. | Scans the table once using a "sliding window." |
| **Performance** | **Lower.** Becomes very slow as the dataset grows (Exponential complexity). | **Higher.** Much more efficient on large datasets (Linear complexity). |
| **Readability** | Easier for beginners to understand. | Cleaner and more "modern" SQL syntax. |
| **Edge Cases** | Fails if IDs have gaps (e.g., 1, 2, 4). | Handles ID gaps better (depending on the `ORDER BY`). |
| **Scalability** | Hard to scale (e.g., finding 10 consecutive numbers would require 10 joins). | Easy to scale (just adjust the `LAG` offset). |

# https://leetcode.com/problems/employees-earning-more-than-their-managers/

```sql
-- Write your PostgreSQL query statement below
select e.name as Employee
from Employee e
inner join
Employee m
on e.managerId = m.id
where e.salary > m.salary
```

# https://leetcode.com/problems/duplicate-emails/

```sql
-- Write your PostgreSQL query statement below
SELECT 
    email
FROM 
    Person
GROUP BY
    email
HAVING
    count(*) > 1
```

