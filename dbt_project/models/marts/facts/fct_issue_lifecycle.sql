{{
    config(
        materialized='incremental',
        unique_key='issue_id',
        incremental_strategy='delete+insert'
    )
}}

with issues as (
    select src.* from {{ ref('stg_github__issues') }} as src
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

labels_agg as (
    select
        bridge.issue_id,
        array_agg(dim_label.label_name) as labels
    from {{ ref('bridge_issue_label') }} as bridge
    inner join {{ ref('dim_label') }} as dim_label
        on bridge.label_key = dim_label.label_key
    group by bridge.issue_id
)

select
    issues.issue_id,
    issues.issue_number,
    issues.issue_title,
    issues.issue_state,
    coalesce(repos.repo_key, -1)               as repo_key,
    coalesce(contributors.contributor_key, -1) as contributor_key,
    issues.created_at,
    issues.closed_at,
    issues.is_closed,
    extract(epoch from (issues.closed_at - issues.created_at)) / 3600
        as resolution_time_hours,
    coalesce(labels_agg.labels, array[]::text[]) as labels,
    issues.loaded_at
from issues
left join repos
    on issues.source_repo = repos.repo_full_name
left join contributors
    on issues.author_login = contributors.login
left join labels_agg
    on issues.issue_id = labels_agg.issue_id