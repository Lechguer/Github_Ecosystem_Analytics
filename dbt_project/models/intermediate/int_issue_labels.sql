with source as (
    select * from {{ source('raw', 'raw_issues') }}
),

exploded as (
    select
        (data->>'id')::bigint as issue_id,
        jsonb_array_elements(data->'labels') as label_json
    from source
    where jsonb_array_length(data->'labels') > 0
)

select
    issue_id,
    (label_json->>'id')::bigint as label_id,
    label_json->>'name'         as label_name,
    label_json->>'color'        as label_color
from exploded