with distinct_labels as (
    select distinct
        label_id,
        label_name,
        label_color
    from {{ ref('int_issue_labels') }}
)

select
    row_number() over (order by label_id) as label_key,
    label_id,
    label_name,
    label_color
from distinct_labels