with source as (
    select * from {{ source('raw', 'raw_contributors') }}
),

renamed as (
    select
        (data->>'id')::bigint          as contributor_id,
        data->>'login'                 as login,
        (data->>'contributions')::int  as contributions,
        data->>'_source_repo'          as source_repo,
        loaded_at
    from source
)

select * from renamed