"""Actual frozen-executable export and loopback smoke test by Jason Stys.

Functions: main, read_output. Variables: process, queue, temporary output, HTTP responses.
Line inventory: docs/CODE_INDEX.md. Starts/stops only the explicitly supplied owned bundle.
Preserved domain acceptance; canonical process/version/browser proof is in smoke_app.py."""

import json
import queue
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

if __package__:
    from .release_contract import require
else:
    from release_contract import require


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A local application check never follows an HTTP redirect to another listener or origin."""

    def redirect_request(self, *args, **kwargs):
        """Abort before urllib can issue the redirected request."""
        raise ValueError("Local native acceptance refuses redirects")


OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirects())


def main(executable: Path) -> None:
    """Verify packaged C++ worker/resources, health, scenario API and real built HTML/JS."""
    executable = executable.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="thermal-smoke-") as temporary:
        output = Path(temporary) / "evidence.json"
        subprocess.run(
            [str(executable), "export", "--scenario", "baseline", "--output", str(output)],
            check=True,
            timeout=30,
        )
        require(
            bool(json.loads(output.read_bytes())["provenance"]["units"] == "dimensionless"),
            "Preserved native acceptance check failed",
        )
    process = subprocess.Popen(
        [str(executable), "serve", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        """Read child stdout without a blocking readline in the timeout-owning main thread."""
        require(bool(process.stdout is not None), "Preserved native acceptance check failed")
        for line in process.stdout:
            lines.put(line.strip())

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        url = ""
        for _ in range(5):
            line = lines.get(timeout=15)
            if line.startswith("http://127.0.0.1:"):
                url = line
                break
        require(bool(url), "Frozen server did not announce a loopback URL")
        with OPENER.open(url + "api/health", timeout=5) as response:
            require(
                bool(json.loads(response.read())["status"] == "ok"),
                "Preserved native acceptance check failed",
            )
        with OPENER.open(url, timeout=5) as response:
            html = response.read().decode()
            require(
                bool("Reactor Systems Simulator" in html and "/assets/" in html),
                "Preserved native acceptance check failed",
            )
        with OPENER.open(url + "api/run?scenario=cooling-dip&duration=300", timeout=5) as response:
            require(
                bool(json.loads(response.read())["experiment"]["max_balance_error"] < 1e-08),
                "Preserved native acceptance check failed",
            )
        print("Frozen app: C++ numerical export, web assets, health and scenario API passed")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=3)
        if process.stdout:
            process.stdout.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
