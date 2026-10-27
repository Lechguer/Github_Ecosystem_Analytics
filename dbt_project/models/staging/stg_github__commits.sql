with source as (
    select * from {{ source('raw', 'raw_commits') }}
),

renamed as (
    select
        data->>'sha'                          as commit_sha,
        data->'commit'->'author'->>'name'     as git_author_name,
        data->'commit'->'author'->>'email'    as git_author_email,
        (data->'commit'->'author'->>'date')::timestamp as authored_at,
        data->'author'->>'login'              as github_login,
        case
            when data->>'_source_repo' = 'dbt-labs/dbt-core' then 'dbt-labs/dbt'
            else data->>'_source_repo'
        end as source_repo,
        data->'commit'->>'message'            as commit_message,
        loaded_at
    from source
)

select * from renamed