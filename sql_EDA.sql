--create database OLA;

use OLA;
--drop table rides;

select *
from rides;

-- SQL Queries


-- 1. How does booking value vary across different vehicle types and distance categories?

select Vehicle_Type, distance_cat, avg(booking_value) as avg_book
from Rides
where ride_status = 'complete'
group by Vehicle_Type, distance_cat
order by avg_book desc;

-- 2. Are certain pickup–drop location pairs associated with higher booking values and ride volumes?

select top 10 Pickup_Location, Drop_Location, avg(booking_value) as avg_book, count(*) as volume
from Rides
where ride_status = 'complete'
group by Pickup_Location, Drop_Location
order by avg_book desc, volume desc;


-- 3. What factors are most strongly associated with ride cancellations?

select cancellation_reason, round(cast(count(*) * 100.0 / (select count(*) from rides) as float), 2) as cancell_per
from Rides
where ride_status = 'incomplete'
group by cancellation_reason
order by cancell_per desc;


-- 4. Is there a relationship between ride distance and cancellation probability?


select distance_cat, round(cast(count(*) * 100.0 / (select count(*) from rides) as float), 2) as cancell_per
from Rides
where ride_status = 'incomplete'
group by distance_cat
order by cancell_per desc;




-- 5. How do vehicle turnaround time (V_TAT) and customer turnaround time (C_TAT) impact ride status?
SELECT
    ride_status,
    AVG(V_TAT) AS avg_vehicle_tat,
    AVG(C_TAT) AS avg_customer_tat,
    COUNT(*)   AS total_rides
FROM rides
GROUP BY ride_status;


-- Does driver rating influence customer rating and ride completion?

with cte as (
SELECT *, 
    CASE
        WHEN Driver_Ratings < 3 THEN 'Low'
        WHEN Driver_Ratings < 4 THEN 'Medium'
        ELSE 'High'
    END AS driver_rating_bucket
from rides)

select driver_rating_bucket, 
    ride_status,
    AVG(Customer_Rating) AS avg_customer_rating,
    COUNT(*) AS ride_count
FROM cte
GROUP BY driver_rating_bucket, ride_status
ORDER BY driver_rating_bucket;

-- Are specific time periods associated with higher booking demand and cancellations?

select Time, count(*) as cnt
from rides
group by time
order by cnt desc;

-- Which vehicle types are the most operationally efficient in terms of revenue, turnaround time, and ride completion?

SELECT
    DATEPART(hour, Time) AS booking_hour,
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN ride_status = 'incomplete' THEN 1 ELSE 0 END) AS cancelled_rides
FROM rides
GROUP BY DATEPART(hour, Time)
ORDER BY total_bookings desc, cancelled_rides;


-- What patterns differentiate high-value repeat customers from low-value or churn-risk customers?
WITH customer_segments AS (
    SELECT
        Customer_ID,
        COUNT(*) AS total_rides,
        SUM(Booking_Value) AS total_booking_value,
        AVG(Customer_Rating) AS avg_customer_rating,
        SUM(CASE WHEN ride_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_rides,
        CASE
            WHEN COUNT(*) >= 5 AND SUM(Booking_Value) >= 1000 THEN 'High-Value Repeat'
            WHEN SUM(CASE WHEN ride_status = 'incomplete' THEN 1 ELSE 0 END) >= 2
                 OR COUNT(*) = 1 THEN 'Churn-Risk'
            ELSE 'Medium-Value'
        END AS customer_segment
    FROM rides
    GROUP BY Customer_ID
)
SELECT
    customer_segment,
    COUNT(Customer_ID) AS customers,
    AVG(total_rides) AS avg_rides,
    AVG(total_booking_value) AS avg_total_value,
    AVG(avg_customer_rating) AS avg_rating,
    AVG(cancelled_rides) AS avg_cancellations
FROM customer_segments
GROUP BY customer_segment;
