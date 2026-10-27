import subprocess
import sys
import os
from dagster import asset, AssetExecutionContext

EXTRACTION_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "extraction")
DBT_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "dbt_project")


def _run_python_script(script_name):
    result = subprocess.run(
        [sys.executable, script_name],
        cwd=EXTRACTION_DIR,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Erreur dans {script_name}: {result.stderr}")
    return result.stdout


def _run_dbt_command(command_args):
    result = subprocess.run(
        ["dbt"] + command_args,
        cwd=DBT_PROJECT_DIR,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Erreur dbt {command_args}: {result.stdout}\n{result.stderr}")
    return result.stdout


@asset
def extracted_repos(context: AssetExecutionContext):
    """Extrait les metadonnees des 3 repos via l'API GitHub."""
    output = _run_python_script("extract_repos.py")
    context.log.info(output)


@asset
def extracted_commits(context: AssetExecutionContext):
    output = _run_python_script("extract_commits.py")
    context.log.info(output)


@asset
def extracted_pull_requests(context: AssetExecutionContext):
    output = _run_python_script("extract_pull_requests.py")
    context.log.info(output)


@asset
def extracted_issues(context: AssetExecutionContext):
    output = _run_python_script("extract_issues.py")
    context.log.info(output)


@asset
def extracted_contributors(context: AssetExecutionContext):
    output = _run_python_script("extract_contributors.py")
    context.log.info(output)


@asset(deps=[extracted_contributors])
def extracted_users(context: AssetExecutionContext):
    """Depend explicitement de extracted_contributors : on a besoin
    de la liste des contributeurs avant de pouvoir enrichir leurs profils."""
    output = _run_python_script("extract_users.py")
    context.log.info(output)


@asset(deps=[extracted_repos, extracted_commits, extracted_pull_requests,
             extracted_issues, extracted_contributors, extracted_users])
def raw_loaded(context: AssetExecutionContext):
    """Charge tous les JSON extraits dans le schema raw de Postgres."""
    output = _run_python_script("load_to_postgres.py")
    context.log.info(output)


@asset(deps=[raw_loaded])
def dbt_staging(context: AssetExecutionContext):
    """dbt run sur staging + intermediate (le snapshot et les marts en dependent)."""
    output = _run_dbt_command(["run", "--select", "staging", "intermediate"])
    context.log.info(output)


@asset(deps=[dbt_staging])
def dbt_snapshot(context: AssetExecutionContext):
    """SCD Type 2 sur dim_contributor (dim_contributor lit le snapshot, il doit passer avant)."""
    output = _run_dbt_command(["snapshot"])
    context.log.info(output)


@asset(deps=[dbt_snapshot])
def dbt_marts(context: AssetExecutionContext):
    """dbt run sur marts : dimensions (tables) puis faits (incrementaux)."""
    output = _run_dbt_command(["run", "--select", "marts"])
    context.log.info(output)


@asset(deps=[dbt_marts])
def dbt_tests_passed(context: AssetExecutionContext):
    """Valide le grain, les cles etrangeres et la logique metier (33 tests)."""
    output = _run_dbt_command(["test"])
    context.log.info(output)