import os
import sys
import shutil
import urllib.request
import importlib.util
import fnmatch

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

# Version info

def version_info():
    return "1.1", "Blueberry"

version, codename = version_info()

# Ensure stdout uses utf-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


def resolve_path(path_str, current_directory):
    # Normalize and resolve absolute path safely
    if os.path.isabs(path_str):
        new_path = os.path.normpath(os.path.join(ROOT_DIR, path_str.lstrip('/')))
    else:
        new_path = os.path.normpath(os.path.join(current_directory, path_str))
    # Prevent escaping root
    if os.path.commonpath([new_path, ROOT_DIR]) != ROOT_DIR:
        raise PermissionError("Access denied: outside of root directory.")
    return new_path


def help(command=None, current_directory=None):
    help_msg = """
Available Commands:
  help                          - Display this help message.
  exit                          - Exit the shell.
  cd <directory>                - Change directory (use 'cd ..' to go up; 'cd /' for root).
  ls                            - List files and directories in the current directory.
  clear                         - Clear the terminal screen.
  cat <file>                    - Display the contents of a file.
  mkdir <directory>             - Create a new directory.
  nano <file>                   - Open the nano-like text editor for a file.
  rm <target>                   - Remove a file or directory.
  cp <source> <destination>     - Copy a file to a new location.
   mv <source> <destination>    - Move or rename a file.
   wget <url> [filename]        - Download a file from the given URL.
  find <pattern>                - Recursively search for files/directories matching a pattern.
  apt update                    - Update the system from remote source.
  apt install <package-name>    - Download and install a Python package into root directory.
  apt uninstall <package-name>  - Uninstall a previously installed package.
  neofetch                      - Display system information.
"""
    print(help_msg)


def exit_shell(command=None, current_directory=None):
    print("Exiting the shell...")
    sys.exit(0)


