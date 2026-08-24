#!/usr/bin/env python3
# Copyright (C) 2026 Karen Khachatryan <karen0734@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-only
# GitHub: https://github.com/karen07

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AwgOpt:
    name: str
    kind: str
    placeholder: str | None
    description: str

    @property
    def lower(self) -> str:
        return self.name.lower()

    @property
    def snake(self) -> str:
        value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", self.name)
        value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
        return value.lower()

    @property
    def uci(self) -> str:
        return f"awg_{self.snake}"

    @property
    def proto_config_type(self) -> str:
        if self.kind == "bool":
            return "boolean"

        return self.kind

    @property
    def luci_datatype(self) -> str:
        if self.kind == "int":
            return "uinteger"

        return "string"


AWG_OPTS = [
    AwgOpt("Jc", "int", "4", "Junk packet count, 0-10."),
    AwgOpt("Jmin", "int", "64", "Junk packet minimum size, 64-1024 bytes."),
    AwgOpt("Jmax", "int", "205", "Junk packet maximum size, 64-1024 bytes."),
    AwgOpt(
        "S1",
        "int",
        "56",
        "Handshake initiation random prefix size, 0-64 bytes.",
    ),
    AwgOpt(
        "S2",
        "int",
        "48",
        "Handshake response random prefix size, 0-64 bytes.",
    ),
    AwgOpt(
        "S3",
        "int",
        "32",
        "Cookie reply random prefix size, 0-64 bytes.",
    ),
    AwgOpt(
        "S4",
        "int",
        "16",
        "Transport packet random prefix size, 0-32 bytes.",
    ),
    AwgOpt(
        "H1",
        "string",
        "135792468-135903579",
        "Handshake initiation packet type header. "
        "Number or range, 0-4294967295. "
        "H1-H4 ranges must not overlap.",
    ),
    AwgOpt(
        "H2",
        "string",
        "864201357-864312468",
        "Handshake response packet type header. "
        "Number or range, 0-4294967295. "
        "H1-H4 ranges must not overlap.",
    ),
    AwgOpt(
        "H3",
        "string",
        "2198765432-2198876543",
        "Handshake cookie packet type header. "
        "Number or range, 0-4294967295. "
        "H1-H4 ranges must not overlap.",
    ),
    AwgOpt(
        "H4",
        "string",
        "4012345678-4012456789",
        "Transport packet type header. "
        "Number or range, 0-4294967295. "
        "H1-H4 ranges must not overlap.",
    ),
    AwgOpt("I1", "string", "<r 128>", "First special junk packet signature."),
    AwgOpt("I2", "string", None, "Second special junk packet signature."),
    AwgOpt("I3", "string", None, "Third special junk packet signature."),
    AwgOpt("I4", "string", None, "Fourth special junk packet signature."),
    AwgOpt("I5", "string", None, "Fifth special junk packet signature."),
    AwgOpt(
        "HeaderProtectionKey",
        "string",
        None,
        "Header protection key shared by both sides. 32-byte Base64 key.",
    ),
    AwgOpt(
        "ContentPaddingAddition",
        "string",
        None,
        "Content padding addition. Number or range, 0-65535 bytes.",
    ),
    AwgOpt(
        "RekeyAfterTime",
        "string",
        None,
        "Rekey after time. Number or range, 0-65535 seconds.",
    ),
    AwgOpt(
        "RekeyTimeout",
        "string",
        None,
        "Rekey timeout. Number or range, 0-65535 seconds.",
    ),
    AwgOpt(
        "RejectAfterTime",
        "string",
        None,
        "Reject after time. Number or range, 0-65535 seconds.",
    ),
    AwgOpt(
        "KeepaliveTimeout",
        "string",
        None,
        "Keepalive timeout. Number or range, 0-65535 seconds.",
    ),
    AwgOpt(
        "MaxHandshakeAttempts",
        "string",
        None,
        "Maximum handshake attempts. Number or range, 0-65535 attempts.",
    ),
    AwgOpt(
        "RandomTrailers",
        "bool",
        None,
        "Enable random packet trailers.",
    ),
    AwgOpt(
        "DisableCookies",
        "bool",
        None,
        "Disable cookie messages.",
    ),
]


AWG_TOOLS_VERSION = "3.1.20260812"
AWG_KERNEL_VERSION = "3.1.20260828"
AWG_TOOLS_REPO = os.environ.get(
    "AWG_TOOLS_REPO",
    "https://github.com/amnezia-vpn/amneziawg-tools.git",
)
AWG_KERNEL_REPO = os.environ.get(
    "AWG_KERNEL_REPO",
    "https://github.com/amnezia-vpn/amneziawg-linux-kernel-module.git",
)
AWG_LUCI_VERSION = "3.1.0"
AWG_LUCI_NAME = "luci-proto-amneziawg"
PROJECT_AUTHOR = "Karen Khachatryan"
PROJECT_EMAIL = "karen0734@gmail.com"
PROJECT_COPYRIGHT = f"Copyright (C) 2026 {PROJECT_AUTHOR} <{PROJECT_EMAIL}>"
AWG_MAINTAINER = f"{PROJECT_AUTHOR} <{PROJECT_EMAIL}>"
AWG_LUCI_MK_INCLUDE = "include $(TOPDIR)/feeds/luci/luci.mk"


