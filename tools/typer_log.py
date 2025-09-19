import json
import os

import typer

from tools.env_root import root


def patch_typer_invoke():
    file = root() / "data/typer-log.json"
    file.parent.mkdir(parents=True, exist_ok=True)

    # Store the original invoke method
    _original_invoke = typer.core.TyperCommand.invoke

    def patched_invoke(self, ctx):
        # This runs after parsing but before command execution
        with file.open("a", encoding="utf-8") as fout:
            fout.write(json.dumps(
                {"cmd": ctx.command.name, "params": ctx.params},
            ) + os.linesep)
        # print(f"Command: {ctx.command.name}")
        # print(f"Params: {ctx.params}")  # Will have all your arguments!

        # Call the original command
        return _original_invoke(self, ctx)

    # Apply the patch
    typer.core.TyperCommand.invoke = patched_invoke
