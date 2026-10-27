with issue_labels as (
    select * from {{ ref('int_issue_labels') }}
),

label_dim as (
    select * from {{ ref('dim_label') }}
)

select
    issue_labels.issue_id,
    label_dim.label_key
from issue_labels
inner join label_dim
    on issue_labels.label_id = label_dim.label_id