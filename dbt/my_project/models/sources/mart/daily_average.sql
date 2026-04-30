{{ config(
    materialized='table'
)}}

SELECT 
    city,
    date(weather_time_local) AS date,
    round(avg(temperature)::numeric, 2) as avg_temperature,
    round(avg(wind_speed)::numeric, 2) as avg_wind_speed
FROM {{ ref('stg_weather_data') }}
GROUP BY 
    city,
    date(weather_time_local)
ORDER BY
    city,
    date(weather_time_local)