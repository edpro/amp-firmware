import os
import sys

entrypoint = sys.argv[1]

if os.name == "nt":
    os.system(f'start "" "C:\\Program Files\\git\\bin\\bash.exe" {entrypoint}')
else:
    os.system(entrypoint)
