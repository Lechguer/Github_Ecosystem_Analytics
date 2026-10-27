select *
from {{ ref('fct_issue_lifecycle') }}
where resolution_time_hours < 0