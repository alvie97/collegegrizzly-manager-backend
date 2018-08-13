from uuid import uuid4


def generate_public_id():
  return str(uuid4()).replace('-', '')