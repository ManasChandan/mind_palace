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

### https://leetcode.com/problems/find-product-recommendation-pairs/

**Joining on the user id creates a partioned cross product by itself**

```sql
# Write your MySQL query statement below
with product_count as (
    select p1.product_id as product1_id, p2.product_id as product2_id, count(distinct(p1.user_id)) as customer_count from 
    productpurchases p1
    join
    productpurchases p2
    on p1.user_id = p2.user_id
    where p1.product_id < p2.product_id
    group by p1.product_id, p2.product_id
    having customer_count >= 3
)

select pc.product1_id, pc.product2_id, info1.category as product1_category, info2.category as product2_category, customer_count 
from product_count pc
join
productinfo as info1
on pc.product1_id = info1.product_id
join
productinfo as info2
on pc.product2_id = info2.product_id
order by customer_count desc, product1_id asc, product2_id asc
```

### https://leetcode.com/problems/seasonal-sales-analysis/

```sql
# Write your MySQL query statement below
with required_info as (
    select
        p.category as category, 
        s.quantity as quantity,
        quantity * price as revenue, 
        case
            when month(sale_date) in (12,1,2) then 'Winter'
            when month(sale_date) in (3,4,5) then 'Spring'
            when month(sale_date) in (6,7,8) then 'Summer'
            else 'Fall'
        end as season
    from
    sales s
    join
    products p
    on s.product_id = p.product_id
), 
seasoned_info as (
    select
        season, category, 
        sum(quantity) as total_quantity, 
        sum(revenue) as total_revenue, 
        row_number() over (partition by season order by sum(quantity) desc, sum(revenue) desc, category asc) as rn
    from
        required_info
    group by season, category
)

select season, category, total_quantity, total_revenue from 
seasoned_info where rn=1
```

### https://leetcode.com/problems/average-time-of-process-per-machine/

```sql
# Write your MySQL query statement below
with time_taken as (
    select 
        machine_id, 
        process_id, 
        max(case when activity_type = 'end' then timestamp end) - max(case when activity_type = 'start' then timestamp end) as time_taken_process
    from
        Activity
    group by 
        machine_id, process_id
)

select
    machine_id,
    round(avg(time_taken_process),3) as processing_time 
from 
    time_taken
group by 
    machine_id
```

### https://leetcode.com/problems/find-overbooked-employees/description/

**YEARWEEK DATE FUNCTION**

```sql
with weekly_timings as (
    select
        employee_id, 
        yearweek(meeting_date,1),
        sum(duration_hours) as weekly_meeting_time
    from
        meetings
    group by 
        employee_id, yearweek(meeting_date,1)
    having
        weekly_meeting_time > 20
)

select
    wt.employee_id, e.employee_name, e.department, 
    count(*) as meeting_heavy_weeks
from 
weekly_timings wt
join
employees e
on wt.employee_id = e.employee_id
group by 
wt.employee_id, e.employee_name, e.department
having meeting_heavy_weeks >= 2
order by meeting_heavy_weeks desc,  e.employee_name asc
```

### https://leetcode.com/problems/find-golden-hour-customers/

**when some question say time between 11 to 14, then only hour = 14 is wrong as for 14:22 the hour is still 14, go donw to minute**

```sql
# Write your MySQL query statement below
select
    customer_id, 
    count(*) as total_orders, 
    round(sum(case when DATE_FORMAT(order_timestamp, '%H-%i') between '11-00' and '14-00' or DATE_FORMAT(order_timestamp, '%H-%i') between '18-00' and '21-00' then 1 else 0 end)*100/count(*)) as peak_hour_percentage,
    round(avg(case when order_rating is not null then order_rating else null end),2) as average_rating
from 
restaurant_orders 
group by 
customer_id
having total_orders >= 3
and peak_hour_percentage >= 60
and sum(case when order_rating is not null then 1 else 0 end)*1.0/count(*) >= 0.5
and average_rating >= 4.0
order by average_rating desc, customer_id desc 
```

### https://leetcode.com/problems/find-churn-risk-customers/

```sql
WITH ProcessedEvents AS (
    SELECT 
        user_id,
        plan_name,
        monthly_amount,
        event_date,
        event_type,
        -- Calculate window functions here
        LAST_VALUE(plan_name) OVER (
            PARTITION BY user_id ORDER BY event_date ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS current_plan,
        LAST_VALUE(monthly_amount) OVER (
            PARTITION BY user_id ORDER BY event_date ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS current_monthly_amount,
        LAST_VALUE(event_type) OVER (
            PARTITION BY user_id ORDER BY event_date ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_event_type
    FROM subscription_events
)
SELECT 
    user_id,
    current_plan,
    current_monthly_amount,
    MAX(monthly_amount) AS max_historical_amount,
    DATEDIFF(MAX(event_date), MIN(event_date)) AS days_as_subscriber
FROM ProcessedEvents
GROUP BY user_id, current_plan, current_monthly_amount, last_event_type
HAVING 
    last_event_type <> 'cancel' AND
    SUM(CASE WHEN event_type = 'downgrade' THEN 1 ELSE 0 END) > 0 AND
    DATEDIFF(MAX(event_date), MIN(event_date)) >= 60 AND
    current_monthly_amount / MAX(monthly_amount) < 0.5
ORDER BY days_as_subscriber DESC, user_id ASC;
```