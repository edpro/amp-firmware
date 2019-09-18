import os
import sys

entrypoint = " ".join(sys.argv[1:])

if os.name == "nt":
    cmd = f'start "" "C:\\Program Files\\git\\bin\\bash.exe" {entrypoint}'
else:
    cmd = entrypoint

print(cmd)
os.system(cmd)
