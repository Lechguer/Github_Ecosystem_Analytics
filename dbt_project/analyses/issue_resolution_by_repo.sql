-- Analysis 3: average issue resolution time, per repo (closed issues only).
select
    repo.repo_full_name,
    count(*) as closed_issues,
    round(avg(issue.resolution_time_hours)::numeric, 1) as avg_hours_to_close
from {{ ref('fct_issue_lifecycle') }} as issue
inner join {{ ref('dim_repo') }} as repo on issue.repo_key = repo.repo_key
where issue.is_closed
group by repo.repo_full_name
order by avg_hours_to_close
