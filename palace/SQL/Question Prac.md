### https://leetcode.com/problems/combine-two-tables/

```sql
select b.firstName, b.lastName, a.city, a.state
from Person as b
left join Address as a on b.personId = a.personId
```

**Dot operator performs faster**

### https://leetcode.com/problems/second-highest-salary/

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

### https://leetcode.com/problems/nth-highest-salary/description/

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

### https://leetcode.com/problems/rank-scores/

```sql
-- Write your PostgreSQL query statement below
SELECT score, DENSE_RANK() OVER (ORDER BY SCORE DESC) AS rank
FROM Scores ORDER BY rank;
```

### https://leetcode.com/problems/consecutive-numbers/

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

### https://leetcode.com/problems/employees-earning-more-than-their-managers/

```sql
-- Write your PostgreSQL query statement below
select e.name as Employee
from Employee e
inner join
Employee m
on e.managerId = m.id
where e.salary > m.salary
```

### https://leetcode.com/problems/duplicate-emails/

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

### https://leetcode.com/problems/department-highest-salary/description/

```sql
-- Write your PostgreSQL query statement below
with salary_ranked as (
    select d.name as Department, e.name as Employee, e.salary as Salary, 
        DENSE_RANK() over (PARTITION BY departmentId order by e.salary desc) as rk
    from
    Employee e
    left join
    Department d
    on e.departmentId = d.id
)
select Department, Employee, Salary from 
salary_ranked where rk = 1;
```

### https://leetcode.com/problems/department-top-three-salaries/

```sql
-- Write your PostgreSQL query statement below
with salary_ranked as (
    select d.name as Department, e.name as Employee, e.salary as Salary, 
        DENSE_RANK() over (PARTITION BY departmentId order by e.salary desc) as rk
    from
    Employee e
    left join
    Department d
    on e.departmentId = d.id
)
select Department, Employee, Salary from 
salary_ranked where rk <= 1;
```

### https://leetcode.com/problems/delete-duplicate-emails/submissions/1914826219/

```sql
-- Write your PostgreSQL query statement below
with dup_idf as (
    select min(id) as keep_id from Person p
    group by p.email
)
delete from Person where id not in (select keep_id from dup_idf)
```

### https://leetcode.com/problems/rising-temperature/submissions/1914836465/

```sql
-- Write your PostgreSQL query statement below
with lead_temp as (
    select *, 
        LAG(temperature) OVER (ORDER BY recordDate) as prev_temp, 
        LAG(recordDate) OVER (ORDER BY recordDate) as prev_date
    from
        Weather
)
select id from lead_temp
where temperature > prev_temp and 
recordDate::date - prev_date::date = 1;
```

### https://leetcode.com/problems/trips-and-users/ [HARD]

```sql
with temp as
(select *,
case
when status = 'cancelled_by_client' or status = 'cancelled_by_driver' then 1
else 0 end as score
from trips
where client_id not in (select users_id from users where banned = 'Yes')
and driver_id not in (select users_id from users where banned = 'Yes'))

select request_at as Day, round(sum(score*1.0)/count(score),2) as "Cancellation Rate"
from temp
group by request_at
having request_at between '2013-10-01' and '2013-10-03'

----------------------------------------------------------------------------------------------

-- Write your PostgreSQL query statement below
with unbanned_users as (
    select users_id from Users 
    where banned = 'No'
),
unbanned_trips as (
    select t.* from
    Trips t
    inner join
    unbanned_users uu
    on t.client_id = uu.users_id
    inner join
    unbanned_users uu_new
    on t.driver_id = uu_new.users_id
),
num_cancelled as (
    select request_at, count(*) as cancelled_num
    from unbanned_trips t
    where t.status != 'completed'
    group by request_at
),
num_all as (
    select request_at, count(*) as all_num
    from unbanned_trips t
    group by request_at
)

select 
    all_rec.request_at as Day, 
    ROUND(COALESCE(can.cancelled_num, 0) * 1.0 / all_rec.all_num,2) as "Cancellation Rate"
from 
    num_all as all_rec 
left join 
    num_cancelled as can 
on can.request_at = all_rec.request_at
where all_rec.request_at >= '2013-10-01' and all_rec.request_at <= '2013-10-03'
order by all_rec.request_at
```

