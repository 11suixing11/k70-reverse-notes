"""Read one explicitly selected K70 through ADB without changing its settings."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default="adb", help="Path to platform-tools/adb")
    parser.add_argument("--serial", required=True, help="Explicit target device serial")
    parser.add_argument("--include-root", action="store_true", help="Read optional Root state")
    parser.add_argument("--output", type=Path, help="Save JSON locally; includes device serial")
    args = parser.parse_args()

    def adb(*command: str) -> str:
        result = subprocess.run(
            [args.adb, "-s", args.serial, *command],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "ADB failed")
        return result.stdout.strip()

    def prop(name: str) -> str:
        return adb("shell", "getprop", name)

    def setting(namespace: str, name: str) -> str:
        return adb("shell", "settings", "get", namespace, name)

    def rooted(command: str) -> str:
        return adb("shell", "su", "-c", shlex.quote(command))

    try:
        if adb("get-state") != "device":
            raise RuntimeError("Selected device is not ready or authorized")
        product = prop("ro.product.device")
        if product != "vermeer":
            raise RuntimeError(f"Expected vermeer; got {product!r}. Stopped without changes.")
        home = adb(
            "shell", "cmd", "package", "resolve-activity", "--brief",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME",
        )
        report = {
            "recorded_at": dt.datetime.now().astimezone().isoformat(),
            "serial": args.serial,
            "device": product,
            "model": prop("ro.product.model"),
            "lineage": prop("ro.lineage.version"),
            "android": prop("ro.build.version.release"),
            "sdk": prop("ro.build.version.sdk"),
            "abi_list": prop("ro.product.cpu.abilist"),
            "slot": prop("ro.boot.slot_suffix"),
            "kernel": adb("shell", "uname", "-r"),
            "selinux": adb("shell", "getenforce"),
            "encryption": prop("ro.crypto.state"),
            "home": home.splitlines()[-1] if home else "",
            "settings": {
                "auto_brightness": setting("system", "screen_brightness_mode"),
                "screen_off_timeout_ms": setting("system", "screen_off_timeout"),
                "stay_on_while_plugged_in": setting("global", "stay_on_while_plugged_in"),
                "animation_scale": {
                    key: setting("global", key)
                    for key in ("window_animation_scale", "transition_animation_scale",
                                "animator_duration_scale")
                },
            },
            "read_only": True,
        }
        if args.include_root:
            report["root"] = {
                "identity": rooted("id"),
                "magisk": rooted("magisk -v"),
                "kali_entry_present": rooted(
                    "if [ -x /data/local/k70-ctf/bin/kali ]; "
                    "then echo true; else echo false; fi"
                ) == "true",
                "ctf_directory_present": rooted(
                    "if [ -d /sdcard/CTF ]; then echo true; else echo false; fi"
                ) == "true",
            }
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(encoded, end="")
        return 0
    except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
        print(f"Inspection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