OPENWRT_REPO = os.environ.get(
    "OPENWRT_REPO",
    "https://github.com/openwrt/openwrt.git",
)
OPENWRT_REF = os.environ.get("OPENWRT_REF", "openwrt-25.12")
OPENWRT_WG_TOOLS_DIR = "package/network/utils/wireguard-tools"

LUCI_REPO = os.environ.get(
    "LUCI_REPO",
    "https://github.com/openwrt/luci.git",
)
LUCI_REF = os.environ.get("LUCI_REF", "openwrt-25.12")
LUCI_WG_PROTO_DIR = "protocols/luci-proto-wireguard"

AWG_TOOLS_DIR = Path("amneziawg-tools")
AWG_FILES_DIR = AWG_TOOLS_DIR / "files"
AWG_TOOLS_PROTO_FILE = AWG_FILES_DIR / "amneziawg.sh"

AWG_LUCI_DIR = Path("luci-proto-amneziawg")
AWG_LUCI_PROTO_FILE = (
    AWG_LUCI_DIR / "htdocs/luci-static/resources/protocol/amneziawg.js"
)
AWG_LUCI_ICON_FILE = AWG_LUCI_DIR / "htdocs/luci-static/resources/icons/amneziawg.svg"
AWG_LUCI_ICON_REPO = os.environ.get(
    "AWG_LUCI_ICON_REPO",
    "https://raw.githubusercontent.com/Slava-Shchipunov/awg-openwrt",
)
AWG_LUCI_ICON_REF = os.environ.get("AWG_LUCI_ICON_REF", "master")
AWG_LUCI_ICON_PATH = (
    "luci-proto-amneziawg/htdocs/luci-static/resources/icons/amneziawg.svg"
)
AWG_LUCI_STATUS_FILE = (
    AWG_LUCI_DIR / "htdocs/luci-static/resources/view/amneziawg/status.js"
)
AWG_LUCI_RPCD_FILE = AWG_LUCI_DIR / "root/usr/share/rpcd/ucode/luci.amneziawg"

AWG_KMOD_DIR = Path("kmod-amneziawg")
AWG_KMOD_MAKEFILE = AWG_KMOD_DIR / "Makefile"

OPENWRT_SRC_DIR = Path(".openwrt-wg-src")
LUCI_SRC_DIR = Path(".luci-proto-wireguard-src")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def latest_awg_tag(repo: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", repo, "v*"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )

    tags = []
    for line in result.stdout.splitlines():
        tag = line.rsplit("refs/tags/", 1)[-1]
        match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d{8})(?:-(\d+))?", tag)
        if match:
            key = tuple(int(value or 0) for value in match.groups())
            tags.append((key, tag))

    if not tags:
        raise RuntimeError(f"no AWG release tags found in {repo}")

    return max(tags)[1]


def check_awg_version() -> None:
    tools_pinned = f"v{AWG_TOOLS_VERSION}"
    kernel_pinned = f"v{AWG_KERNEL_VERSION}"
    tools = latest_awg_tag(AWG_TOOLS_REPO)
    kernel = latest_awg_tag(AWG_KERNEL_REPO)

    print(
        "AWG versions: "
        f"tools={tools_pinned} (upstream {tools}), "
        f"kernel={kernel_pinned} (upstream {kernel})"
    )

    if tools != tools_pinned or kernel != kernel_pinned:
        raise RuntimeError(
            "AmneziaWG version changed upstream; review AWG changes and update "
            "AWG_TOOLS_VERSION and/or AWG_KERNEL_VERSION before regenerating "
            "the package"
        )


def rm_rf(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def sparse_checkout(
    work_dir: Path,
    repo: str,
    ref: str,
    sparse_dir: str,
) -> None:
    rm_rf(work_dir)
    work_dir.mkdir(parents=True)

    run(["git", "-C", str(work_dir), "init", "-q"])
    run(["git", "-C", str(work_dir), "remote", "add", "origin", repo])
    run(["git", "-C", str(work_dir), "sparse-checkout", "init", "--cone"])
    run(["git", "-C", str(work_dir), "sparse-checkout", "set", sparse_dir])
    run(["git", "-C", str(work_dir), "fetch", "--depth=1", "origin", ref])
    run(["git", "-C", str(work_dir), "checkout", "-q", "--detach", "FETCH_HEAD"])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_copyright_after_existing(path: Path, *, prefix: str) -> None:
    text = read_text(path)
    copyright_line = f"{prefix} {PROJECT_COPYRIGHT}\n"

    if copyright_line in text:
        return

    lines = text.splitlines(keepends=True)
    pattern = re.compile(rf"^{re.escape(prefix)}\s*Copyright(?: \(C\))?\b")
    matches = [
        index
        for index, line in enumerate(lines[:20])
        if pattern.search(line.rstrip("\n"))
    ]

    if not matches:
        raise RuntimeError(f"copyright header not found in {path}")

    lines.insert(matches[-1] + 1, copyright_line)
    write_text(path, "".join(lines))


def add_modifications_copyright(path: Path, *, prefix: str) -> None:
    text = read_text(path)
    copyright_line = f"{prefix} AmneziaWG modifications: {PROJECT_COPYRIGHT}\n"

    if copyright_line in text:
        return

    lines = text.splitlines(keepends=True)
    lines.insert(0, copyright_line)
    write_text(path, "".join(lines))


def download_file(url: str, path: Path) -> None:
    print(f"Fetching: {url}")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "amneziawg-openwrt-package/generate.py"},
    )
    with urllib.request.urlopen(request) as response:
        data = response.read()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def replace_literal_once(
    text: str,
    old: str,
    new: str,
    *,
    path: Path,
    label: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one marker in {path}, found {count}"
        )

    return text.replace(old, new, 1)


