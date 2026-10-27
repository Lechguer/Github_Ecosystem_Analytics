with source as (
    select * from {{ source('raw', 'raw_users') }}
),

renamed as (
    select
        (data->>'id')::bigint  as contributor_id,
        data->>'login'         as login,
        nullif(data->>'company', '')  as company,
        nullif(data->>'location', '') as location,
        nullif(data->>'bio', '')      as bio,
        (data->>'followers')::int     as followers_count,
        (data->>'public_repos')::int  as public_repos_count,
        (data->>'created_at')::timestamp as account_created_at,
        loaded_at
    from source
)

select * from renamed