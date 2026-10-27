-- Analysis 2: contribution concentration (Pareto), bots excluded.
-- How many human contributors account for 80% of the contributions of the extracted top contributors?
with ranked as (
    select
        login,
        total_contributions,
        sum(total_contributions) over (order by total_contributions desc, login asc) as cumulative,
        sum(total_contributions) over () as grand_total
    from {{ ref('dim_contributor') }}
    where is_current
      and not is_bot
      and contributor_key <> -1
)

select
    count(*) filter (where cumulative - total_contributions < 0.8 * grand_total) as contributors_for_80pct,
    count(*) as total_contributors,
    round(100.0 * count(*) filter (where cumulative - total_contributions < 0.8 * grand_total) / count(*), 1)
        as pct_of_contributors
from ranked
