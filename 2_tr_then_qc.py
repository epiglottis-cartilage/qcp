#!/bin/python3

import os


fix_q = None
fix_l = None

if input("fixed q l value? y/N?") == 'y':
    while True:
        fix_q = input("q:").strip()
        fix_l = input("l:").strip()
        pop_browser = False
        if input(f"{fix_q=} {fix_l=} Y/n?") == '':
            break

# 获取当前目录所有文件夹
samples = [f.name for f in os.scandir() if f.is_dir()
           and f.name.startswith('GSM')]

cmds = []

# 遍历所有文件夹
for sample in samples:
    srrs = [f.name for f in os.scandir(sample) if f.is_dir() and f.name.startswith('SRR')]

    if len(srrs) == 1:
        for srr in srrs:
            print(sample)
            if os.path.exists(f'{sample}/{srr}/tr_{srr}.log'):
                print('[skip]')
                continue
            
            if fix_q is not None and fix_l is not None:
                q = fix_q
                l = fix_l
            else:
                while True:
                    q = input(f'-q:')
                    l = input(f'-l:')
                    if input(f'q={q} l={l} (OK? Y/n)') == '':
                        break

            cmds.append(f'cd {sample}/{srr} && TrimmomaticSE -threads 8 {srr}.fastq.gz tr_{srr}.fastq.gz ILLUMINACLIP:TruSeq3-SE.fa:2:30:10 LEADING:{q} TRAILING:{q} SLIDINGWINDOW:4:15 MINLEN:{l} > tr.log 2>&1')

            # fastqc
            cmds.append(
                f'cd {sample}/{srr} && fastqc -t 8 tr_{srr}.fastq.gz > qc1.log 2>&1 &')
    else:
        print(f'multi srr!')
        raise "You open wrong file!"


for cmd in cmds:
    print(cmd)
    os.system(cmd)
