### https://leetcode.com/problems/analyze-subscription-conversion/

**key learning: Avg function ignores the null so in case when its going to be null**

```sql
select 
    user_id, 
    round(avg(case when activity_type='free_trial' then activity_duration else null end),2) as trial_avg_duration,
    round(avg(case when activity_type='paid' then activity_duration else null end),2) as paid_avg_duration
from 
    UserActivity
group by 
    user_id
having paid_avg_duration is not null
```