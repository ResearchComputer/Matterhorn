import typer
from typing import Optional
from matterhorn.core.ui import RichUI
from matterhorn.cli.utils import create_application

app = typer.Typer()


@app.command()
def run(config: str = typer.Option(..., help="Path to the config file")):
    
    with RichUI() as ui:
        application = create_application()
