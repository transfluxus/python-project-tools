import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import humanize
import typer

from tools.env_root import root


def patch_typer_invoke(log_fp: Optional[Path] = None):
    if not log_fp:
        log_fp = root() / "data/typer-log.jsonl"
    elif log_fp.suffix != ".jsonl":
        print("typer-log should be a jsonl file")
    log_fp.parent.mkdir(parents=True, exist_ok=True)

    # Store the original invoke method
    _original_invoke = typer.core.TyperCommand.invoke

    def patched_invoke(self, ctx):
        # This runs after parsing but before command execution

        start = datetime.now()
        row = {"cmd": ctx.command.name,
             "params": ctx.params,
             "ts": start.isoformat(timespec="minutes")}

        # print(f"Command: {ctx.command.name}")
        # print(f"Params: {ctx.params}")  # Will have all your arguments!

        # Call the original command
        try:
            res = _original_invoke(self, ctx)
            print(res)
        except Exception as e:
            row["error"] = str(e)
        finally:
            row["duration"] = humanize.naturaldelta(datetime.now() - start)
            with log_fp.open("a", encoding="utf-8") as fout:
                fout.write(json.dumps(row) + os.linesep)
            return res

    # Apply the patch
    typer.core.TyperCommand.invoke = patched_invoke
