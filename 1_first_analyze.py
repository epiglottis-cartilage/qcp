#!/bin/python3 

import os
import sys

# 从arg获取文件名
name_full = sys.argv[1]
name = name_full.split('/')[-1]

os.system(f'fastqc -t 8 {name_full} >> qc.log 2>&1')
