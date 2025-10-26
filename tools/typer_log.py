import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from tools.project_logging import get_logger

try:
    import humanize
    import typer
    from tools.env_root import root

    # Global context for sharing between invoke and log
    _execution_context = {}
    _log_buffer = []


    def safe_serializer(obj):
        return str(obj)

    def patch_typer_invoke(log_fp: Optional[Path] = None):
        global _execution_context
        if not log_fp:
            log_fp = root() / "data/typer-log.jsonl"
        elif log_fp.suffix != ".jsonl":
            print("typer-log should be a jsonl file")
        log_fp.parent.mkdir(parents=True, exist_ok=True)

        # Store the original invoke method
        _original_invoke = typer.core.TyperCommand.invoke

        def patched_invoke(self, ctx):
            global _execution_context
            start = datetime.now()

            # Get more specific command info
            root_ctx = ctx.find_root()
            app_name = _execution_context["app"].info.name

            # Get actual command name and config
            if hasattr(ctx.command, 'callback') and ctx.command.callback:
                actual_cmd = ctx.command.callback.__name__
            else:
                actual_cmd = ctx.command.name


            # Store context for log function
            _execution_context = {
                "app_name": app_name,
                "command": actual_cmd,
                "params": ctx.params,
                "start_time": start.isoformat(),
            }

            row = {
                "type": "command",
                "app_name": app_name,
                "command": actual_cmd,
                "params": ctx.params,
                "start_time": start.isoformat(),
                "ts": start.isoformat(timespec="minutes")
            }

            res = None
            try:
                res = _original_invoke(self, ctx)
            except Exception as e:
                row["error"] = str(e)
                print(e)
            finally:
                row["duration"] = humanize.naturaldelta(datetime.now() - start)
                if res and isinstance(res, Path):
                    row["result"] = str(res)
                with log_fp.open("a", encoding="utf-8") as fout:
                    fout.write(json.dumps(row, default=safe_serializer) + os.linesep)

            return res

        # Apply the patch
        module_ = typer.core.TyperCommand.invoke.__module__
        orig_module = "click.core"
        modules = [orig_module, "tools.typer_log"]
        if module_ not in modules:
            print(f"warning typer invoke command should be either : {modules}. Fix the library")
        if module_ == orig_module:
            typer.core.TyperCommand.invoke = patched_invoke

    def log(message, level="info", **extra_data):
        """Custom log function that includes execution context"""
        global _execution_context, _log_buffer

        log_entry = {
            "type": "log",
            "level": level,
            "message": str(message),
            "ts": datetime.now().isoformat(),
            **extra_data
        }

        if _execution_context:
            log_entry.update(_execution_context)

        _log_buffer.append(log_entry)

    def close():
        """Flush all buffered logs to file"""
        global _log_buffer
        if not _log_buffer:
            return

        log_fp = root() / "data/typer-log.jsonl"
        with log_fp.open("a", encoding="utf-8") as fout:
            for entry in _log_buffer:
                fout.write(json.dumps(entry, default=safe_serializer) + os.linesep)
        _log_buffer.clear()

    # Patch Typer class to add log method
    def add_log_to_typer():
        original_init = typer.Typer.__init__

        def patched_init(self, *args, **kwargs):
            global _execution_context
            original_init(self, *args, **kwargs)
            self.log = log
            self.close = close
            _execution_context["app"] = self

        typer.Typer.__init__ = patched_init

    add_log_to_typer()

except ModuleNotFoundError as err:
    get_logger(__file__).error(err)
    def patch_typer_invoke(_):
        pass
    def log(*args, **kwargs):
        pass