def sub_regex_once(
    text: str,
    pattern: str,
    replacement: str,
    *,
    path: Path,
    label: str,
    flags: int = 0,
) -> str:
    new_text, count = re.subn(
        pattern,
        replacement,
        text,
        flags=flags,
    )

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one regex match in {path}, found {count}"
        )

    return new_text


def try_read_utf8(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def is_svg(path: Path) -> bool:
    return path.suffix.lower() == ".svg"


def insert_after_line(path: Path, marker_regex: str, block: str) -> None:
    text = read_text(path)
    if not block.endswith("\n"):
        block += "\n"

    lines = text.splitlines(keepends=True)
    matches = [
        index for index, line in enumerate(lines) if re.search(marker_regex, line)
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one marker in {path}: {marker_regex}; "
            f"found {len(matches)}"
        )

    lines.insert(matches[0] + 1, block)
    write_text(path, "".join(lines))


def replace_call_block(path: Path, start_regex: str, block: str) -> None:
    text = read_text(path)
    if not block.endswith("\n"):
        block += "\n"

    lines = text.splitlines(keepends=True)
    start_matches = [
        index for index, line in enumerate(lines) if re.search(start_regex, line)
    ]

    if len(start_matches) != 1:
        raise RuntimeError(
            f"expected exactly one start marker in {path}: {start_regex}; "
            f"found {len(start_matches)}"
        )

    start_index = start_matches[0]
    end_index = None

    for index in range(start_index, len(lines)):
        if ");" in lines[index]:
            end_index = index
            break

    if end_index is None:
        raise RuntimeError(f"end of call not found in {path}: {start_regex}")

    new_lines = lines[:start_index] + [block] + lines[end_index + 1 :]
    write_text(path, "".join(new_lines))


def rewrite_text_tree(root: Path, transform, skip_path=None) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if skip_path is not None and skip_path(path):
            continue

        text = try_read_utf8(path)
        if text is None:
            continue

        new_text = transform(text)

        if new_text != text:
            write_text(path, new_text)


def rename_path(old: Path, new: Path) -> None:
    if not old.exists() and not old.is_symlink():
        raise RuntimeError(f"path not found: {old}")

    if new.exists() or new.is_symlink():
        raise RuntimeError(f"destination already exists: {new}")

    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)


def rename_wg_to_awg_text(text: str, *, replace_wg0_conf: bool) -> str:
    text = text.replace("Wg", "Awg")
    text = text.replace("WG", "AWG")
    text = re.sub(r"\bwg\b", "awg", text)
    text = re.sub(r"(^|[^a])wg_", r"\1awg_", text, flags=re.MULTILINE)

    if replace_wg0_conf:
        text = text.replace("wg0.conf", "awg0.conf")

    text = text.replace("wireguard", "amneziawg")
    text = text.replace("WireGuard", "AmneziaWG")
    text = text.replace("Wireguard", "AmneziaWG")

    return text


def update_tools_makefile(path: Path) -> None:
    text = read_text(path)

    lines = text.splitlines()
    new_lines: list[str] = []
    version_count = 0
    release_count = 0
    skip_prefixes = (
        "PKG_SOURCE:=",
        "PKG_SOURCE_URL:=",
        "PKG_HASH:=",
        "PKG_MIRROR_HASH:=",
        "PKG_SOURCE_PROTO:=",
        "PKG_SOURCE_VERSION:=",
        "PKG_SOURCE_DATE:=",
    )

    for line in lines:
        if line.startswith("PKG_VERSION:="):
            version_count += 1
            new_lines.append(f"PKG_VERSION:={AWG_TOOLS_VERSION}")
            continue

        if line.startswith("PKG_RELEASE:="):
            release_count += 1
            new_lines.extend(
                [
                    "PKG_RELEASE:=1",
                    "",
                    "PKG_SOURCE_PROTO:=git",
                    "PKG_SOURCE_URL:=https://github.com/amnezia-vpn/amneziawg-tools.git",
                    "PKG_SOURCE_VERSION:=v$(PKG_VERSION)",
                ]
            )
            continue

        if line.startswith(skip_prefixes):
            continue

        new_lines.append(line)

    if version_count != 1:
        raise RuntimeError(
            f"expected exactly one PKG_VERSION marker in {path}, found {version_count}"
        )

    if release_count != 1:
        raise RuntimeError(
            f"expected exactly one PKG_RELEASE marker in {path}, found {release_count}"
        )

    text = "\n".join(new_lines) + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = sub_regex_once(
        text,
        r"^(\s*URL:=).*$",
        r"\1https://amnezia.org/",
        path=path,
        label="package URL",
        flags=re.MULTILINE,
    )
    text = sub_regex_once(
        text,
        r"^(\s*MAINTAINER:=).*$",
        rf"\1{AWG_MAINTAINER}",
        path=path,
        label="package maintainer",
        flags=re.MULTILINE,
    )

    source_assignments = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^(?:PKG_SOURCE(?:_|\b)|PKG_(?:MIRROR_)?HASH\b)", line.strip())
    ]
    expected_source_assignments = [
        "PKG_SOURCE_PROTO:=git",
        "PKG_SOURCE_URL:=https://github.com/amnezia-vpn/amneziawg-tools.git",
        "PKG_SOURCE_VERSION:=v$(PKG_VERSION)",
    ]
    if source_assignments != expected_source_assignments:
        raise RuntimeError(
            f"unexpected package source assignments in {path}: "
            f"{source_assignments!r}"
        )

    write_text(path, text)
    add_copyright_after_existing(path, prefix="#")


