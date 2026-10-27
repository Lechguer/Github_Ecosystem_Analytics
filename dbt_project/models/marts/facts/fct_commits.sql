{{
    config(
        materialized='incremental',
        unique_key='commit_sha',
        incremental_strategy='delete+insert'
    )
}}

with commits as (
    select src.* from {{ ref('stg_github__commits') }} as src
    {% if is_incremental() %}
    where src.loaded_at > (select max(existing.loaded_at) from {{ this }} as existing)
    {% endif %}
),

repos as (
    select * from {{ ref('dim_repo') }}
),

contributors as (
    select * from {{ ref('dim_contributor') }}
    where is_current = true
),

dates as (
    select * from {{ ref('dim_date') }}
)

select
    commits.commit_sha,
    coalesce(repos.repo_key, -1)               as repo_key,
    coalesce(contributors.contributor_key, -1) as contributor_key,
    dates.date_key,
    commits.authored_at,
    commits.commit_message,
    commits.loaded_at
from commits
left join repos
    on commits.source_repo = repos.repo_full_name
left join contributors
    on commits.github_login = contributors.login
left join dates
    on commits.authored_at::date = dates.full_date
