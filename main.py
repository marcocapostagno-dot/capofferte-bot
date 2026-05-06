import os
import sys
import site
import json
import pkgutil
import importlib
import subprocess


def line(title: str):
    print("\n" + "=" * 20 + f" {title} " + "=" * 20)


line("PYTHON")
print("executable:", sys.executable)
print("version:", sys.version)
print("cwd:", os.getcwd())

line("SITE PACKAGES")
try:
    print("site.getsitepackages():", site.getsitepackages())
except Exception as exc:
    print("site.getsitepackages() error:", repr(exc))
try:
    print("site.getusersitepackages():", site.getusersitepackages())
except Exception as exc:
    print("site.getusersitepackages() error:", repr(exc))
print("sys.path:")
for p in sys.path:
    print(" -", p)

line("PIP LIST")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    print("returncode:", result.returncode)
    if result.stdout:
        packages = json.loads(result.stdout)
        interesting = [
            p for p in packages
            if any(k in p["name"].lower() for k in ["amazon", "creator", "paapi"])
        ]
        print("interesting packages:")
        for p in interesting:
            print(" -", p["name"], p["version"])
    else:
        print("stdout empty")
    if result.stderr:
        print("stderr:", result.stderr[:4000])
except Exception as exc:
    print("pip list error:", repr(exc))

line("PKGUTIL MODULES")
mods = sorted({m.name for m in pkgutil.iter_modules() if any(k in m.name.lower() for k in ["amazon", "creator", "paapi"])})
for name in mods:
    print(" -", name)
if not mods:
    print("No matching modules found")

line("IMPORT TESTS")
candidates = [
    "creators_api",
    "amazon_creatorsapi_python_sdk",
    "amazon_creatorsapi",
    "amazon_creators_api",
    "creator_api",
    "creators",
]
for name in candidates:
    try:
        mod = importlib.import_module(name)
        print(f"OK import {name}:", getattr(mod, "__file__", "built-in"))
    except Exception as exc:
        print(f"FAIL import {name}: {exc!r}")

line("DONE")