def fix_tools_install_binary_name(path: Path) -> None:
    text = read_text(path)
    old = "\t$(INSTALL_BIN) $(PKG_BUILD_DIR)/src/awg $(1)/usr/bin/"
    new = "\t$(INSTALL_BIN) $(PKG_BUILD_DIR)/src/wg $(1)/usr/bin/awg"

    text = replace_literal_once(
        text,
        old,
        new,
        path=path,
        label="tools install binary",
    )
    write_text(path, text)


def rewrite_luci_mk_include(text: str, path: Path) -> str:
    old = "include ../../luci.mk"
    return replace_literal_once(
        text,
        old,
        AWG_LUCI_MK_INCLUDE,
        path=path,
        label="luci.mk include",
    )


def update_luci_makefile(path: Path) -> None:
    text = read_text(path)
    text = rewrite_luci_mk_include(text, path)

    version_line = f"PKG_VERSION:={AWG_LUCI_VERSION}"
    luci_name_line = f"LUCI_NAME:={AWG_LUCI_NAME}"

    version_matches = len(re.findall(r"^PKG_VERSION:=", text, flags=re.MULTILINE))
    if version_matches > 1:
        raise RuntimeError(
            f"expected at most one PKG_VERSION marker in {path}, found {version_matches}"
        )
    if version_matches == 1:
        text = sub_regex_once(
            text,
            r"^PKG_VERSION:=.*$",
            version_line,
            path=path,
            label="LuCI PKG_VERSION",
            flags=re.MULTILINE,
        )
    else:
        text = replace_literal_once(
            text,
            "include $(TOPDIR)/rules.mk\n",
            f"include $(TOPDIR)/rules.mk\n\n{version_line}\n",
            path=path,
            label="LuCI rules.mk insertion point",
        )

    luci_name_matches = len(re.findall(r"^LUCI_NAME:=", text, flags=re.MULTILINE))
    if luci_name_matches > 1:
        raise RuntimeError(
            f"expected at most one LUCI_NAME marker in {path}, found {luci_name_matches}"
        )
    if luci_name_matches == 1:
        text = sub_regex_once(
            text,
            r"^LUCI_NAME:=.*$",
            luci_name_line,
            path=path,
            label="LuCI package name",
            flags=re.MULTILINE,
        )
    else:
        text = replace_literal_once(
            text,
            f"{version_line}\n",
            f"{version_line}\n\n{luci_name_line}\n",
            path=path,
            label="LuCI name insertion point",
        )

    text = sub_regex_once(
        text,
        r"^PKG_MAINTAINER:=.*$",
        f"PKG_MAINTAINER:={AWG_MAINTAINER}",
        path=path,
        label="LuCI maintainer",
        flags=re.MULTILINE,
    )

    if text.count(version_line) != 1:
        raise RuntimeError(f"PKG_VERSION marker not added exactly once in {path}")
    if text.count(luci_name_line) != 1:
        raise RuntimeError(f"LUCI_NAME marker not added exactly once in {path}")
    maintainer_line = f"PKG_MAINTAINER:={AWG_MAINTAINER}"
    if text.count(maintainer_line) != 1:
        raise RuntimeError(f"PKG_MAINTAINER marker not added exactly once in {path}")
    if text.count(AWG_LUCI_MK_INCLUDE) != 1:
        raise RuntimeError(f"luci.mk include not present exactly once in {path}")
    if "include ../../luci.mk" in text:
        raise RuntimeError(f"old luci.mk include still present in {path}")

    write_text(path, text)
    add_copyright_after_existing(path, prefix="#")


def js_quote(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "\\'")


