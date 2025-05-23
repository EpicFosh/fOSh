# main.py

import os
from core import dispatch, version, codename

def get_prompt(cwd):
    ROOT = os.path.dirname(os.path.realpath(__file__))
    if cwd == ROOT:
        return "~"
    return os.path.join("~", os.path.relpath(cwd, ROOT))

def shell():
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    cwd = ROOT_DIR

    print(f'FuadeOS™ "{codename}" ({version})')
    print("Copyright© 2025, FusionCore Corporation™. All rights reserved.")
    print('Type "help" for a list of commands.')

    while True:
        try:
            cmd = input(f"{get_prompt(cwd)} $ ").strip()
            if not cmd:
                continue

            dispatch(cmd, cwd)
            # capture directory changes from `cd`
            from core import last_cwd
            if last_cwd:
                cwd = last_cwd

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting shell.")
            break

if __name__ == "__main__":
    shell()
    
