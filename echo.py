# echo.py

def run(command, current_directory):
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: echo <text>")
        return
    text = parts[1].strip()
    print(f"{text}")
