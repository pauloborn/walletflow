import random
import string


def random_string(size: int):
    source = string.ascii_letters + string.digits
    return ''.join((random.choice(source) for i in range(size)))
