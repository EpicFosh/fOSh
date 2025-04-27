import os
import sys
import shutil
import urllib.request
import importlib.util
import fnmatch

# Global variable for the root directory where this Python file is located.
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def resolve_path(path_str, current_directory):
    # Accept absolute-like '/file' paths relative to ROOT_DIR
    if path_str.startswith('/'):
        return os.path.join(ROOT_DIR, path_str.lstrip('/'))
    return os.path.join(current_directory, path_str)


def help():
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
  rm <target>                   - Remove a file or directory (protects main.py & commands.py).
  find <pattern>                - Recursively search for files/directories matching a pattern.
  apt update                    - Update the system from a remote source.
  apt install <package-name>    - Download and install a Python package into root directory.
  apt uninstall <package-name>  - Uninstall (delete) a previously installed package.
  neofetch                      - Display system information.
"""
    print(help_msg)


def exit_shell(command):
    print("Exiting the shell...")
    sys.exit(0)


def cd(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: cd <directory>")
        return current_directory
    new_dir = parts[1].strip()
    if new_dir == "/":
        return ROOT_DIR
    new_path = resolve_path(new_dir, current_directory)
    if os.path.isdir(new_path) and os.path.commonpath([new_path, ROOT_DIR]) == ROOT_DIR:
        return new_path
    print(f"Directory '{new_dir}' not found or access denied.")
    return current_directory


def ls(command, current_directory):
    for item in os.listdir(current_directory):
        print(item)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def cat(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: cat <file>")
        return
    filename = parts[1].strip()
    file_path = resolve_path(filename, current_directory)
    try:
        with open(file_path, 'r') as file:
            print(file.read())
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
    new_path = resolve_path(dir_name, current_directory)
    try:
        os.mkdir(new_path)
        print(f"Directory '{dir_name}' created.")
    except FileExistsError:
        print(f"Directory '{dir_name}' already exists.")
    except Exception as e:
        print(f"Error: {e}")

def rm(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: rm <target>")
        return
    target = parts[1].strip()

    # Protect core files and root
    if target in ('main.py', 'commands.py', '/main.py', '/commands.py') or target == '/':
        print(f"Error: Cannot remove core file or root '{target}'.")
        return

    target_path = resolve_path(target, current_directory)

    # Block any attempt to delete ROOT_DIR itself
    if os.path.abspath(target_path) == os.path.abspath(ROOT_DIR):
        print(f"Error: Cannot remove root directory '{target}'.")
        return

    if not os.path.exists(target_path):
        print(f"'{target}' not found.")
        return

    if os.path.isdir(target_path):
        try:
            shutil.rmtree(target_path)
            print(f"Directory '{target}' deleted.")
        except Exception as e:
            print(f"Error deleting directory '{target}': {e}")
    else:
        try:
            os.remove(target_path)
            print(f"File '{target}' deleted.")
        except Exception as e:
            print(f"Error deleting file '{target}': {e}")

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
                # print path relative to cwd, prefix with './' when appropriate
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, current_directory)
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
    file_path = resolve_path(filename, current_directory)
    content_lines = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
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
        blank = max(rows - len(content_lines) - 3, 0)
        for _ in range(blank): print()
        dis = " Press Ctrl+X to exit (and use ':del <line_number>' to delete a line) "
        print("\033[43m" + dis.center(cols) + "\033[0m")

    while True:
        print_screen()
        inp = input("nano> ")
        if inp.lower() in ('\x18', 'ctrl+x'):
            break
        if inp.startswith(':del '):
            parts_del = inp.split(maxsplit=1)
            if len(parts_del) == 2 and parts_del[1].isdigit():
                idx = int(parts_del[1]) - 1
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
            with open(file_path, 'w') as f:
                for line in content_lines:
                    f.write(line + "\n")
            print(f"File '{filename}' saved.")
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("Changes discarded.")
    clear()


def neofetch():
    lime, white, reset = "\033[38;5;155m", "\033[97m", "\033[0m"
    print(f"{lime}root{white}@{lime}root{reset}")
    print(f"{white}{'-'*46}{reset}")
    print(f"{lime}   _-@@@@@@@@-_     OS:{white} FuadeOS 1.0.0{reset} (Cherry)")
    print(f"{lime}  +@@@{white}██████{lime}@@@+    Kernel Version:{white} 3.13.2{reset}")
    print(f"{lime} *@@@@{white}██{lime}@@@@@@@@*   System Commands:{white} 14{reset}")
    print(f"{lime} *@@@@{white}██████{lime}@@@@*   Host:{white} root{reset}")
    print(f"{lime} *@@@@{white}██{lime}@@@@@@@@*   Shell:{white} Python CLI{reset}")
    print(f"{lime}  +@@@{white}██{lime}@@@@@@@+    Version:{white} 1.0.0{reset}")
    print(f"{lime}   *-@@@@@@@@-*     Terminal:{white} python3-terminal{reset}")


def apt_install(command):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: apt install <package-name>")
        return
    pkg = parts[2].strip()
    if pkg in ('main', 'commands'):
        print(f"Error: Cannot install package.")
        return
    url = f"https://raw.githubusercontent.com/FusionCore-Corp/FuadeOS/refs/heads/main/{pkg}.py"
    print(f"Installing/Updating '{pkg}' from {url}...")
    try:
        data = urllib.request.urlopen(url).read().decode('utf-8')
        pkg_path = os.path.join(ROOT_DIR, f"{pkg}.py")
        with open(pkg_path, 'w') as f:
            f.write(data)
        print(f"Package '{pkg}' installed.")
    except Exception as e:
        print(f"Error installing '{pkg}': {e}")


def apt_uninstall(command):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("Usage: apt uninstall <package-name>")
        return
    pkg = parts[2].strip()
    if pkg in ('main', 'commands'):
        print(f"Error: Cannot uninstall package.")
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


def exec_custom(command, current_directory):
    """
    Attempt to load and execute a custom package command.
    Modules must live in ROOT_DIR and define a run(cmd, cwd) function.
    """
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
        # Call the module's run() entry point
        if hasattr(mod, 'run'):
            mod.run(command, current_directory)
        else:
            print(f"Module '{module_name}' has no run() function.")
    except Exception as e:
        print(f"Error running '{module_name}': {e}")
        
# Troubleshooting
def run(command, current_directory):
    print("Cannot run command.")
    
# Version info
version = "1.0.0"
codename = "Cherry"
