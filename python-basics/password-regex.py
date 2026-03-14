import random
import string
import re

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%&*"

    while True:
        password = ''.join(random.sample(chars, 16))

        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=(.*\d){2,})(?=.*[!@#$%&*]).{16}$'

        if re.match(pattern, password):
            return password


print("Generated Password:", generate_password())