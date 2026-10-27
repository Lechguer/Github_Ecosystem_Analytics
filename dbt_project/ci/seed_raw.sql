-- Minimal synthetic raw data so that `dbt build` can run end to end in CI
-- (the real JSON extracts are git-ignored). Same structure as extraction/load_to_postgres.py.
create schema if not exists raw;

drop table if exists raw.raw_repos, raw.raw_contributors, raw.raw_users,
    raw.raw_commits, raw.raw_pull_requests, raw.raw_issues;

create table raw.raw_repos (id serial primary key, loaded_at timestamp default now(), data jsonb not null);
create table raw.raw_contributors (like raw.raw_repos including all);
create table raw.raw_users (like raw.raw_repos including all);
create table raw.raw_commits (like raw.raw_repos including all);
create table raw.raw_pull_requests (like raw.raw_repos including all);
create table raw.raw_issues (like raw.raw_repos including all);

insert into raw.raw_repos (data) values
  ('{"id":1,"full_name":"duckdb/duckdb","name":"duckdb","owner":{"login":"duckdb"},"language":"C++","stargazers_count":10,"forks_count":2,"open_issues_count":3,"default_branch":"main","created_at":"2018-06-26T00:00:00Z","updated_at":"2026-09-01T00:00:00Z","pushed_at":"2026-09-01T00:00:00Z"}'),
  ('{"id":2,"full_name":"dbt-labs/dbt","name":"dbt","owner":{"login":"dbt-labs"},"language":"Python","stargazers_count":8,"forks_count":1,"open_issues_count":2,"default_branch":"main","created_at":"2016-03-10T00:00:00Z","updated_at":"2026-09-01T00:00:00Z","pushed_at":"2026-09-01T00:00:00Z"}'),
  ('{"id":3,"full_name":"apache/airflow","name":"airflow","owner":{"login":"apache"},"language":"Python","stargazers_count":9,"forks_count":3,"open_issues_count":4,"default_branch":"main","created_at":"2015-04-13T00:00:00Z","updated_at":"2026-09-01T00:00:00Z","pushed_at":"2026-09-01T00:00:00Z"}');

insert into raw.raw_contributors (data) values
  ('{"id":101,"login":"alice","contributions":50,"_source_repo":"duckdb/duckdb"}'),
  ('{"id":101,"login":"alice","contributions":10,"_source_repo":"apache/airflow"}'),
  ('{"id":102,"login":"bob","contributions":30,"_source_repo":"dbt-labs/dbt-core"}'),
  ('{"id":103,"login":"dependabot[bot]","contributions":20,"_source_repo":"apache/airflow"}');

insert into raw.raw_users (data) values
  ('{"id":101,"login":"alice","company":"ACME","location":"Paris","bio":"","followers":5,"public_repos":3,"created_at":"2015-01-01T00:00:00Z","type":"User"}'),
  ('{"id":102,"login":"bob","company":"","location":"","bio":"dev","followers":2,"public_repos":1,"created_at":"2016-01-01T00:00:00Z","type":"User"}'),
  ('{"id":103,"login":"dependabot[bot]","company":"","location":"","bio":"","followers":0,"public_repos":0,"created_at":"2017-01-01T00:00:00Z","type":"Bot"}');

-- carol (no contributor/user row) and the commit with no author exercise the "unknown" member
insert into raw.raw_commits (data) values
  ('{"sha":"c1","author":{"login":"alice"},"commit":{"author":{"name":"Alice","email":"a@x.io","date":"2026-08-10T10:00:00Z"},"message":"fix"},"_source_repo":"duckdb/duckdb"}'),
  ('{"sha":"c2","author":{"login":"bob"},"commit":{"author":{"name":"Bob","email":"b@x.io","date":"2026-08-11T10:00:00Z"},"message":"feat"},"_source_repo":"dbt-labs/dbt-core"}'),
  ('{"sha":"c3","author":null,"commit":{"author":{"name":"Ghost","email":"g@x.io","date":"2026-08-12T10:00:00Z"},"message":"chore"},"_source_repo":"apache/airflow"}');

insert into raw.raw_pull_requests (data) values
  ('{"id":1001,"number":1,"title":"pr1","state":"closed","user":{"login":"alice"},"_source_repo":"duckdb/duckdb","created_at":"2026-08-10T10:00:00Z","merged_at":"2026-08-10T20:00:00Z","closed_at":"2026-08-10T20:00:00Z"}'),
  ('{"id":1002,"number":2,"title":"pr2","state":"closed","user":{"login":"carol"},"_source_repo":"apache/airflow","created_at":"2026-08-11T10:00:00Z","merged_at":null,"closed_at":"2026-08-12T10:00:00Z"}'),
  ('{"id":1003,"number":3,"title":"pr3","state":"open","user":{"login":"dependabot[bot]"},"_source_repo":"dbt-labs/dbt-core","created_at":"2026-08-13T10:00:00Z","merged_at":null,"closed_at":null}');

insert into raw.raw_issues (data) values
  ('{"id":2001,"number":10,"title":"bug","state":"closed","user":{"login":"bob"},"_source_repo":"dbt-labs/dbt-core","created_at":"2026-08-10T10:00:00Z","closed_at":"2026-08-11T10:00:00Z","labels":[{"id":1,"name":"bug","color":"d73a4a"},{"id":2,"name":"area:cli","color":"ededed"}]}'),
  ('{"id":2002,"number":11,"title":"question","state":"open","user":{"login":"carol"},"_source_repo":"duckdb/duckdb","created_at":"2026-08-12T10:00:00Z","closed_at":null,"labels":[]}');
