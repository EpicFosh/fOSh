# greet.py

def main(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: greet <name>")
        return
    name = parts[1].strip()
    print(f"Hey {name}, what's up?")
