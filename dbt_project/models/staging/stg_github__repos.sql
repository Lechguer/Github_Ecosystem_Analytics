with source as (
    select * from {{ source('raw', 'raw_repos') }}
),

renamed as (
    select
        (data->>'id')::bigint              as repo_id,
        data->>'full_name'                  as repo_full_name,
        data->>'name'                       as repo_name,
        data->'owner'->>'login'             as owner_login,
        data->>'language'                   as primary_language,
        (data->>'stargazers_count')::int    as stargazers_count,
        (data->>'forks_count')::int         as forks_count,
        (data->>'open_issues_count')::int   as open_issues_count,
        data->>'default_branch'             as default_branch,
        (data->>'created_at')::timestamp    as repo_created_at,
        (data->>'updated_at')::timestamp    as repo_updated_at,
        (data->>'pushed_at')::timestamp     as repo_pushed_at,
        loaded_at
    from source
)

select * from renamed