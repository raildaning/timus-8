#!/usr/bin/env python3

current_key = int(input().strip())
backup_key = int(input().strip())
for thief_key in range(0, 9999):
    if current_key == thief_key:
        print("yes")
        break
    if thief_key > current_key and thief_key > backup_key:
        print("no")
        break
    temp_key = backup_key
    backup_key = current_key
    current_key = temp_key
