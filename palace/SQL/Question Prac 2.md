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
