with snapshot as (
    select * from {{ ref('contributors_snapshot') }}
),

contributions_agg as (
    select
        contributor_id,
        login,
        sum(contributions) as total_contributions,
        array_agg(distinct source_repo) as repos_contributed
    from {{ ref('stg_github__contributors') }}
    group by contributor_id, login
),

known as (
    select
        {{ stable_key("snapshot.contributor_id::text || '|' || snapshot.dbt_valid_from::text") }}
            as contributor_key,
        snapshot.contributor_id,
        snapshot.login,
        snapshot.company,
        snapshot.location,
        snapshot.followers_count,
        coalesce(contributions_agg.total_contributions, 0)::bigint as total_contributions,
        contributions_agg.repos_contributed,
        (snapshot.login like '%[bot]') as is_bot,
        snapshot.dbt_valid_from as valid_from,
        snapshot.dbt_valid_to as valid_to,
        (snapshot.dbt_valid_to is null) as is_current
    from snapshot
    left join contributions_agg
        on snapshot.contributor_id = contributions_agg.contributor_id
),

-- Kimball "unknown member": facts whose author is not in the dimension point here
-- instead of carrying a NULL foreign key. GitHub logins cannot contain parentheses,
-- so '(unknown)' can never collide with a real login.
unknown_member as (
    select
        -1::bigint                  as contributor_key,
        -1::bigint                  as contributor_id,
        '(unknown)'::text           as login,
        null::text                  as company,
        null::text                  as location,
        null::int                   as followers_count,
        0::bigint                   as total_contributions,
        null::text[]                as repos_contributed,
        false                       as is_bot,
        '1900-01-01'::timestamp     as valid_from,
        null::timestamp             as valid_to,
        true                        as is_current
)

select * from known
union all
select * from unknown_member
