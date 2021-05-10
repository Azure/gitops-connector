import os

def getenv(key, default=None):
    env_value = os.getenv(key, default)

    if not env_value:
        raise IndentationError(f'The env variable {key} is not initialized')
    
    return env_value


