"""Official signed Antigravity CLI (`agy`) Python wrapper.

Zero external dependencies (Python 3.10+ stdlib only).
Works cleanly on Windows 11 with Smart App Control enabled by invoking the
Google-signed `agy.exe` binary directly via `-p / --output-format json|stream-json`.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterator


class AgyCliError(RuntimeError):
  """Raised when the `agy` CLI exits with an error or returns invalid output."""


@dataclass(frozen=True)
class AgyResult:
  """Structured response returned by `agy -p ... --output-format json`."""

  response: str
  conversation_id: str | None = None
  status: str = "SUCCESS"
  duration_seconds: float | None = None
  num_turns: int | None = None
  usage: dict[str, Any] = field(default_factory=dict)
  raw: dict[str, Any] = field(default_factory=dict)


def find_agy_executable(explicit_path: str | os.PathLike[str] | None = None) -> str:
  """Locates the signed `agy` executable on Windows, macOS, or Linux."""
  if explicit_path:
    p = Path(explicit_path).expanduser().resolve()
    if p.is_file():
      return str(p)
    raise FileNotFoundError(f"Specified agy executable not found: {p}")

  in_path = shutil.which("agy")
  if in_path:
    return in_path

  if os.name == "nt":
    local_app = os.environ.get("LOCALAPPDATA")
    if local_app:
      cand = Path(local_app) / "agy" / "bin" / "agy.exe"
      if cand.is_file():
        return str(cand)

  raise FileNotFoundError(
      "Could not locate `agy` executable. Ensure Antigravity CLI is installed and in PATH."
  )


class AgyClient:
  """High-level synchronous/asynchronous Python client backed by signed `agy` CLI."""

  def __init__(
      self,
      *,
      agy_path: str | os.PathLike[str] | None = None,
      project: str | None = None,
      model: str | None = None,
      effort: str | None = None,
      mode: str | None = None,
      cwd: str | os.PathLike[str] | None = None,
      add_dirs: list[str | os.PathLike[str]] | None = None,
      dangerously_skip_permissions: bool = False,
  ) -> None:
    self.agy_path = find_agy_executable(agy_path)
    self.project = project
    self.model = model
    self.effort = effort
    self.mode = mode
    self.cwd = str(Path(cwd).resolve()) if cwd else None
    self.add_dirs = [str(Path(d).resolve()) for d in (add_dirs or [])]
    self.dangerously_skip_permissions = dangerously_skip_permissions

  def _build_args(
      self,
      prompt: str,
      *,
      output_format: str = "json",
      model: str | None = None,
      effort: str | None = None,
      mode: str | None = None,
      project: str | None = None,
      conversation_id: str | None = None,
      continue_last: bool = False,
      json_schema: dict[str, Any] | str | None = None,
      print_timeout: str | None = None,
      extra_args: list[str] | None = None,
  ) -> list[str]:
    args: list[str] = [self.agy_path, "-p", prompt, "--output-format", output_format]

    eff_project = project if project is not None else self.project
    eff_model = model if model is not None else self.model
    eff_effort = effort if effort is not None else self.effort
    eff_mode = mode if mode is not None else self.mode

    if eff_project:
      args.extend(["--project", eff_project])
    if eff_model:
      args.extend(["--model", eff_model])
    if eff_effort:
      args.extend(["--effort", eff_effort])
    if eff_mode:
      args.extend(["--mode", eff_mode])
    if conversation_id:
      args.extend(["--conversation", conversation_id])
    elif continue_last:
      args.append("--continue")
    if json_schema is not None:
      schema_str = json.dumps(json_schema, ensure_ascii=False) if isinstance(json_schema, dict) else str(json_schema)
      args.extend(["--json-schema", schema_str])
    if print_timeout:
      args.extend(["--print-timeout", print_timeout])
    for d in self.add_dirs:
      args.extend(["--add-dir", d])
    if self.dangerously_skip_permissions:
      args.append("--dangerously-skip-permissions")
    if extra_args:
      args.extend(extra_args)
    return args

  @staticmethod
  def _parse_json_output(stdout: str, stderr: str, returncode: int) -> AgyResult:
    if returncode != 0:
      raise AgyCliError(f"agy exited with code {returncode}: {(stderr or stdout).strip()}")

    text = stdout.strip()
    if not text:
      raise AgyCliError(f"agy returned empty output. stderr={stderr.strip()}")

    try:
      data = json.loads(text)
    except json.JSONDecodeError as exc:
      # Fallback if non-JSON prefix lines were emitted before final JSON object
      last_line = text.splitlines()[-1]
      try:
        data = json.loads(last_line)
      except json.JSONDecodeError:
        raise AgyCliError(f"Failed to parse agy JSON output: {exc}\nRaw: {text[:500]}") from exc

    return AgyResult(
        response=str(data.get("response", "")),
        conversation_id=data.get("conversation_id"),
        status=str(data.get("status", "UNKNOWN")),
        duration_seconds=data.get("duration_seconds"),
        num_turns=data.get("num_turns"),
        usage=data.get("usage") or {},
        raw=data,
    )

  def run(
      self,
      prompt: str,
      *,
      model: str | None = None,
      effort: str | None = None,
      mode: str | None = None,
      project: str | None = None,
      conversation_id: str | None = None,
      continue_last: bool = False,
      json_schema: dict[str, Any] | str | None = None,
      timeout: float | None = 300.0,
      extra_args: list[str] | None = None,
  ) -> AgyResult:
    """Runs a prompt synchronously and returns a structured `AgyResult`."""
    args = self._build_args(
        prompt,
        output_format="json",
        model=model,
        effort=effort,
        mode=mode,
        project=project,
        conversation_id=conversation_id,
        continue_last=continue_last,
        json_schema=json_schema,
        extra_args=extra_args,
    )
    proc = subprocess.run(
        args,
        cwd=self.cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return self._parse_json_output(proc.stdout, proc.stderr, proc.returncode)

  async def arun(
      self,
      prompt: str,
      *,
      model: str | None = None,
      effort: str | None = None,
      mode: str | None = None,
      project: str | None = None,
      conversation_id: str | None = None,
      continue_last: bool = False,
      json_schema: dict[str, Any] | str | None = None,
      timeout: float | None = 300.0,
      extra_args: list[str] | None = None,
  ) -> AgyResult:
    """Runs a prompt asynchronously and returns a structured `AgyResult`."""
    args = self._build_args(
        prompt,
        output_format="json",
        model=model,
        effort=effort,
        mode=mode,
        project=project,
        conversation_id=conversation_id,
        continue_last=continue_last,
        json_schema=json_schema,
        extra_args=extra_args,
    )
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=self.cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
      out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
      proc.kill()
      await proc.wait()
      raise
    stdout = out_b.decode("utf-8", errors="replace")
    stderr = err_b.decode("utf-8", errors="replace")
    return self._parse_json_output(stdout, stderr, proc.returncode or 0)

  def stream(
      self,
      prompt: str,
      *,
      model: str | None = None,
      effort: str | None = None,
      mode: str | None = None,
      project: str | None = None,
      conversation_id: str | None = None,
      continue_last: bool = False,
      extra_args: list[str] | None = None,
  ) -> Iterator[dict[str, Any]]:
    """Yields parsed NDJSON events from `agy -p ... --output-format stream-json`."""
    args = self._build_args(
        prompt,
        output_format="stream-json",
        model=model,
        effort=effort,
        mode=mode,
        project=project,
        conversation_id=conversation_id,
        continue_last=continue_last,
        extra_args=extra_args,
    )
    with subprocess.Popen(
        args,
        cwd=self.cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    ) as proc:
      assert proc.stdout is not None
      for line in proc.stdout:
        s = line.strip()
        if not s:
          continue
        try:
          yield json.loads(s)
        except json.JSONDecodeError:
          yield {"type": "raw", "text": s}
      rc = proc.wait()
      if rc != 0:
        err_text = proc.stderr.read().strip() if proc.stderr else ""
        raise AgyCliError(f"agy stream exited with code {rc}: {err_text}")
