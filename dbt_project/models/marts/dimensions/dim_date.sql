with date_spine as (
    select
        generate_series(
            '2015-01-01'::date,
            '2026-12-31'::date,
            '1 day'::interval
        )::date as full_date
)

select
    to_char(full_date, 'YYYYMMDD')::int as date_key,
    full_date,
    extract(year from full_date)::int as year,
    extract(month from full_date)::int as month,
    extract(day from full_date)::int as day,
    extract(week from full_date)::int as week_of_year,
    extract(dow from full_date)::int as day_of_week,
    to_char(full_date, 'Day') as day_name,
    to_char(full_date, 'Month') as month_name
from date_spine