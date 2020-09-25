#!/usr/bin/python3

import os
import re
import sys

import yaml

CONFIG_FILE_IN = "config_all.yml"
CONFIG_FILE_OUT = "config_custom.yml"

print(f"Loading devices from \"{CONFIG_FILE_IN}\" ...")

with open(CONFIG_FILE_IN) as f:
    config_in = yaml.safe_load(f.read())

print(f"Loaded {len(config_in['devices'])} devices.")
if os.isatty(sys.stdin.fileno()):
    print()
    print("Enter MAC addresses, end with CTRL-D")

p = re.compile(r"[^0-9a-f]")
config_out = {"devices": {}}
for line in sys.stdin:
    mac = p.sub("", line.lower())
    device = config_in["devices"].get(mac)
    if device is None:
        print(f"NOT FOUND: {line.strip()}")
    else:
        config_out["devices"][mac] = device

with open(CONFIG_FILE_OUT, "w") as f:
    yaml.dump(config_out, f)

print(f"Finished writing {len(config_out['devices'])} devices to \"{CONFIG_FILE_OUT}\"")
