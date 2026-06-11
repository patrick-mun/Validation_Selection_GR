import click

@click.group()
def cli():
    """Genome Reunion validation pipeline."""
    pass

@cli.command()
def status():
    click.echo("genorun-validation: development scaffold")

if __name__ == "__main__":
    cli()
