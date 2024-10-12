config = {}
file = open("config.txt", "r").readlines()
for line in file:
    if "=" in line:
        if line.startswith("#"):
            pass
        else:
            split_line = line.split(sep=None)
            name = split_line[0]
            value = split_line[2]
            config[name] = value

