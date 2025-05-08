import os
import sys
import importlib
import commands

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_prompt(current_directory):
    if current_directory == ROOT_DIR:
        return "~"
    else:
        rel_path = os.path.relpath(current_directory, ROOT_DIR)
        return os.path.join("~", rel_path)

def shell():
    current_directory = ROOT_DIR
    while True:
        command = input(f"{get_prompt(current_directory)} $ ").strip()
        if not command:
            continue

        if command.lower() == "exit":
            commands.exit_shell(command)
        elif command == "help":
            commands.help()
        elif command.startswith("cd"):
            current_directory = commands.cd(command, current_directory)
        elif command == "ls":
            commands.ls(command, current_directory)
        elif command == "clear":
            commands.clear()
        elif command.startswith("cat"):
            commands.cat(command, current_directory)
        elif command.startswith("mkdir"):
            commands.mkdir(command, current_directory)
        elif command.startswith("nano"):
            commands.nano(command, current_directory)
        elif command.startswith("rm"):
            commands.rm(command, current_directory)
        elif command.startswith("find"):
            commands.find(command, current_directory)
        elif command.startswith("wget"):
            commands.wget(command, current_directory)
        elif command.startswith("cp"):
            commands.cp(command, current_directory)
        elif command.startswith("mv"):
            commands.mv(command, current_directory)

        elif command == "apt update":
            commands.apt_update()
            importlib.reload(commands)
        elif command.startswith("apt install"):
            commands.apt_install(command)
        elif command.startswith("apt uninstall"):
            commands.apt_uninstall(command)

        elif command == "neofetch":
            commands.neofetch()
        else:
            commands.exec_custom(command, current_directory)

if __name__ == "__main__":
    print(f'FuadeOS™ "{commands.codename}" ({commands.version})')
    print("Copyright© 2025, FusionCore Corporation™. All rights reserved.")
    print('Type "help" for a list of commands.')
    shell()
