with source as (
    select * from {{ source('raw', 'raw_issues') }}
),

renamed as (
    select
        (data->>'id')::bigint            as issue_id,
        (data->>'number')::int           as issue_number,
        data->>'title'                   as issue_title,
        data->>'state'                   as issue_state,
        data->'user'->>'login'           as author_login,
        case
            when data->>'_source_repo' = 'dbt-labs/dbt-core' then 'dbt-labs/dbt'
            else data->>'_source_repo'
        end as source_repo,
        (data->>'created_at')::timestamp as created_at,
        (data->>'closed_at')::timestamp  as closed_at,
        (data->>'closed_at') is not null as is_closed,
        loaded_at
    from source
)

select * from renamed