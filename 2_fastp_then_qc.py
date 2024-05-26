#!/bin/python3 

import os
import re

# 获取当前目录所有文件夹
samples = [f.name for f in os.scandir() if f.is_dir()
           and f.name.startswith('GSM')]

cmds = []

pop_browser = False

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

            while True:
                q = input(f'-q:')
                l = input(f'-l:')
                if input(f'q={q} l={l} (OK? Y/n)') == '':
                    break

            report = open(f'./{sample}/{srr}/{srr}_fastqc.html').read()

            overrepresented = re.findall(r'[ATCGU]{15,}', report)
            assert len(overrepresented) <= 1

            if len(overrepresented) == 1:
                overrepresented = overrepresented[0]
                print(f'{overrepresented=}')
                # fastp
                cmds.append(f'cd {sample}/{srr} && fastp -q {q} -l {l} -i {srr}.fastq.gz -o fastp_{srr}.fastq.gz -a {overrepresented} -w 8 > 2.log 2>&1')
            else:
                cmds.append(f'cd {sample}/{srr} && fastp -q {q} -l {l} -i {srr}.fastq.gz -o fastp_{srr}.fastq.gz -w 8 > 2.log 2>&1')

            # fastqc
            cmds.append(
                f'cd {sample}/{srr} && fastqc -t 8 fastp_{srr}.fastq.gz > 3.log 2>&1 &')
    else:
        print(f'multi srr!')
        if os.path.exists(f'{sample}/merged/fastp.json'):
            print('[skip]')
            continue

        os.makedirs(f"{sample}/merged", exist_ok=True)

        end = {}
        overrepresented = {}

        for srr in srrs:
            files = [f.name for f in os.scandir(
                f"{sample}/{srr}") if f.is_file()]
            files = [f for f in files if f.endswith('.fastq.gz')]

            for file in files:
                # 末尾编号
                end_with = file.split('_')[-1].split('.')[0]
                if end_with not in end:
                    end[end_with] = []
                end[end_with].append(f"{sample}/{srr}/{file}")
                print(srr, file, end_with)

                report = open(
                    f'./{sample}/{srr}/{file.split('.')[0]}_fastqc.html').read()
                if end_with not in overrepresented:
                    overrepresented[end_with] = set()
                overrepresented[end_with] = overrepresented[end_with].union(set(re.findall(
                    r'[ATCGU]{15,}', report)))

        for (id, files) in end.items():
            os.system(
                # 清空原有
                f"> {sample}/merged/{sample}_merged_{id}.fastq.gz")
            for file in files:
                print("merge", file)
                os.system(
                    f"cat {file} >> {sample}/merged/{sample}_merged_{id}.fastq.gz")

        # 打开浏览器要求检视 -q -l
        if pop_browser:
            os.system(
                f'microsoft-edge {list(end.values())[0][0].split('.')[0]}_fastqc.html > /dev/null 2>&1 &')

        while True:
            q = input(f'-q:')
            l = input(f'-l:')
            if input(f'q={q} l={l} (OK? Y/n)') == '':
                break

        if end.get('1') is not None:

            file1 = f"{sample}_merged_1.fastq.gz"
            file2 = f"{sample}_merged_2.fastq.gz"

            assert len(overrepresented['1']) <= 1
            assert len(overrepresented['2']) <= 1

            a1 = f"-a {list(overrepresented['1'])[0]}" if len(overrepresented['1']) == 1 else ''
            a2 = f"--adapter_sequence_r2 {list(overrepresented['1'])[0]}" if len(overrepresented['1']) == 1 else ''

            cmds.append(f'cd {sample}/merged && fastqc -t 8 {file1} {file2} > 3.log 2>&1 &')
            cmds.append(f'cd {sample}/merged && fastp -q {q} -l {l} -i {file1} -I {file2} -o fastp_{file1} -O fastp_{file2} -w 8 {a1} {a2} > 2.log 2>&1')
            cmds.append(f'cd {sample}/merged && fastqc -t 8 fastp_{file1} fastp_{file2} >> 4.log 2>&1 &')

        end.pop('1')
        end.pop('2')

        # 没有分 12 的情况，未测试
        for (id, files) in end.items():
            raise "未知的情况"
        
            assert len(files) <= 1
            assert len(overrepresented[id]) <= 1

            a = f"-a {list(overrepresented[id])[0]}" if len(overrepresented[id]) == 1 else ''

            file = f"{sample}_merged_{id}.fastq.gz"

            cmds.append(f'cd {sample}/merged &&\
                        fastp -q {q} -l {l} -i {file} -o fastp_{file} {a} -w 8 > {id}.log 2>&1')
            cmds.append(f'cd {sample}/merged &&\
                        fastqc -t 8 {files[0]} > 3.log 2>&1 &')


for cmd in cmds:
    print(cmd)
    os.system(cmd)
