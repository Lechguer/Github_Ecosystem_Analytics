-- Analysis 1: average time to merge a PR, per repo (merged PRs only).
select
    repo.repo_full_name,
    count(*) as merged_prs,
    round(avg(pr.time_to_merge_hours)::numeric, 1) as avg_hours_to_merge
from {{ ref('fct_pull_requests') }} as pr
inner join {{ ref('dim_repo') }} as repo on pr.repo_key = repo.repo_key
where pr.is_merged
group by repo.repo_full_name
order by avg_hours_to_merge
