import random
def main(command, current_directory):
    result = random.randint(1, 8)
    if result == 1:
        print("Yes.")
    elif result == 2:
        print("No.")
    elif result == 3:
        print("Very likely.")
    elif result == 4:
        print("Ask again later.")
    elif result == 5:
        print("Not very likely.")
    elif result == 6:
        print("Definetely.")
    elif result == 7:
        print("Cannot predict now.")
    elif result == 8:
        print("Don't count on it.")
