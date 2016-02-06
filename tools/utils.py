from uuid import uuid4

FILENAME_SIZE = 32


# create a length-32 string of random uppercase letters and numbers
def generate_filename():
    return str(uuid4()).replace('-', '').upper()
