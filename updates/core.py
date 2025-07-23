# core.py

import os
import sys
import importlib.util
import urllib.request
import fnmatch
import shutil

# ─── version info ──────────────────────────────────────────────────────────────
def version_info():
    return "1.0", "Potato (Based off of FuadeOS 1.1)"
version, codename = version_info()

# ─── paths & utils ─────────────────────────────────────────────────────────────
ROOT_DIR      = os.path.dirname(os.path.realpath(__file__))
CMD_DIR       = os.path.join(ROOT_DIR, "commands")
PACKAGES_DIR  = os.path.join(ROOT_DIR, "packages")

def resolve_path(path_str, current_directory):
    if os.path.isabs(path_str):
        new_path = os.path.normpath(os.path.join(ROOT_DIR, path_str.lstrip('/')))
    else:
        new_path = os.path.normpath(os.path.join(current_directory, path_str))
    if os.path.commonpath([new_path, ROOT_DIR]) != ROOT_DIR:
        raise PermissionError("Access denied: outside of root directory.")
    return new_path

# ─── built-in commands ─────────────────────────────────────────────────────────
def help(command=None, current_directory=None):
    print(f"""
Available Commands:
  help                          - Display this help message.
  exit                          - Exit the shell.
  version                       - Show version.
  cd <directory>                - Change directory.
  ls                            - List directory.
  clear                         - Clear screen.
  cat <file>                    - Show file contents.
  mkdir <directory>             - Make directory.
  nano <file>                   - Edit file.
  rm <target>                   - Remove file/dir.
  cp <src> <dst>                - Copy file.
  mv <src> <dst>                - Move/rename file.
  wget <url> [filename]         - Download URL.
  find <pattern>                - Search tree.
  apt update                    - Update core.
  apt install <pkg>             - Install pkg into packages/.
  apt uninstall <pkg>           - Uninstall pkg from packages/.
  neofetch                      - Show system info.
""")

def exit_shell(command=None, current_directory=None):
    print("Exiting the shell...")
    sys.exit(0)

def exec_custom(command, current_directory):
    parts = command.split(maxsplit=1)
    module_name = parts[0]
    module_file = os.path.join(ROOT_DIR, f"{module_name}.py")
    if not os.path.isfile(module_file):
        print(f"Command '{command}' not recognized.")
        return
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, 'run'):
        mod.run(command, current_directory)
    else:
        print(f"Module '{module_name}' has no run() function.")

def run(command=None, current_directory=None):
    print("Command not recognized. Type 'help' for list of commands.")

# ─── dispatcher ────────────────────────────────────────────────────────────────
last_cwd = None

def dispatch(command, current_directory):
    """
    Parse `command`, route to built-in, apt_*, commands/<cmd>.py,
    packages/<cmd>.py, or external .py, updating last_cwd for cd.
    """
    global last_cwd
    last_cwd = None
    c     = command.strip()
    lower = c.lower()

    # built-ins
    if lower == 'help':
        help(); return
    if lower in ('exit', 'quit'):
        exit_shell(); return
    if lower == 'version':
        print(f"Version: {version} ({codename})"); return

    # apt_*
    if lower.startswith('apt '):
        parts    = lower.split(maxsplit=2)
        if len(parts) >= 2:
            apt_mod  = f"apt_{parts[1]}"
            apt_path = os.path.join(CMD_DIR, f"{apt_mod}.py")
            if os.path.isfile(apt_path):
                _load_and_run(apt_path, apt_mod, command, current_directory)
                return

    # system commands in commands/ folder
    key       = c.split()[0]
    cmd_path  = os.path.join(CMD_DIR, f"{key}.py")
    if os.path.isfile(cmd_path):
        _load_and_run(cmd_path, key, command, current_directory)
        return

    # packages commands in packages/ folder
    pkg_path = os.path.join(PACKAGES_DIR, f"{key}.py")
    if os.path.isfile(pkg_path):
        _load_and_run(pkg_path, key, command, current_directory, namespace="packages")
        return

    # fallback to external .py
    exec_custom(command, current_directory)

def _load_and_run(path, module_name, command, cwd, namespace="commands"):
    """
    Dynamically load module from given path under
    <namespace>.<module_name>, execute its main(), and capture cd.
    """
    global last_cwd
    full_name = f"{namespace}.{module_name}"
    spec      = importlib.util.spec_from_file_location(full_name, path)
    mod       = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    result = mod.main(command, cwd)
    if module_name == 'cd' and isinstance(result, str):
        last_cwd = result
        