def cd(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: cd <directory>")
        return current_directory
    target = parts[1].strip()

    # Handle root
    if target == "/":
        return ROOT_DIR

    # Handle parent directory
    if target == "..":
        # If already at root, cannot go up
        if os.path.abspath(current_directory) == ROOT_DIR:
            print("Already at root directory.")
            return current_directory
        return os.path.dirname(current_directory)

    # Resolve path normally
    try:
        new_path = resolve_path(target, current_directory)
    except PermissionError as pe:
        print(pe)
        return current_directory

    if os.path.isdir(new_path):
        return new_path
    print(f"Directory '{target}' not found.")
    return current_directory


def ls(command, current_directory):
    try:
        for item in os.listdir(current_directory):
            print(item)
    except Exception as e:
        print(f"Error listing directory: {e}")


def clear(command=None, current_directory=None):
    os.system('cls' if os.name == 'nt' else 'clear')


def cat(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: cat <file>")
        return
    filename = parts[1].strip()
    try:
        file_path = resolve_path(filename, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    # Check if directory
    if os.path.isdir(file_path):
        print(f"Error: '{filename}' is a directory.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def mkdir(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: mkdir <directory>")
        return
    dir_name = parts[1].strip()
    try:
        new_path = resolve_path(dir_name, current_directory)
        os.mkdir(new_path)
        print(f"Directory '{dir_name}' created.")
    except FileExistsError:
        print(f"Directory '{dir_name}' already exists.")
    except PermissionError as pe:
        print(pe)
    except Exception as e:
        print(f"Error: {e}")


def rm(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: rm <target>")
        return
    target = parts[1].strip()

    # Protect core and root
    protected = {'main.py', 'commands.py'}
    if target in ('/',) or target in protected:
        print(f"Error: Cannot remove protected target '{target}'.")
        return

    try:
        target_path = resolve_path(target, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    # Double-check root
    if os.path.abspath(target_path) == ROOT_DIR:
        print(f"Error: Cannot remove root directory '{target}'.")
        return

    if not os.path.exists(target_path):
        print(f"'{target}' not found.")
        return

    try:
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
            print(f"Directory '{target}' deleted.")
        else:
            os.remove(target_path)
            print(f"File '{target}' deleted.")
    except Exception as e:
        print(f"Error deleting '{target}': {e}")


def find(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: find <pattern>")
        return
    pattern = parts[1].strip()
    matches = []
    for dirpath, dirnames, filenames in os.walk(current_directory):
        for name in dirnames + filenames:
            if fnmatch.fnmatch(name, pattern):
                rel = os.path.relpath(os.path.join(dirpath, name), current_directory)
                matches.append(rel)
    if matches:
        for m in matches:
            print("/" + m)
    else:
        print(f"No matches for '{pattern}'")


def nano(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: nano <file>")
        return
    filename = parts[1].strip()
    try:
        file_path = resolve_path(filename, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    # Prevent editing directories
    if os.path.isdir(file_path):
        print(f"Error: '{filename}' is a directory.")
        return

    content_lines = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_lines = [line.rstrip('\n') for line in f]
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        ans = input(f"File '{filename}' not found. Create? (Y/n): ").strip().lower()
        if ans == 'n':
            print("File not created.")
            return

    def print_screen():
        clear()
        size = os.get_terminal_size()
        rows, cols = size.lines, size.columns
        for i, line in enumerate(content_lines):
            print(f"{i+1:3}: {line}")
        for _ in range(max(rows - len(content_lines) - 3, 0)):
            print()
        dis = " Press Ctrl+X to exit (and use ':del <line_number>' to delete a line) "
        print("\033[43m" + dis.center(cols) + "\033[0m")

    while True:
        print_screen()
        inp = input("nano> ")
        if inp.lower() in ('\x18', 'ctrl+x'):
            break
        if inp.startswith(':del '):
            _, num = inp.split(maxsplit=1)
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(content_lines):
                    content_lines.pop(idx)
                else:
                    print("Invalid line number.")
            else:
                print("Usage: :del <line_number>")
            continue
        content_lines.append(inp)

    save = input("Save changes? (Y/n): ").strip().lower()
    if save != 'n':
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in content_lines:
                    f.write(line + '\n')
            print(f"File '{filename}' saved.")
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("Changes discarded.")
    clear()


def neofetch(command=None, current_directory=None):
    lime, white, reset = "\033[38;5;155m", "\033[97m", "\033[0m"
    print(f"{lime}root{white}@{lime}root{reset}")
    print(f"{white}{'-'*46}{reset}")
    print(f"{lime}   _-@@@@@@@@-_     OS:{white} FuadeOS {version}{reset} ({codename})")
    print(f"{lime}  +@@@{white}██████{lime}@@@+    Kernel Version:{white} 3.13.2{reset}")
    print(f"{lime} *@@@@{white}██{lime}@@@@@@@@*   System Commands:{white} 14{reset}")
    print(f"{lime} *@@@@{white}██████{lime}@@@@*   Host:{white} root{reset}")
    print(f"{lime} *@@@@{white}██{lime}@@@@@@@@*   Shell:{white} Python CLI{reset}")
    print(f"{lime}  +@@@{white}██{lime}@@@@@@@+    Version:{white} {version}{reset}")
    print(f"{lime}   *-@@@@@@@@-*     Terminal:{white} python3-terminal{reset}")

# Package management and execution

def apt_install(command, current_directory=None):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: apt install <package-name>")
        return
    pkg = parts[2].strip()
    if pkg in ('main', 'commands'):
        print("Error: Cannot install package.")
        return
    url = f"https://raw.githubusercontent.com/FusionCore-Corp/FuadeOS/refs/heads/main/{pkg}.py"
    print(f"Installing '{pkg}' from {url}...")
    try:
        data = urllib.request.urlopen(url).read().decode('utf-8')
        pkg_path = os.path.join(ROOT_DIR, f"{pkg}.py")
        with open(pkg_path, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"Package '{pkg}' installed.")
    except Exception as e:
        print(f"Error installing '{pkg}': {e}")


def apt_uninstall(command, current_directory=None):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: apt uninstall <package-name>")
        return
    pkg = parts[2].strip()
    if pkg in ('main', 'commands'):
        print("Error: Cannot uninstall package.")
        return
    pkg_path = os.path.join(ROOT_DIR, f"{pkg}.py")
    if not os.path.exists(pkg_path):
        print(f"Package '{pkg}' is not installed.")
        return
    try:
        os.remove(pkg_path)
        print(f"Package '{pkg}' uninstalled.")
    except Exception as e:
        print(f"Error uninstalling '{pkg}': {e}")


def apt_update(command=None, current_directory=None):
    base_url = "https://raw.githubusercontent.com/FusionCore-Corp/FuadeOS/refs/heads/main/updates/"
    files = ["commands.py", "main.py"]
    for fname in files:
        url = base_url + fname
        print(f"Updating '{fname}' from {url}...")
        tmp_path = os.path.join(ROOT_DIR, fname + ".tmp")
        try:
            resp = urllib.request.urlopen(url)
            data = resp.read()
            with open(tmp_path, 'wb') as tf:
                tf.write(data)
            os.replace(tmp_path, os.path.join(ROOT_DIR, fname))
            print(f"'{fname}' updated successfully.")
        except Exception as e:
            print(f"Failed to update '{fname}': {e}")
            try:
                os.remove(tmp_path)
            except:
                pass


def exec_custom(command, current_directory):
    parts = command.split(maxsplit=1)
    module_name = parts[0]
    module_file = os.path.join(ROOT_DIR, f"{module_name}.py")
    if not os.path.isfile(module_file):
        print(f"Command '{command}' not recognized.")
        return
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'run'):
            mod.run(command, current_directory)
        else:
            print(f"Module '{module_name}' has no run() function.")
    except Exception as e:
        print(f"Error running '{module_name}': {e}")

def wget(command, current_directory):
    parts = command.split(maxsplit=2)
    if len(parts) < 2:
        print("Usage: wget <url> [filename]")
        return
    url = parts[1].strip()
    # Determine filename
    if len(parts) == 3:
        filename = parts[2].strip()
    else:
        filename = os.path.basename(urllib.request.urlparse(url).path) or "index.html"
    try:
        file_path = resolve_path(filename, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    try:
        # Download to a temp file first
        tmp = file_path + ".tmp"
        with urllib.request.urlopen(url) as resp, open(tmp, 'wb') as out:
            out.write(resp.read())
        os.replace(tmp, file_path)
        print(f"Downloaded '{url}' to '{filename}'.")
    except urllib.error.HTTPError as he:
        print(f"HTTP error: {he.code} {he.reason}")
    except urllib.error.URLError as ue:
        print(f"URL error: {ue.reason}")
    except Exception as e:
        print(f"Error downloading '{url}': {e}")

def cp(command, current_directory):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: cp <source> <destination>")
        return
    src = parts[1].strip()
    dst = parts[2].strip()
    try:
        src_path = resolve_path(src, current_directory)
        dst_path = resolve_path(dst, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    if not os.path.exists(src_path):
        print(f"Source '{src}' not found.")
        return
    if os.path.isdir(src_path):
        print(f"Error: '{src}' is a directory. Use recursive copy if desired.")
        return

    # If destination is a directory, copy into it
    if os.path.isdir(dst_path):
        dst_path = os.path.join(dst_path, os.path.basename(src_path))

    try:
        shutil.copy2(src_path, dst_path)
        print(f"Copied '{src}' to '{dst}'.")
    except Exception as e:
        print(f"Error copying '{src}' to '{dst}': {e}")

def mv(command, current_directory):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: mv <source> <destination>")
        return
    src = parts[1].strip()
    dst = parts[2].strip()
    try:
        src_path = resolve_path(src, current_directory)
        dst_path = resolve_path(dst, current_directory)
    except PermissionError as pe:
        print(pe)
        return

    if not os.path.exists(src_path):
        print(f"Source '{src}' not found.")
        return

    # If destination is a directory, move into it
    if os.path.isdir(dst_path):
        dst_path = os.path.join(dst_path, os.path.basename(src_path))

    try:
        shutil.move(src_path, dst_path)
        print(f"Moved '{src}' to '{dst}'.")
    except Exception as e:
        print(f"Error moving '{src}' to '{dst}': {e}")

def run(command, current_directory):
    print("Command not recognized. Type 'help' for list of commands.")
