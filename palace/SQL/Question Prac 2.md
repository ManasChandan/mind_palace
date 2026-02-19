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

### https://leetcode.com/problems/product-price-at-a-given-date/

```sql
# Write your MySQL query statement below
with distinct_prod as (
    select distinct(product_id) as product_id
    from Products
), change_analysis as (
    select
        *, 
        ROW_NUMBER() over (partition by product_id order by change_date desc) as rn
    from 
        Products
    where
        change_date <= "2019-08-16"
)

select dp.product_id, coalesce(ca.new_price, 10) as price from 
distinct_prod dp
left join
(select * from change_analysis where rn=1) ca
on dp.product_id = ca.product_id
```

### https://leetcode.com/problems/immediate-food-delivery-ii/

```sql
# Write your MySQL query statement below
with order_rank as (
    select 
        *, 
        ROW_NUMBER() over(partition by customer_id order by order_date asc) as rn
    from
        Delivery
), first_immediate_orders as (
    select * from 
    order_rank
    where rn=1 and order_date = customer_pref_delivery_date
)

select 
    round((select count(distinct(customer_id)) from first_immediate_orders)*100 / 
    (select count(distinct(customer_id)) from Delivery),2)
as immediate_percentage;
```

### https://leetcode.com/problems/monthly-transactions-i/

```sql
with monthly_data as (
    select
        *, 
        DATE_FORMAT(trans_date,'%Y-%m') as `month`
    from 
        Transactions
)

select 
    `month`, 
    country, 
    count(*) as trans_count, 
    sum(case when state = 'approved' then 1 else 0 end) as approved_count, 
    sum(amount) as trans_total_amount, 
    sum(case when state = 'approved' then amount else 0 end) as approved_total_amount
from 
    monthly_data
group by 
    `month`, country;
```

### https://leetcode.com/problems/last-person-to-fit-in-the-bus/

```sql
# Write your MySQL query statement below
with cummulative_sum as (
    select 
        *, 
        sum(weight) over (order by turn asc rows between UNBOUNDED PRECEDING AND CURRENT ROW) as cs
    from
        Queue
), all_allowed_person as (
    select * from cummulative_sum
    where cs <= 1000
)

select person_name from all_allowed_person
where cs = (select max(cs) from all_allowed_person)
```

```sql
with cte1 as (
    select person_name,
        sum(weight)over(order by turn) as cum_weight
    from Queue 

)
select person_name
from cte1
where cum_weight <= 1000
order by cum_weight DESC
limit 1 
```

### https://leetcode.com/problems/restaurant-growth/

```sql
with sv as (
    select visited_on, sum(amount) as amt
    from Customer
    group by visited_on
    order by visited_on asc
), wf as (
    select *, 
        sum(amt) over (order by visited_on asc range between interval 6 day preceding and current row) as ca, 
        avg(amt) over (order by visited_on asc range between interval 6 day preceding and current row) as ma,
        rank() over(order by visited_on asc) as rk
    from 
        sv 
)

select visited_on, ca as amount, round(ma,2) as average_amount
from wf where rk >= 7
```

### https://leetcode.com/problems/students-and-examinations/

```sql
# Write your MySQL query statement below
SELECT 
    st.student_id, 
    st.student_name, 
    sb.subject_name, 
    COUNT(e.student_id) AS attended_exams
FROM 
    Students st
CROSS JOIN 
    Subjects sb
LEFT JOIN 
    Examinations e 
    ON st.student_id = e.student_id 
    AND sb.subject_name = e.subject_name
GROUP BY 
    st.student_id, 
    st.student_name, 
    sb.subject_name
ORDER BY 
    st.student_id, 
    sb.subject_name;
```

### https://leetcode.com/problems/movie-rating/

```sql
# Write your MySQL query statement below
with grouped_table as (
    select u.name as name, m.title as title, mr.rating as rating, mr.created_at as created_at from 
    MovieRating mr
    left join
    Users u
    on mr.user_id = u.user_id
    left join
    Movies m
    on
    mr.movie_id = m.movie_id
)

(select name as results from grouped_table group by name order by count(*) desc, name asc limit 1)
union all
(select title as results from grouped_table where date_format(created_at, '%Y%m') = 202002 group by title order by avg(rating) desc, title asc limit 1)
```