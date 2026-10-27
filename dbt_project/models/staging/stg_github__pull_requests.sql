with source as (
    select * from {{ source('raw', 'raw_pull_requests') }}
),

renamed as (
    select
        (data->>'id')::bigint           as pr_id,
        (data->>'number')::int          as pr_number,
        data->>'title'                  as pr_title,
        data->>'state'                  as pr_state,
        data->'user'->>'login'          as author_login,
        case
            when data->>'_source_repo' = 'dbt-labs/dbt-core' then 'dbt-labs/dbt'
            else data->>'_source_repo'
        end as source_repo,
        (data->>'created_at')::timestamp as created_at,
        (data->>'merged_at')::timestamp  as merged_at,
        (data->>'closed_at')::timestamp  as closed_at,
        (data->>'merged_at') is not null as is_merged,
        loaded_at
    from source
)

select * from renamed