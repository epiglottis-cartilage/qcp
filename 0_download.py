#!/bin/python3 

# 从want.txt下载fastq.gz文件

import requests
import json
import os


def get_srr(target: str):
    url = "https://www.ncbi.nlm.nih.gov/Traces/solr-proxy-be/solr-proxy-be.cgi?core=run_sel_index"
    body = f"""q=start%3D0%26rows%3D0%26q%3D-non_public_run%253A%255B*%2520TO%2520*%255D%2520AND%2520((primary_search_ids%253A%2522{
        target}%2522))%26wt%3Djson%26facet%3Don%26facet.mincount%3D1%26facet.limit%3D150%26facet.field%3Dfields%26facet.field%3Dfieldvals%26stats%3Dtrue%26stats.field%3Dbases_l%26stats.field%3Dbytes_l"""
    res = requests.post(url, data=body)
    res = json.loads(res.text)

    res = list(filter(lambda each: str(each)[
        :7] == "acc_s: ", res['facet_counts']['facet_fields']['fieldvals']))
    res = list(map(lambda each: each[7:].upper(), res))

    return res


def srr2ftp(target: str) -> list[str]:
    url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?result=read_run&fields=fastq_ftp&format=JSON&accession={
        target}"
    res = requests.get(url)
    res: str = json.loads(res.text)[0]['fastq_ftp']
    res = res.split(';')

    return res


cmds = []
if __name__ == "__main__":
    with open("want.txt", "r") as f:
        targets = f.read().split()

    for sample in targets:
        print('\n', sample, end=":")
        SRRs = get_srr(sample)

        os.makedirs(sample, exist_ok=True)
        for srr in SRRs:
            print('\n ', srr, end=':')

            FTPs = srr2ftp(srr)
            os.makedirs(f"{sample}/{srr}", exist_ok=True)

            for ftp in FTPs:
                print('\n  ', ftp, end=' ', flush=True)

                name_ftp = f"{sample}-{ftp.split('/')[-1]}"
                name_full = ftp.split('/')[-1]
                name = name_full.split('/')[-1]

                # 当同名文件存在时跳过
                if os.path.exists(f"{sample}/{srr}/{name_full}"):
                    print('[skip]', end='')
                    if not os.path.exists(f"{sample}/{srr}/qc.log"):
                        print('[but qc]', end='')
                        os.system(f"cd {sample}/{srr}/ && python3 ../../1_first_analyze.py {name_full} &")
                    continue
                os.system(f"aria2c -x 8 ftp://{ftp} -o {name_ftp}")
                os.system(f"mv {name_ftp} {sample}/{srr}/{name_full}")
                os.system(f"cd {sample}/{srr}/ && python3 ../../1_first_analyze.py {name_full} &")

        print()
