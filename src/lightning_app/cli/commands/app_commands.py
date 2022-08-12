import os
import sys
from typing import Dict, Optional

import requests

from lightning_app.cli.commands.connection import _resolve_command_path
from lightning_app.utilities.cli_helpers import _retrieve_application_url_and_available_commands
from lightning_app.utilities.commands.base import _download_command
from lightning_app.utilities.enum import OpenAPITags


def _run_app_command(app_name: str, app_id: Optional[str]):
    """Execute a function in a running application from its name."""
    # 1: Collect the url and comments from the running application
    url, api_commands = _retrieve_application_url_and_available_commands(app_id)
    if url is None or api_commands is None:
        raise Exception("We couldn't find any matching running app.")

    if not api_commands:
        raise Exception("This application doesn't expose any commands yet.")

    command = sys.argv[1]

    if command not in api_commands:
        raise Exception(f"The provided command {command} isn't available in {list(api_commands)}")

    # 2: Send the command from the user
    metadata = api_commands[command]

    # 3: Execute the command
    if metadata["tag"] == OpenAPITags.APP_COMMAND:
        _handle_command_without_client(command, metadata, url)
    else:
        assert app_id
        _handle_command_with_client(command, metadata, app_id, url)


def _handle_command_without_client(command: str, metadata: Dict, url: str) -> None:
    # TODO: Improve what is current supported
    supported_params = list(metadata["parameters"])
    if "--help" == sys.argv[-1]:
        print(f"Usage: lightning {command} [ARGS]...")
        print(" ")
        print("Options")
        for param in supported_params:
            print(f"  {param}: Add description")
        return

    provided_params = [param.replace("--", "") for param in sys.argv[2:]]

    if any("=" not in param for param in provided_params):
        raise Exception("Please, use --x=y syntax when providing the command arguments.")

    for param in provided_params:
        if param.split("=")[0] not in supported_params:
            raise Exception(f"Some arguments need to be provided. The keys are {supported_params}.")

    # TODO: Encode the parameters and validate their type.
    query_parameters = "&".join(provided_params)
    resp = requests.post(url + f"/command/{command}?{query_parameters}")
    assert resp.status_code == 200, resp.json()
    print("Your command execution was successful.")


def _handle_command_with_client(command: str, metadata: Dict, app_id: str, url: str):
    debug_mode = bool(int(os.getenv("DEBUG", "0")))

    target_file = _resolve_command_path(command) if debug_mode else _resolve_command_path(command)

    if debug_mode:
        print(target_file)

    client_command = _download_command(
        command,
        metadata["cls_path"],
        metadata["cls_name"],
        app_id,
        debug_mode=debug_mode,
        target_file=target_file if debug_mode else _resolve_command_path(command),
    )
    client_command._setup(command_name=command, app_url=url)
    sys.argv = sys.argv[1:]
    client_command.run()
