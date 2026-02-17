### https://leetcode.com/problems/exchange-seats/description/

```sql
# Write your MySQL query statement below
with group_id_df as (
    select
        *,
        ceil(id/2) as group_id
    from 
        Seat
), lag_lead as (
    select
        *, 
        lag(student) over (partition by group_id) as lag_student,
        lead(student) over (partition by group_id) as lead_student
    from 
        group_id_df
)

select id, coalesce(lead_student, lag_student, student) as student
from lag_lead order by id;
```

### https://leetcode.com/problems/swap-sex-of-employees/

```sql
# Write your MySQL query statement below
UPDATE Salary
SET sex = CASE
    WHEN sex = 'm' THEN 'f'
    ELSE 'm'
END
```

### https://leetcode.com/problems/market-analysis-i/

```sql
SELECT 
u.user_id as buyer_id, 
u.join_date, 
count(o.order_id) as 'orders_in_2019'
FROM users u
LEFT JOIN Orders o
ON o.buyer_id=u.user_id AND YEAR(order_date)='2019'
GROUP BY u.user_id
```

```sql
# Write your MySQL query statement below
with count_2019 as (
    select buyer_id, count(*) as orders_in_2019
    from Orders
    where year(order_date)=2019
    group by buyer_id
)

select
    u.user_id as buyer_id,
    u.join_date,
    coalesce(c.orders_in_2019, 0) as orders_in_2019
from
Users u
left join
count_2019 as c
on u.user_id = c.buyer_id
```