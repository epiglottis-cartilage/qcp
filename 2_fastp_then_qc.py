#!/bin/python3

import os
import re


fix_q = None
fix_l = None
pop_browser = True

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
    srrs = [f.name for f in os.scandir(
        sample) if f.is_dir() and f.name.startswith('SRR')]

    if len(srrs) == 1:
        for srr in srrs:
            # 检查是否存在fastp.json文件 有则跳过
            print(sample)
            if os.path.exists(f'{sample}/{srr}/fastp.json'):
                print('[skip]')
                continue

            # 打开浏览器要求检视 -q -l
            if pop_browser:
                os.system(
                    f'microsoft-edge {sample}/{srr}/{srr}_fastqc.html > /dev/null 2>&1 &')

            if fix_q is not None and fix_l is not None:
                q = fix_q
                l = fix_l
            else:
                while True:
                    q = input(f'-q:')
                    l = input(f'-l:')
                    if input(f'q={q} l={l} (OK? Y/n)') == '':
                        break


            a0 = '--adapter_fasta ../../adapters/TruSeq3-SE.fa'

            cmds.append(f'cd {sample}/{srr} && fastp -q {q} -l {l} -i {srr}.fastq.gz -o fastp_{srr}.fastq.gz {a0} -w 8 > p.log 2>&1')

            # fastqc
            cmds.append(
                f'cd {sample}/{srr} && fastqc -t 8 fastp_{srr}.fastq.gz > qc1.log 2>&1 &')
    else:
        print(f'multi srr!')
        if os.path.exists(f'{sample}/merged/fastp.json'):
            print('[skip]')
            continue
        
        cmds.append(f'rm -rf {sample}/merged/*')

        os.makedirs(f"{sample}/merged", exist_ok=True)

        end = {}

        for srr in srrs:
            files = [f.name for f in os.scandir(f"{sample}/{srr}") if f.is_file()]
            files = [f for f in files if f.endswith('.fastq.gz')]

            for file in files:
                # 末尾编号
                end_with = file.split('_')[-1].split('.')[0]
                if end_with not in end:
                    end[end_with] = []
                end[end_with].append(f"{sample}/{srr}/{file}")
                print(srr, file, end_with)


        for (id, files) in end.items():
            # 清空原有
            cmds.append(f"> {sample}/merged/{sample}_merged_{id}.fastq.gz")
            for file in files:
                print("merge", file)
                # 合并文件
                cmds.append(f"cat {file} >> {sample}/merged/{sample}_merged_{id}.fastq.gz")

        # 打开浏览器要求检视 -q -l
        if pop_browser:
            os.system(
                f"microsoft-edge {list(end.values())[0][0].split('.')[0]}_fastqc.html > /dev/null 2>&1 &")
        
        if fix_q is not None and fix_l is not None:
                q = fix_q
                l = fix_l
        else:
            while True:
                q = input(f'-q:')
                l = input(f'-l:')
                if input(f'q={q} l={l} (OK? Y/n)') == '':
                    break

        if end.get('1') is not None:

            file1 = f"{sample}_merged_1.fastq.gz"
            file2 = f"{sample}_merged_2.fastq.gz"

            a0 = '--adapter_fasta ../../adapters/TruSeq3-SE.fa'

            cmds.append(f'cd {sample}/merged && fastqc -t 8 {file1} {file2} > qc1.log 2>&1 &')
            cmds.append(f'cd {sample}/merged && fastp -q {q} -l {l} -i {file1} -I {file2} -o fastp_{file1} -O fastp_{file2} -w 8 {a0} > p.log 2>&1')
            cmds.append(f'cd {sample}/merged && fastqc -t 8 fastp_{file1} fastp_{file2} > qc2.log 2>&1 &')

        end.pop('1')
        end.pop('2')

        # 没有分 12 的情况，未测试
        for (id, files) in end.items():
            raise "未知的情况"

            assert len(files) <= 1


for cmd in cmds:
    print(cmd)
    os.system(cmd)
