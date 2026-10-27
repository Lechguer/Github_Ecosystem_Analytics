from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

EXTRACTION_DIR = "/opt/airflow/project/extraction"
DBT_PROJECT_DIR = "/opt/airflow/project/dbt_project"

default_args = {
    "owner": "zakaria",
    "retries": 1,
}

with DAG(
    dag_id="github_ecosystem_dag",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    extract_repos = BashOperator(
        task_id="extract_repos",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_repos.py",
    )

    extract_commits = BashOperator(
        task_id="extract_commits",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_commits.py",
    )

    extract_pull_requests = BashOperator(
        task_id="extract_pull_requests",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_pull_requests.py",
    )

    extract_issues = BashOperator(
        task_id="extract_issues",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_issues.py",
    )

    extract_contributors = BashOperator(
        task_id="extract_contributors",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_contributors.py",
    )

    extract_users = BashOperator(
        task_id="extract_users",
        bash_command=f"cd {EXTRACTION_DIR} && python extract_users.py",
    )

    load_to_postgres = BashOperator(
        task_id="load_to_postgres",
        bash_command=f"cd {EXTRACTION_DIR} && python load_to_postgres.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt snapshot",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    # Declaration EXPLICITE des dependances, avec l'operateur >>
    [extract_repos, extract_commits, extract_pull_requests, extract_issues, extract_contributors] >> extract_users
    extract_users >> load_to_postgres
    load_to_postgres >> dbt_run >> dbt_snapshot >> dbt_test