def gen_tools_proto_config_adds() -> str:
    lines = [
        "",
        "\t# AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        line = f'\tproto_config_add_{opt.proto_config_type} "{opt.uci}"'
        lines.append(line)

    return "\n".join(lines) + "\n"


def gen_tools_local_vars() -> str:
    lines = [
        "",
        "\t# AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        lines.append(f"\tlocal {opt.uci}")

    lines.append("")
    return "\n".join(lines) + "\n"


def gen_tools_config_gets() -> str:
    lines = [
        "",
        "\t# AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        lines.append(f'\tconfig_get {opt.uci} "${{config}}" "{opt.uci}"')

    return "\n".join(lines) + "\n"


def gen_tools_awg_config_lines() -> str:
    lines = [
        "",
        "\t# AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        lines.append(
            f'\t[ -n "${{{opt.uci}}}" ] && '
            f'awg_config="${{awg_config}}{opt.name}=${{{opt.uci}}}\\n"'
        )

    return "\n".join(lines) + "\n"


def gen_luci_settings_tab() -> str:
    doc_html = (
        "_('Further information about AmneziaWG interfaces and peers at ' + "
        "'<a href=\\'https://docs.amnezia.org/documentation/amnezia-wg\\'>"
        "amnezia.org</a>.')"
    )

    lines = [
        "",
        "\t\t// AmneziaWG specific parameters",
        "\t\ttry {",
        ("\t\t\ts.tab('amneziawg', _('AmneziaWG Settings'), " f"{doc_html});"),
        "\t\t}",
        "\t\tcatch(e) {}",
    ]

    for opt in AWG_OPTS:
        lines.append("")
        if opt.kind == "bool":
            lines.append(
                "\t\to = s.taboption('amneziawg', form.Flag, "
                f"'{opt.uci}', _('{js_quote(opt.name)}'), "
                f"_('{js_quote(opt.description)}'));"
            )
        else:
            lines.extend(
                [
                    (
                        "\t\to = s.taboption('amneziawg', form.Value, "
                        f"'{opt.uci}', _('{js_quote(opt.name)}'), "
                        f"_('{js_quote(opt.description)}'));"
                    ),
                    f"\t\to.datatype = '{opt.luci_datatype}';",
                ]
            )

            if opt.placeholder is not None:
                lines.append(f"\t\to.placeholder = '{js_quote(opt.placeholder)}';")

        lines.append("\t\to.optional = true;")

    return "\n".join(lines) + "\n"


def gen_luci_peers_tab() -> str:
    doc_html = (
        "_('Further information about AmneziaWG interfaces and peers at ' + "
        "'<a href=\\'https://docs.amnezia.org/documentation/amnezia-wg\\'>"
        "amnezia.org</a>.')"
    )

    lines = [
        f"\t\t\ts.tab('peers', _('Peers'), {doc_html});",
    ]

    return "\n".join(lines) + "\n"


def gen_luci_import_setters() -> str:
    lines = [
        "",
        "\t\t\t\t\t// AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        if opt.kind == "bool":
            value = (
                f"(config.interface_{opt.lower} == 'on' || "
                f"+config.interface_{opt.lower}) ? '1' : '0'"
            )
        else:
            value = f"config.interface_{opt.lower} || ''"

        lines.append(
            f"\t\t\t\t\ts.getOption('{opt.uci}')"
            f".getUIElement(s.section).setValue({value});"
        )

    return "\n".join(lines) + "\n"


def gen_luci_export_vars() -> str:
    lines = [
        "",
        "\t\t\t// AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        lines.append(
            f"\t\t\tconst {opt.lower} = " f"s.formvalue(s.section, '{opt.uci}');"
        )

    return "\n".join(lines) + "\n"


def gen_luci_export_lines() -> str:
    lines = [
        "\t\t\t\t// AmneziaWG specific parameters",
    ]

    for opt in AWG_OPTS:
        lines.append(
            f"\t\t\t\t{opt.lower} ? "
            f"'{opt.name} = ' + {opt.lower} : "
            f"'# {opt.name} not defined',"
        )

    return "\n".join(lines) + "\n"


def make_qr_generation_defensive(path: Path) -> None:
    start_re = re.compile(r"const svg = uqr\.renderSVG\(data, options\);")
    end_re = re.compile(r"dom\.content\(code, Object\.assign\(E\(svg\)")

    text = read_text(path)
    lines = text.splitlines(keepends=True)
    start_matches = [index for index, line in enumerate(lines) if start_re.search(line)]
    end_matches = [index for index, line in enumerate(lines) if end_re.search(line)]

    if len(start_matches) != 1:
        raise RuntimeError(
            f"expected exactly one QR start marker in {path}, found {len(start_matches)}"
        )
    if len(end_matches) != 1:
        raise RuntimeError(
            f"expected exactly one QR end marker in {path}, found {len(end_matches)}"
        )

    start_index = start_matches[0]
    end_index = end_matches[0]
    if end_index < start_index:
        raise RuntimeError(f"QR end marker precedes start marker in {path}")

    before = lines[:start_index]
    body = ["\t" + line for line in lines[start_index : end_index + 1]]
    after = lines[end_index + 1 :]

    try_block = [
        "\n",
        "\t// Large configurations may exceed QR code size limits.\n",
        "\ttry {\n",
    ]

    qr_error = "QR code generation failed. The configuration may be too large."
    catch_block = [
        "\t} catch (e) {\n",
        "\t\tconsole.warn('QR generation failed:', e);\n",
        "\n",
        "\t\tcode.style.opacity = '';\n",
        (
            "\t\tdom.content(code, E('div', "
            "{'class': 'alert-message warning', "
            "'style': 'margin:0;text-align:center'}, "
            f"[_('{qr_error}')]));\n"
        ),
        "\t}\n",
    ]

    write_text(path, "".join(before + try_block + body + catch_block + after))


def fix_luci_persistent_keepalive(path: Path) -> None:
    text = read_text(path)

    validator_old = (
        "\n\t\t\t\tif (!stubValidator.apply('port', "
        "pconf.peer_persistentkeepalive || '0'))\n"
        "\t\t\t\t\treturn _('PersistentKeepAlive setting is invalid');"
    )
    form_old = (
        "\t\to = ss.option(form.Value, 'persistent_keepalive', "
        "_('Persistent Keep Alive'), "
        "_('Optional. Seconds between keep alive messages. Default is 0 (disabled). "
        "Recommended value if this device is behind a NAT is 25.'));\n"
        "\t\to.modalonly = true;\n"
        "\t\to.datatype = 'range(0,65535)';"
    )
    form_new = (
        "\t\to = ss.option(form.Value, 'persistent_keepalive', "
        "_('Persistent Keep Alive'), "
        "_('Optional. Seconds between keep alive messages. Number or range, 0-65535 seconds. "
        "Default is 0 (disabled).'));\n"
        "\t\to.modalonly = true;\n"
        "\t\to.datatype = 'string';"
    )

    text = replace_literal_once(
        text,
        validator_old,
        "",
        path=path,
        label="PersistentKeepalive validator",
    )
    text = replace_literal_once(
        text,
        form_old,
        form_new,
        path=path,
        label="PersistentKeepalive form",
    )

    write_text(path, text)


def fix_luci_status_persistent_keepalive(path: Path) -> None:
    text = read_text(path)
    old = "_('every %ds', 'AmneziaWG keep alive interval').format(+peer.persistent_keepalive)"
    new = "_('every %s seconds', 'AmneziaWG keep alive interval').format(peer.persistent_keepalive)"

    text = replace_literal_once(
        text,
        old,
        new,
        path=path,
        label="PersistentKeepalive status rendering",
    )
    write_text(path, text)


def gen_luci_rpcd_awg_fields() -> str:
    lines = []

    for index, opt in enumerate(AWG_OPTS, start=4):
        if opt.name == "HeaderProtectionKey":
            value = f"record[{index}] == '(none)' ? '(none)' : '(hidden)'"
        else:
            value = f"record[{index}]"

        lines.append(f"\t\t\t\t\t\t\t{opt.snake}: {value},")

    return "\n".join(lines)


def fix_luci_rpcd_dump(path: Path) -> None:
    text = read_text(path)
    old = "\t\t\t\t\t\t\tlisten_port: record[3],\n\t\t\t\t\t\t\tfwmark: record[4],"
    new = (
        "\t\t\t\t\t\t\tlisten_port: record[3],\n"
        + gen_luci_rpcd_awg_fields()
        + "\n\t\t\t\t\t\t\tfwmark: record[length(record) - 1],"
    )

    text = replace_literal_once(
        text,
        old,
        new,
        path=path,
        label="AWG interface dump fields",
    )
    write_text(path, text)


def gen_luci_status_awg_items() -> str:
    lines = []

    for opt in AWG_OPTS:
        if opt.name == "HeaderProtectionKey":
            value = (
                f"iface.{opt.snake} == '(hidden)' "
                "? E('em', _('configured')) : E('em', _('none'))"
            )
        else:
            value = f"iface.{opt.snake}"

        lines.append(f"\t\t\t_('{js_quote(opt.name)}'), {value},")

    return "\n".join(lines)


def fix_luci_status_interface_details(path: Path) -> None:
    text = read_text(path)

    old = (
        "\t\t\t_('Firewall Mark'), iface.fwmark != 'off' ? iface.fwmark : E('em', _('none'))\n"
        "\t\t]),\n"
        "\t\tE('div', { 'class': 'right' }, ["
    )
    new = (
        "\t\t\t_('Firewall Mark'), iface.fwmark != 'off' ? iface.fwmark : E('em', _('none')),\n"
        + gen_luci_status_awg_items()
        + "\n\t\t]),\n"
        "\t\tE('div', { 'class': 'right' }, ["
    )

    text = replace_literal_once(
        text,
        old,
        new,
        path=path,
        label="AWG interface status details",
    )
    write_text(path, text)


def gen_kmod_makefile() -> str:
    tab = "\t"
    continuation = "\\"
    lines = [
        "#",
        f"# {PROJECT_COPYRIGHT}",
        "#",
        "",
        "include $(TOPDIR)/rules.mk",
        "include $(INCLUDE_DIR)/kernel.mk",
        "",
        "PKG_NAME:=kmod-amneziawg",
        f"PKG_VERSION:={AWG_KERNEL_VERSION}",
        "PKG_RELEASE:=1",
        "",
        "PKG_SOURCE_PROTO:=git",
        "PKG_SOURCE_URL:=https://github.com/amnezia-vpn/amneziawg-linux-kernel-module.git",
        "PKG_SOURCE_VERSION:=v$(PKG_VERSION)",
        "",
        "PKG_LICENSE:=GPL-2.0",
        "PKG_LICENSE_FILES:=COPYING",
        "",
        "PKG_BUILD_PARALLEL:=1",
        "",
        "MAKE_PATH:=src",
        "",
        "include $(INCLUDE_DIR)/package.mk",
        "",
        "define KernelPackage/amneziawg",
        f"{tab}SECTION:=kernel",
        f"{tab}CATEGORY:=Kernel modules",
        f"{tab}SUBMENU:=Network Support",
        f"{tab}TITLE:=AmneziaWG VPN Kernel Module",
        f"{tab}MAINTAINER:={AWG_MAINTAINER}",
        f"{tab}FILES:=$(PKG_BUILD_DIR)/$(MAKE_PATH)/amneziawg.ko",
        f"{tab}DEPENDS:= {continuation}",
        f"{tab}{tab}+kmod-udptunnel4 {continuation}",
        f"{tab}{tab}+kmod-udptunnel6 {continuation}",
        f"{tab}{tab}+kmod-crypto-lib-chacha20poly1305 {continuation}",
        f"{tab}{tab}+kmod-crypto-lib-curve25519",
        "endef",
        "",
        "define KernelPackage/amneziawg/description",
        f"{tab}AmneziaWG VPN kernel module.",
        "endef",
        "",
        f"MAKE_OPTS:= {continuation}",
        f'{tab}M="$(PKG_BUILD_DIR)/$(MAKE_PATH)" {continuation}',
        f'{tab}WIREGUARD_VERSION="$(PKG_VERSION)"',
        "",
        "define Build/Compile",
        f"{tab}+$(KERNEL_MAKE) $(PKG_JOBS) {continuation}",
        f"{tab}{tab}$(MAKE_OPTS) {continuation}",
        f"{tab}{tab}modules",
        "endef",
        "",
        "$(eval $(call KernelPackage,amneziawg))",
    ]
    return "\n".join(lines) + "\n"


def update_kmod(*, stage: str) -> None:
    rm_rf(AWG_KMOD_DIR)

    if stage != "full":
        print(f"Removed {AWG_KMOD_DIR}: no vanilla WireGuard source package exists")
        return

    write_text(AWG_KMOD_MAKEFILE, gen_kmod_makefile())

    print("Generated:")
    print(f"  {AWG_KMOD_MAKEFILE} (PKG_VERSION={AWG_KERNEL_VERSION})")


def update_tools(*, stage: str) -> None:
    print("Fetching WireGuard tools package from OpenWrt:")
    print(f"  repo: {OPENWRT_REPO}")
    print(f"  ref:  {OPENWRT_REF}")
    print(f"  dir:  {OPENWRT_WG_TOOLS_DIR}")

    sparse_checkout(
        OPENWRT_SRC_DIR,
        OPENWRT_REPO,
        OPENWRT_REF,
        OPENWRT_WG_TOOLS_DIR,
    )

    rm_rf(AWG_TOOLS_DIR)

    shutil.copytree(
        OPENWRT_SRC_DIR / OPENWRT_WG_TOOLS_DIR,
        AWG_TOOLS_DIR,
    )

    rm_rf(OPENWRT_SRC_DIR)

    if stage == "vanilla":
        print("Updated vanilla WireGuard tree:")
        print(f"  {AWG_TOOLS_DIR}")
        return

    rename_path(
        AWG_FILES_DIR / "wireguard_watchdog",
        AWG_FILES_DIR / "amneziawg_watchdog",
    )

    rename_path(
        AWG_FILES_DIR / "wireguard.sh",
        AWG_TOOLS_PROTO_FILE,
    )

    if stage == "files":
        print("Updated file/path rename tree:")
        print(f"  {AWG_TOOLS_DIR}")
        return

    rewrite_text_tree(
        AWG_TOOLS_DIR,
        lambda text: rename_wg_to_awg_text(
            text,
            replace_wg0_conf=False,
        ),
        skip_path=is_svg,
    )

    if stage == "text":
        print("Updated textual rename tree:")
        print(f"  {AWG_TOOLS_DIR}")
        return

    update_tools_makefile(AWG_TOOLS_DIR / "Makefile")
    fix_tools_install_binary_name(AWG_TOOLS_DIR / "Makefile")

    insert_after_line(
        AWG_TOOLS_PROTO_FILE,
        r'proto_config_add_string "addresses"',
        gen_tools_proto_config_adds(),
    )

    insert_after_line(
        AWG_TOOLS_PROTO_FILE,
        r"local private_key listen_port mtu fwmark "
        r"addresses ip6prefix nohostroute tunlink",
        gen_tools_local_vars(),
    )

    insert_after_line(
        AWG_TOOLS_PROTO_FILE,
        r'config_get tunlink "\$\{config\}" "tunlink"',
        gen_tools_config_gets(),
    )

    insert_after_line(
        AWG_TOOLS_PROTO_FILE,
        r'FwMark=\$\{fwmark\}\\n"',
        gen_tools_awg_config_lines(),
    )

    add_copyright_after_existing(AWG_TOOLS_PROTO_FILE, prefix="#")

    print("Updated:")
    print(f"  {AWG_TOOLS_DIR}")


def update_luci(*, stage: str) -> None:
    print("Fetching LuCI WireGuard protocol package from:")
    print(f"  repo: {LUCI_REPO}")
    print(f"  ref:  {LUCI_REF}")
    print(f"  dir:  {LUCI_WG_PROTO_DIR}")

    sparse_checkout(
        LUCI_SRC_DIR,
        LUCI_REPO,
        LUCI_REF,
        LUCI_WG_PROTO_DIR,
    )

    rm_rf(AWG_LUCI_DIR)

    shutil.copytree(
        LUCI_SRC_DIR / LUCI_WG_PROTO_DIR,
        AWG_LUCI_DIR,
    )

    rm_rf(LUCI_SRC_DIR)

    if stage == "vanilla":
        print("Updated vanilla WireGuard tree:")
        print(f"  {AWG_LUCI_DIR}")
        return

    rename_path(
        AWG_LUCI_DIR / "htdocs/luci-static/resources/protocol/wireguard.js",
        AWG_LUCI_PROTO_FILE,
    )

    rename_path(
        AWG_LUCI_DIR / "htdocs/luci-static/resources/view/wireguard",
        AWG_LUCI_DIR / "htdocs/luci-static/resources/view/amneziawg",
    )

    rename_path(
        AWG_LUCI_DIR / "root/usr/share/luci/menu.d/luci-proto-wireguard.json",
        AWG_LUCI_DIR / "root/usr/share/luci/menu.d/luci-proto-amneziawg.json",
    )

    rename_path(
        AWG_LUCI_DIR / "root/usr/share/rpcd/ucode/luci.wireguard",
        AWG_LUCI_DIR / "root/usr/share/rpcd/ucode/luci.amneziawg",
    )

    rename_path(
        AWG_LUCI_DIR / "root/usr/share/rpcd/acl.d/luci-wireguard.json",
        AWG_LUCI_DIR / "root/usr/share/rpcd/acl.d/luci-amneziawg.json",
    )

    if stage == "files":
        print("Updated file/path rename tree:")
        print(f"  {AWG_LUCI_DIR}")
        return

    rewrite_text_tree(
        AWG_LUCI_DIR,
        lambda text: rename_wg_to_awg_text(
            text,
            replace_wg0_conf=True,
        ),
        skip_path=is_svg,
    )

    if stage == "text":
        print("Updated textual rename tree:")
        print(f"  {AWG_LUCI_DIR}")
        return

    icon_url = (
        f"{AWG_LUCI_ICON_REPO.rstrip('/')}/{AWG_LUCI_ICON_REF}/" f"{AWG_LUCI_ICON_PATH}"
    )
    download_file(icon_url, AWG_LUCI_ICON_FILE)

    update_luci_makefile(AWG_LUCI_DIR / "Makefile")
    fix_luci_persistent_keepalive(AWG_LUCI_PROTO_FILE)
    fix_luci_status_persistent_keepalive(AWG_LUCI_STATUS_FILE)
    fix_luci_status_interface_details(AWG_LUCI_STATUS_FILE)
    fix_luci_rpcd_dump(AWG_LUCI_RPCD_FILE)

    insert_after_line(
        AWG_LUCI_PROTO_FILE,
        r"o\.datatype = 'cidr6';",
        gen_luci_settings_tab(),
    )

    replace_call_block(
        AWG_LUCI_PROTO_FILE,
        r"s\.tab\('peers'",
        gen_luci_peers_tab(),
    )

    insert_after_line(
        AWG_LUCI_PROTO_FILE,
        r"s\.getOption\('addresses'\)\.getUIElement\(s\.section\)",
        gen_luci_import_setters(),
    )

    insert_after_line(
        AWG_LUCI_PROTO_FILE,
        r"s\.formvalue\(s\.section, 'listen_port'\) \|\| '51820';",
        gen_luci_export_vars(),
    )

    insert_after_line(
        AWG_LUCI_PROTO_FILE,
        r"dns && dns\.length .*'DNS = '.*'# DNS not defined',",
        gen_luci_export_lines(),
    )

    make_qr_generation_defensive(AWG_LUCI_PROTO_FILE)

    add_modifications_copyright(AWG_LUCI_PROTO_FILE, prefix="//")
    add_modifications_copyright(AWG_LUCI_STATUS_FILE, prefix="//")
    add_copyright_after_existing(AWG_LUCI_RPCD_FILE, prefix="//")

    print("Updated:")
    print(f"  {AWG_LUCI_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate AmneziaWG OpenWrt packages from upstream sources."
    )

    parser.add_argument(
        "target",
        nargs="?",
        choices=("tools", "luci", "kmod", "all", "check"),
        default="all",
        help="what to generate",
    )

    stages = parser.add_mutually_exclusive_group()
    stages.add_argument(
        "--stage",
        choices=("vanilla", "files", "text", "full"),
        help=(
            "generation stage: vanilla upstream, file/path renames, textual "
            "wg->awg renames, or full AmneziaWG overlay"
        ),
    )
    stages.add_argument(
        "--vanilla-only",
        dest="stage",
        action="store_const",
        const="vanilla",
        help="copy vanilla upstream WireGuard packages without renames",
    )
    stages.add_argument(
        "--rename-files-only",
        "--rename-only",
        dest="stage",
        action="store_const",
        const="files",
        help="copy upstream packages and rename paths/files only",
    )
    stages.add_argument(
        "--rename-text-only",
        dest="stage",
        action="store_const",
        const="text",
        help="also rename WireGuard/wg identifiers in file contents",
    )

    parser.set_defaults(stage="full")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.target == "check" or args.stage == "full":
        check_awg_version()

    if args.target == "check":
        return

    if args.target in ("tools", "all"):
        update_tools(stage=args.stage)

    if args.target in ("luci", "all"):
        update_luci(stage=args.stage)

    if args.target in ("kmod", "all"):
        update_kmod(stage=args.stage)


if __name__ == "__main__":
    main()
