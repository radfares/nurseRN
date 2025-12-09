import click
import os
from memory_bank import MemoryBank

def _get_db_connection():
    # SECURITY FIX: Use environment variables for database credentials
    return MemoryBank(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),  # NEVER hardcode passwords
        database=os.getenv('DB_NAME', 'ai_memory')
    )

def _log_cli_action(db_conn, command_name, status='success', error=None):
    """Log a CLI action to the memory bank."""
    content = f"CLI command '{command_name}' executed with status: {status}"
    if error:
        content += f" | Error: {error}"
    db_conn.store_memory(agent_id=1, content=content)

@click.group()
@click.version_option("0.1.0", help="Show the version and exit.")
@click.pass_context
def cli(ctx):
    """
    An AI Orchestration Framework CLI to manage models, run tasks, and view logs.
    """
    ctx.obj = {'db_connection': _get_db_connection()}

@cli.group(help="Manage local Ollama models.")
def model():
    """A group for model-related commands."""
    pass

@model.command('list', help="List available local Ollama models.")
@click.pass_context
def list_models(ctx):
    """Stub for listing models."""
    db_conn = ctx.obj['db_connection']
    click.echo("Confirmation: Listing available models...")
    _log_cli_action(db_conn, "model-list")

@model.command('use', help="Select a model to be used for subsequent tasks.")
@click.argument('model_name')
@click.pass_context
def use_model(ctx, model_name):
    """Stub for selecting an active model."""
    db_conn = ctx.obj['db_connection']
    click.echo(f"Confirmation: Setting active model to '{model_name}'...")
    _log_cli_action(db_conn, "model-use")

@cli.command('run', help="Run a task with a specified prompt.")
@click.option('--prompt', required=True, help='The prompt to execute.')
@click.option('--async', 'run_async', is_flag=True, default=False, help="Run the task asynchronously.")
@click.pass_context
def run(ctx, prompt, run_async):
    """Stub for running a prompt."""
    db_conn = ctx.obj['db_connection']
    click.echo(f"Received prompt: '{prompt}'")
    if run_async:
        click.echo("Confirmation: Enqueuing task for asynchronous execution...")
    else:
        click.echo("Confirmation: Executing task synchronously...")
    
    _log_cli_action(db_conn, "run")

@cli.group(help="View system logs.")
def log():
    """A group for log-related commands."""
    pass

@log.command('view', help="View the latest entries from the structured memory log.")
@click.pass_context
def view_logs(ctx):
    """Stub for viewing logs."""
    db_conn = ctx.obj['db_connection']
    click.echo("Confirmation: Tailing the last 20 lines of structured_memory_log.md...")
    _log_cli_action(db_conn, "log-view")

@log.command('memory', help="View recent memory entries.")
@click.option('--agent', default=1, help="Agent ID to view memory for.")
@click.pass_context
def view_memory(ctx, agent):
    """Display recent memory entries for a given agent."""
    db_conn = ctx.obj['db_connection']
    entries = db_conn.fetch_recent_memories(agent_id=agent, limit=10)
    for entry in entries:
        timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"[{timestamp}] {entry['content']}")

# 👇 This must be the last line
if __name__ == '__main__':
    cli()