### https://leetcode.com/problems/game-play-analysis-iv/?envType=problem-list-v2&envId=database

```sql
-- Write your PostgreSQL query statement below
with next_day as (
    select player_id, min(event_date) + interval '1day' as next_day_after_login
    from Activity group by player_id
), next_day_players as (
    select a.player_id as player_id from Activity a
    join next_day n
    on a.player_id = n.player_id and a.event_date = n.next_day_after_login
)

select round((select count(distinct(player_id)) * 1.0 from next_day_players )/(select count(distinct(player_id)) from Activity),2) as fraction;
```
### https://leetcode.com/problems/managers-with-at-least-5-direct-reports/description/?envType=problem-list-v2&envId=database

```sql
-- Write your PostgreSQL query statement below
select e2.name as name from 
Employee e1
join
Employee e2
on e1.managerId = e2.id
group by e1.managerId, e2.name
having count(distinct(e1.id)) >= 5
```

### https://leetcode.com/problems/find-customer-referee/

```sql
select name
from Customer
where referee_id !=2 is not false
```

### https://leetcode.com/problems/investments-in-2016/

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
    SELECT tiv_2016,
           COUNT(*) OVER(PARTITION BY tiv_2015) as tiv_count,
           COUNT(*) OVER(PARTITION BY lat, lon) as loc_count
    FROM Insurance
) t
WHERE tiv_count > 1 AND loc_count = 1;

-- WRONG SOLUTION
-- The below solution eliminates for a pid that can be included 
-- but their couterparty got removed due the fact of lat lon removal. 

with drop_duplicate as (
    select min(tiv_2015) as tiv_2015, min(tiv_2016) as tiv_2016
    from Insurance
    group by lat, lon
    having count(lat) = 1 and count(lon) = 1
), tiv_sums as (
    select sum(tiv_2016) as sum_tiv from
    drop_duplicate group by tiv_2015
    having count(*) > 1
)

select ROUND(SUM(sum_tiv), 2) as tiv_2016 from 
tiv_sums;
```

### https://leetcode.com/problems/human-traffic-of-stadium/

This is a classic SQL problem (often referred to as the "Stadium Problem") that tests your ability to identify patterns in sequences. To solve this, we need to find groups of at least three rows where the `id` values are consecutive and every row in that sequence has a `people` count .

The most efficient way to handle this is by using a **window function** to create a "grouping" key.

If you subtract a sequential row number (`ROW_NUMBER()`) from a consecutive `id`, the result will be a constant value for that specific sequence.

* **Example:** If IDs are 5, 6, 7 and row numbers are 1, 2, 3...
* $5 - 1 = 4$
* $6 - 2 = 4$
* $7 - 3 = 4$

* Because the difference is the same (**4**), we know these records belong together.

```sql
WITH GroupedSequences AS (
    SELECT 
        *,
        -- id - row_number gives a constant value for consecutive sequences
        id - ROW_NUMBER() OVER (ORDER BY id) AS id_group
    FROM Stadium
    WHERE people >= 100
),
SequenceCounts AS (
    SELECT 
        *,
        -- Count how many rows are in each 'id_group'
        COUNT(*) OVER (PARTITION BY id_group) AS group_len
    FROM GroupedSequences
)
-- Only select records from groups that have 3 or more rows
SELECT 
    id, 
    visit_date, 
    people
FROM SequenceCounts
WHERE group_len >= 3
ORDER BY visit_date;

```

1. **`GroupedSequences` CTE**: First, we filter for rows where `people >= 100`. Then, we calculate the difference between the `id` and a generated `ROW_NUMBER`. This creates a unique identifier (`id_group`) for every consecutive stretch of IDs.
2. **`SequenceCounts` CTE**: We use another window function (`COUNT(*) OVER...`) to check how many rows exist within each of those unique groups.
3. **Final Select**: We filter out any groups that have fewer than 3 records and sort the final result by date.