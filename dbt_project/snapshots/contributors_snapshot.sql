{% snapshot contributors_snapshot %}

{{
    config(
      target_schema='marts',
      unique_key='contributor_id',
      strategy='check',
      check_cols=['company', 'location'],
    )
}}

select
    contributor_id,
    login,
    company,
    location,
    bio,
    followers_count,
    public_repos_count
from {{ ref('stg_github__users') }}

{% endsnapshot %}