import typer
from typing import Optional, Any
import signal
import sys
from rcc.core.ui import RichUI
from rcc.cli.utils import create_application, construct_launch_options, ProductionServiceRegistry, parse_config

app = typer.Typer()


@app.command()
def launch(config: str = typer.Option(..., help="Path to the config file")):
    config = parse_config(config)
    options = construct_launch_options(config, True)
    service_registry = ProductionServiceRegistry()
    fs = service_registry.local_filesystem()
    with RichUI() as ui:
        application = create_application(options, service_registry, ui)
        def on_cancel(*args: Any, **kwargs: Any) -> None:
            sys.exit(app.cancel())

        signal.signal(signal.SIGINT, on_cancel)
        return application.run(options)

@app.command()
def server():
    typer.echo("Server not implemented yet")