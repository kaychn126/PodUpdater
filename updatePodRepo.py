#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Update pod repo and generate .framework use cocoapod-packager '

import os,sys,re,shutil

#获取正在处理的文件夹（外部传入）
def cur_file_dir():
    path = sys.argv[1]
    # print(path)
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

#is working directory clean
def is_woking_directory_clean(path):
    os.chdir(path)
    for line in os.popen("git status").readlines():
        if line.find("working directory clean")>0:
            return 0
    return 1

#替换文件中的行
def replace_file_line(srcline, desline, filename):
    with open(filename, 'r') as f:
        with open(filename+'.new', 'w') as g:
            for line in f.readlines():
                if srcline not in line:
                    g.write(line)
                else:
                    g.write(desline)
        g.close()
    f.close()
    shutil.move(filename+'.new', filename)

#替换文件中的特定的字符
def replace_file_text(src, des, filename):
    with open(filename, 'r') as f:
        with open(filename+'.new', 'w') as g:
            for line in f.readlines():
                if src not in line:
                    g.write(line)
                else:
                    g.write(line.replace(src, des))
        g.close()
    f.close()
    shutil.move(filename+'.new', filename)

#从文件file中获取包含string字符的行
def get_line(string, file):
    filename = os.path.abspath(file)
    with open(filename, 'r') as f:
        for line in f.readlines():
            if string in line:
                return line

#版本号加1,入参为包含版本号的一行字符串
def add_version_number(versionLine):
    verlist = versionLine[versionLine.index('"')+1:-2].split('.')
    addedverint = int(verlist[len(verlist)-1]) + 1
    verlist[len(verlist)-1] = str(addedverint)
    return '.'.join(verlist)

#检查是否有framework文件夹
def check_framework_dir():
    for lists in os.listdir(cur_file_dir()):
        path = os.path.join(cur_file_dir(), lists)
        if os.path.isdir(path):
            sublist = os.listdir(path)
            if "ios" in sublist and "build" in sublist:
                return path
    return ""

#删除framework文件夹和spec文件
def delete_framework_files():
    framework_dir = check_framework_dir()
    if len(framework_dir) > 0:
        shutil.rmtree(framework_dir)

    if len(get_spec_file(cur_file_dir(), "-framework.podspec")) > 0:
        framework_spec_file = get_spec_file(cur_file_dir(), "-framework.podspec")[0]
        if len(framework_spec_file) > 0:
            print(framework_spec_file)
            os.remove(framework_spec_file)


#文件名中包含特定字符的文件
def get_spec_file(dir, spec):
    filelist = []
    for lists in os.listdir(dir):
        path = os.path.join(dir, lists)
        if os.path.isfile(path):
            if(os.path.basename(path).find(spec)>=0):
                filelist.append(path)
    return filelist

#获取pod名字
def get_pod_name():
    filelist = get_spec_file(cur_file_dir(), ".podspec")
    for filename in filelist:
        if "-framework" not in filename:
            return os.path.basename(os.path.splitext(filename)[0])
    return ""

#更新git添加tag,tag可为空
def git_update_with_tag(tag):
    os.system('git add *')
    os.system('git commit -m "pod update"')
    os.system('git pull')
    os.system('git push origin master')
    if len(tag)>0:
        os.system('git tag ' + tag)
        res = os.system('git push origin --tags')
        print('git_update_with_tag 返回值' + str(res))
        return res
    else:
        res = os.system('git push origin')
        print('git_update_with_tag 返回值' + str(res))
        return res


#更新pod
def pod_update(podname):
    repo_push = 'pod repo push EZBSpecs ' + podname + '.podspec ' + '--sources=https://github.com/CocoaPods/Specs.git,https://git.coding.net/cker/EZBSpecs.git --allow-warnings --verbose'
    res = os.system(repo_push)
    print('pod_update 返回值' + str(res))
    return res

#打包framework
def pod_package_framework(file):
    commond = "pod package " + file + " --spec-sources=https://github.com/CocoaPods/Specs.git,https://git.coding.net/cker/EZBSpecs.git --force --no-mangle"
    res = os.system(commond)
    print('pod_package 返回值' + str(res))
    return res

