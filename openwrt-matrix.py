#!/usr/bin/env python3
"""Generate a GitHub Actions build matrix for OpenWrt release targets.

The script intentionally uses only the Python standard library.

Positional interface:
    ./openwrt-matrix.py VERSION [INCLUDE] [EXCLUDE]

Examples:
    ./openwrt-matrix.py 25.12.5
    ./openwrt-matrix.py 25.12.5 '*'
    ./openwrt-matrix.py 25.12.5 'x86/*'
    ./openwrt-matrix.py 25.12.5 'x86/64,mediatek/filogic'
    ./openwrt-matrix.py 25.12.5 '*' 'microchipsw/lan969x'
    ./openwrt-matrix.py 25.12.5 'all' 'microchipsw/*' --pretty

GitHub Actions:
    ./openwrt-matrix.py "$VERSION" "$INCLUDE" "$EXCLUDE"
    # writes job-config=<json> to $GITHUB_OUTPUT when present
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

USER_AGENT = "openwrt-matrix-generator/1.0"
DEFAULT_TIMEOUT = 30


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return

        for name, value in attrs:
            if name.lower() == "href" and value:
                self.hrefs.append(value)
                return


@dataclass(frozen=True)
class OpenWrtTarget:
    tag: str
    target: str
    subtarget: str
    pkgarch: str

    @property
    def board(self) -> str:
        return f"{self.target}/{self.subtarget}"

    def as_matrix_item(self) -> dict[str, str]:
        return {
            "tag": self.tag,
            "target": self.target,
            "subtarget": self.subtarget,
            "board": self.board,
            "pkgarch": self.pkgarch,
        }


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def normalize_version(version: str) -> str:
    version = version.strip()

    if version.startswith("v"):
        version = version[1:]

    if not version:
        die("OpenWrt version is required")

    return version


def split_patterns(value: str | None) -> list[str]:
    if not value:
        return []

    patterns: list[str] = []

    for item in value.split(","):
        pattern = item.strip().strip("/")
        if not pattern:
            continue

        if pattern == "all":
            pattern = "*"

        patterns.append(pattern)

    return patterns


def matches_pattern(target: str, subtarget: str, pattern: str) -> bool:
    board = f"{target}/{subtarget}"

    if pattern in ("*", "all"):
        return True

    if "/" not in pattern:
        return fnmatch.fnmatchcase(target, pattern)

    return fnmatch.fnmatchcase(board, pattern)


def matches_any_pattern(target: str, subtarget: str, patterns: list[str]) -> bool:
    return any(matches_pattern(target, subtarget, pattern) for pattern in patterns)


def is_selected(
    target: str,
    subtarget: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> bool:
    if include_patterns and not matches_any_pattern(
        target, subtarget, include_patterns
    ):
        return False

    if exclude_patterns and matches_any_pattern(target, subtarget, exclude_patterns):
        return False

    return True


def fetch_bytes(url: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read()


def fetch_text(url: str) -> str:
    return fetch_bytes(url).decode("utf-8", errors="replace")


def fetch_json(url: str) -> dict:
    return json.loads(fetch_text(url))


def directory_links(url: str) -> list[str]:
    parser = LinkParser()
    parser.feed(fetch_text(url))

    base = url if url.endswith("/") else f"{url}/"

    entries: list[str] = []
    seen: set[str] = set()

    for href in parser.hrefs:
        href = href.split("#", 1)[0].split("?", 1)[0]

        if not href.endswith("/"):
            continue

        absolute = urljoin(base, href)

        if absolute == base:
            continue

        if not absolute.startswith(base):
            continue

        relative = absolute[len(base) :].strip("/")

        if not relative or "/" in relative:
            continue

        name = relative

        if name == ".." or name.startswith("."):
            continue

        if name not in seen:
            seen.add(name)
            entries.append(name)

    return sorted(entries)


def get_pkgarch(base_url: str, target: str, subtarget: str) -> str:
    index_url = f"{base_url}{target}/{subtarget}/packages/index.json"

    try:
        data = fetch_json(index_url)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
        return ""

    architecture = data.get("architecture", "")

    return str(architecture) if architecture is not None else ""


def openwrt_matrix(
    version: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> list[dict[str, str]]:
    version = normalize_version(version)
    base_url = f"https://downloads.openwrt.org/releases/{version}/targets/"

    targets = directory_links(base_url)

    if not targets:
        die(f"no targets found at {base_url}")

    matrix: list[dict[str, str]] = []

    for target in targets:
        target_url = f"{base_url}{target}/"

        try:
            subtargets = directory_links(target_url)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            print(
                f"warning: cannot read subtargets for {target}: {exc}",
                file=sys.stderr,
            )
            continue

        for subtarget in subtargets:
            if not is_selected(target, subtarget, include_patterns, exclude_patterns):
                continue

            pkgarch = get_pkgarch(base_url, target, subtarget)

            if not pkgarch:
                die(f"cannot determine pkgarch for {target}/{subtarget}")

            matrix_item = OpenWrtTarget(
                tag=version,
                target=target,
                subtarget=subtarget,
                pkgarch=pkgarch,
            ).as_matrix_item()

            matrix.append(matrix_item)

    return matrix


def write_github_output(name: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")

    if not github_output:
        return

    with open(github_output, "a", encoding="utf-8") as output:
        output.write(f"{name}={value}\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate OpenWrt target/subtarget GitHub Actions matrix."
    )

    parser.add_argument(
        "version",
        help="OpenWrt release version, with or without leading v",
    )

    parser.add_argument(
        "include_pos",
        nargs="?",
        default="*",
        help="comma-separated include patterns, for example '*', 'x86/*', 'x86/64'",
    )

    parser.add_argument(
        "exclude_pos",
        nargs="?",
        default="",
        help="comma-separated exclude patterns, for example 'microchipsw/lan969x'",
    )

    parser.add_argument(
        "--include",
        dest="include_opt",
        default="",
        help="comma-separated include patterns",
    )

    parser.add_argument(
        "--exclude",
        dest="exclude_opt",
        default="",
        help="comma-separated exclude patterns",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON to stdout",
    )

    parser.add_argument(
        "--no-github-output",
        action="store_true",
        help="do not write job-config to $GITHUB_OUTPUT",
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    include = split_patterns(args.include_opt or args.include_pos)
    exclude = split_patterns(args.exclude_opt or args.exclude_pos)

    if not include:
        include = ["*"]

    try:
        matrix = openwrt_matrix(args.version, include, exclude)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        die(str(exc))

    if not matrix:
        die(
            "matrix is empty; check version/include/exclude filters "
            f"(version={args.version!r}, include={include!r}, exclude={exclude!r})"
        )

    compact = json.dumps(matrix, separators=(",", ":"), ensure_ascii=False)

    if not args.no_github_output:
        write_github_output("job-config", compact)

    if args.pretty:
        print(json.dumps(matrix, indent=2, ensure_ascii=False))
    else:
        print(compact)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
