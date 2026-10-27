select *
from {{ ref('fct_pull_requests') }}
where time_to_merge_hours < 0