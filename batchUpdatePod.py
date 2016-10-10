#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys

#获取正在处理的文件夹（外部传入）
def cur_file_dir():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        # print(path)
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)
    else:
        print("请输入地址")


#检查是否是pod文件夹
def is_pod_dir(path):
    sublist = os.listdir(path)
    for line in sublist:
        if line.find(".podspec") > 0:
            return path
    return ""

def find_pod_file(path):
    pod_file_list = []
    for lists in os.listdir(path):
        subpath = os.path.join(path, lists)
        if os.path.isdir(subpath):
            if len(is_pod_dir(subpath))>0:
                #找到pod文件夹
                process_pod_file(subpath)
            else:
                find_pod_file(subpath)

def process_pod_file(path):
    commond = './updatePodRepo.py ' + path
    os.system(commond)

#找到所有pod文件夹
def find_all_pod_file():
    find_pod_file(cur_file_dir())

find_all_pod_file()