#处理framework文件: 包括重命名framework文件夹名字，framework文件夹内的.podspec文件内容修改 .podspec文件位置移动并提交git
#返回新的版本号
def process_framework_files(filename):
    if len(filename) > 0:
        #文件夹重命名
        new_framework_dir_name = get_pod_name() + "-framework"
        os.rename(filename, new_framework_dir_name)

        #.podspec文件重命名并移动位置
        spec_file_list = get_spec_file(new_framework_dir_name, ".podspec")
        new_spec_file_name = get_pod_name() + "-framework.podspec"
        if len(spec_file_list) > 0:
            old_spec_file_name = spec_file_list[0]
            os.rename(old_spec_file_name, new_spec_file_name)

        #修改podspec文件内容
        #修改name
        name_line = get_line('s.name', new_spec_file_name)
        new_name_line = "  s.name = " + "'" + os.path.split(new_framework_dir_name)[1] + "'\n"
        replace_file_line(name_line, new_name_line, new_spec_file_name)

        #修改s.source
        source_line = get_line('s.source', new_spec_file_name)
        new_source_line = get_line('s.source', get_pod_name() + ".podspec")
        replace_file_line(source_line, new_source_line, new_spec_file_name)

        #修改s.ios.preserve_paths
        preservepaths_line = get_line('s.ios.preserve_paths', new_spec_file_name)
        new_preservepaths_line = "  s.ios.preserve_paths       = " + "'" + os.path.basename(new_framework_dir_name) + "/ios/" + get_pod_name() + ".framework" + "'\n"
        replace_file_line(preservepaths_line, new_preservepaths_line, new_spec_file_name)

        #修改s.ios.public_header_files
        public_header_files_line = get_line('s.ios.public_header_files', new_spec_file_name)
        new_public_header_files_line = "#  s.ios.public_header_files  = " + "'" + os.path.basename(new_framework_dir_name) + "/ios/" + get_pod_name() + ".framework/Versions/A/Headers/*.h" + "'\n"
        replace_file_line(public_header_files_line, new_public_header_files_line, new_spec_file_name)

        #修改s.ios.resource
        pod_spec_file_name = get_pod_name() + ".podspec"
        resource_line = get_line('s.ios.resource', new_spec_file_name)
        new_resource_line = "  s.ios.resource             = " + "'" + os.path.basename(new_framework_dir_name) + "/ios/" + get_pod_name() + ".framework/Versions/A/Resources/**/*" + "'\n"

        pod_resource_line = get_line("s.resource", pod_spec_file_name)
        pod_resources_line = get_line("s.resources", pod_spec_file_name)
        if len(pod_resource_line)>0 and len(pod_resources_line)>0:
            if get_line("s.resource", pod_spec_file_name).strip(' ')[0] is "#" and get_line("s.resources", pod_spec_file_name).strip(' ')[0] is "#":
                new_resource_line = "#" + new_resource_line

        replace_file_line(resource_line, new_resource_line, new_spec_file_name)

        #修改s.ios.vendored_frameworks
        vendored_frameworks_line = get_line('s.ios.vendored_frameworks', new_spec_file_name)
        new_vendored_frameworks_line = "  s.ios.vendored_frameworks  = " + "'" + os.path.basename(new_framework_dir_name) + "/ios/" + get_pod_name() + ".framework" + "'\n"
        replace_file_line(vendored_frameworks_line, new_vendored_frameworks_line, new_spec_file_name)

        #单引号全部替换成双引号
        replace_file_text('\'','\"' , new_spec_file_name)

        #版本号再次加1
        new_framework_version_number = add_version_number(get_line("s.version", new_spec_file_name))
        new_framework_version_number_line = '  s.version      =  "' + new_framework_version_number + '"\n'
        #修改-framework.podspec文件
        replace_file_line(get_line("s.version", new_spec_file_name), new_framework_version_number_line, new_spec_file_name)

        #修改.podspec文件
        replace_file_line(get_line("s.version", pod_spec_file_name), new_framework_version_number_line, pod_spec_file_name)

        return new_framework_version_number
    return ""

def main():
    os.chdir(cur_file_dir())

    #无任何修改并且有framework文件的情况下 不做任何操作
    if is_woking_directory_clean(cur_file_dir()) == 0 and len(check_framework_dir) > 0:
        print(os.path.basename(cur_file_dir()) + "没有修改记录，不做操作")
        return

    #删除framework文件
    delete_framework_files()

    #获取pod_name
    pod_name = get_pod_name()

    #.podspec文件名
    pod_spec_file_name = os.path.join(cur_file_dir(), pod_name + ".podspec")
    #版本号加1
    new_version_number = add_version_number(get_line("s.version", pod_spec_file_name))
    new_version_number_line = '  s.version      =  "' + new_version_number + '"\n'
    replace_file_line(get_line("s.version", pod_spec_file_name), new_version_number_line, pod_spec_file_name)

    #提交git,打tag
    if git_update_with_tag(new_version_number) == 0:
        #更新pod
        if pod_update(pod_name) == 0:
            #打包framework
            if pod_package_framework(pod_spec_file_name) == 0:
                #处理framework文件
                new_framework_version_number = process_framework_files(check_framework_dir())

                #处理完framework文件再次提交git并打tag
                if git_update_with_tag(new_framework_version_number) == 0:
                    #更新pod和frameworkpod
                    pod_update(pod_name)

                    #如果framework上传pod失败则清除framework文件
                    if pod_update(pod_name + "-framework") != 0:
                        delete_framework_files()
                        git_update_with_tag("")

main()
# cur_file_dir()
