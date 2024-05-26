#!/ust/bin/python3

# 从all.txt中筛选样本，并写入want.txt
wants = []
with open('./all.txt', 'r') as f:
    for line in f.readlines():
        line = line.strip().split()
        name, type = line[0], line[1]

        if type.startswith(('SCN', 'DRG')) and type.endswith(('1', '2')):
            wants.append(name)
            print(name, type)

with open('./want.txt', 'w') as f:
    for w in wants:
        f.write(w + '\n')
