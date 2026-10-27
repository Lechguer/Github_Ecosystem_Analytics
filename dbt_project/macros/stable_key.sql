{#
  Surrogate key stable across runs: first 60 bits of the md5 of the expression, as a bigint.
  Unlike row_number(), adding rows to a dimension never changes existing keys,
  which is required once fact tables are incremental and store these keys.
#}
{% macro stable_key(expression) -%}
    ('x' || substr(md5({{ expression }}), 1, 15))::bit(60)::bigint
{%- endmacro %}
