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