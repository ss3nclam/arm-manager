# import re


# reg = r"\x1b\[[0-9;]*[mGKH]"
# x = "\x1b[1;31m0.39/17.5 GB\x1b[0m"
# print(re.findall(reg, x))

for timestamp in (i * 3_600 for i in (24, 12, 6, 3, 1)):
    print(timestamp)