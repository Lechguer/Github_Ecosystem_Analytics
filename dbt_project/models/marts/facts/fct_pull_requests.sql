{{
    config(
        materialized='incremental',
        unique_key='pr_id',
        incremental_strategy='delete+insert'
    )
}}

with pull_requests as (
    select src.* from {{ ref('stg_github__pull_requests') }} as src
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
)

select
    pull_requests.pr_id,
    pull_requests.pr_number,
    pull_requests.pr_title,
    pull_requests.pr_state,
    coalesce(repos.repo_key, -1)               as repo_key,
    coalesce(contributors.contributor_key, -1) as contributor_key,
    pull_requests.created_at,
    pull_requests.merged_at,
    pull_requests.closed_at,
    pull_requests.is_merged,
    extract(epoch from (pull_requests.merged_at - pull_requests.created_at)) / 3600
        as time_to_merge_hours,
    pull_requests.loaded_at
from pull_requests
left join repos
    on pull_requests.source_repo = repos.repo_full_name
left join contributors
    on pull_requests.author_login = contributors.login
