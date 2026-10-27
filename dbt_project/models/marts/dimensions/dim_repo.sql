with source as (
    select * from {{ ref('stg_github__repos') }}
),

known as (
    select
        {{ stable_key("repo_id::text") }} as repo_key,
        repo_id,
        repo_full_name,
        repo_name,
        owner_login,
        primary_language,
        stargazers_count,
        forks_count,
        open_issues_count,
        default_branch
    from source
),

unknown_member as (
    select
        -1::bigint          as repo_key,
        -1::bigint          as repo_id,
        '(unknown)'::text   as repo_full_name,
        '(unknown)'::text   as repo_name,
        null::text          as owner_login,
        null::text          as primary_language,
        null::int           as stargazers_count,
        null::int           as forks_count,
        null::int           as open_issues_count,
        null::text          as default_branch
)

select * from known
union all
select * from unknown_member
