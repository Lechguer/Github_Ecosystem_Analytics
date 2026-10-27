-- Real PR rejection rate: closed without merge / closed (open PRs excluded).
select
    count(*) filter (where pr_state = 'closed' and not is_merged) as closed_unmerged,
    count(*) filter (where pr_state = 'closed') as closed_total,
    round(100.0 * count(*) filter (where pr_state = 'closed' and not is_merged)
          / count(*) filter (where pr_state = 'closed'), 1) as rejection_rate_pct
from {{ ref('fct_pull_requests') }}
