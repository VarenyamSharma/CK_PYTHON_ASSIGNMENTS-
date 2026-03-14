import random
import string

def generate_password():
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digits = random.sample(string.digits, 2)
    special = random.choice("!@#$%&*")

    # Remaining characters
    remaining_length = 16 - 5

    all_chars = string.ascii_letters + string.digits + "!@#$%&*"
    remaining = random.sample(all_chars, remaining_length)

    password_list = [upper, lower] + digits + [special] + remaining

    # Remove duplicates if any
    password_list = list(set(password_list))

    while len(password_list) < 16:
        ch = random.choice(all_chars)
        if ch not in password_list:
            password_list.append(ch)

    random.shuffle(password_list)

    password = "".join(password_list)

    return password


print("Generated Password:", generate_password())