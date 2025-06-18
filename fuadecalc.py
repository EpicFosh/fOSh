# cli_calculator.py

def add(x, y):
    """Adds two numbers."""
    return x + y

def subtract(x, y):
    """Subtracts two numbers."""
    return x - y

def multiply(x, y):
    """Multiplies two numbers."""
    return x * y

def divide(x, y):
    """Divides two numbers. Handles division by zero."""
    if y == 0:
        return "Error: Cannot divide by zero!"
    return x / y

def main(command, cwd):
    """
    Main function to run the CLI calculator.
    Accepts 'command' and 'cwd' for compatibility with external execution environments,
    though they are not used by this simple calculator logic.
    """
    print("Calculator")
    print("Operations available: +, -, *, /")
    print("Enter 'exit' to quit.")

    while True:
        try:
            # Get the first number from the user
            num1_input = input("Enter first number (or 'exit'): ")
            if num1_input.lower() == 'exit':
                break
            num1 = float(num1_input)

            # Get the operation from the user
            operator = input("Enter operation (+, -, *, /): ")
            if operator.lower() == 'exit':
                break
            if operator not in ['+', '-', '*', '/']:
                print("Invalid operator. Please use +, -, *, or /.")
                continue

            # Get the second number from the user
            num2_input = input("Enter second number (or 'exit'): ")
            if num2_input.lower() == 'exit':
                break
            num2 = float(num2_input)

            result = None
            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)

            print(f"Result: {result}")

        except ValueError:
            print("Invalid input. Please enter numbers for calculations.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("Thank you for using the calculator. Goodbye!")

if __name__ == "__main__":
    # When run directly, main() is called without arguments.
    # When integrated into another system (like FuadeOS), it might receive arguments.
    # We call it with dummy arguments here to allow direct execution.
    main(None, None) # Pass None for command and cwd when run directly
