import os

filename = os.path.dirname(os.path.realpath(__file__)) + '/.env'

if os.path.isfile(filename):
    with open(filename) as fp:
        for cnt, line in enumerate(fp):
            parts = line.split('=', 2)
            if len(parts) == 2:
                os.environ[parts[0].strip()] = parts[1].strip()