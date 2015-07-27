#!/usr/bin/env python
# coding:UTF-8

import os,sys,shutil,subprocess,filecmp,tempfile
from os import path
# 将dirlist中的目录列表下的文件放在一个文件词典filesdict中,
# 词典的key是dirlist中某个目录下的文件名(不含该目录名),
# value是dirlist中存在对应的key的所有目录
def getfilesfromdirs(dirlist):
    filesdict = {}
    for onedir in dirlist:
        onedir = path.realpath(onedir)  # 规范化目录名
        #处理目标路径下(含子目录下)的所有文件
        for root,dirs,files in os.walk(onedir):
            if '.svn' in dirs:
                dirs.remove('.svn')
            if os.path.basename(root) == ".svn":
                continue
            # 记录每个文件名所属的目录,同名文件则会属于多个不同目录.
            # 这样就生成了文件名到文件所在目录的倒排索引
            for onefile in files:
                # 若该文件名的键值还未创建则先创建
                onefile = os.path.join(root,onefile)[len(onedir)+1:]
                if onefile not in filesdict:
                    filesdict[onefile] = []
                filesdict[onefile] += [onedir]
    return filesdict

def vimDirDiffN(diffdirs):
    (fd,diffbuffer) = tempfile.mkstemp()
    filesdict = getfilesfromdirs(diffdirs)
    fileslines = []
    for key,values in filesdict.iteritems():
        fileslines += [(key, values)]

    files = []
    for i in range(len(fileslines)):
        (f, v) = fileslines[i]
        for i in range(len(v)):
            for j in range (i+1,len(v)):
                if not filecmp.cmp(os.path.join(v[i],f), os.path.join(v[j],f)):
                    files += [(f, v)]
                    break
            else:
                continue
            break

    fp = os.fdopen(fd,'w')
    fp.write(str(len(diffdirs))+'\n')

    dirsymbol = 'A'
    for onedir in diffdirs:
        dirline = '<' + dirsymbol + '>' + '=' + onedir
        fp.write(dirline + '\n')
        for i in range(len(files)):
            (f, v) = files[i]
            for i in range(len(v)):
                if v[i] == onedir:
                    v[i] = '<' + dirsymbol + '>' 
            files[i] = (f, v)

        dirsymbol = chr(ord(dirsymbol) + 1)

    for (f,v) in files:
        fp.write('    File: /'+f+' @ ' + ','.join(v)+'\n')

    fp.flush()
    vim=subprocess.Popen('gvim -f -c ":DirDiffN ' + diffbuffer + '"',shell=True)
    vim.wait()
    fp.close()
    os.remove(diffbuffer)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        diffdirs = sys.argv[1:]
        for index in range(0,len(diffdirs)):
            diffdirs[index] = path.realpath(diffdirs[index])
        vimDirDiffN(diffdirs)
    else:
        print "Interactive Mode."
        diffdirs = raw_input('input the dirs you want to diff(in List["A","B"]): ')
        if diffdirs == '':
            diffdirs = ['f:/PYOutput/old','f:/PYOutput/new','f:/PYOutput/third_merge']
        else:
            diffdirs = eval(diffdirs)
        for index in range(0,len(diffdirs)):
            diffdirs[index] = path.realpath(diffdirs[index])
        vimDirDiffN(diffdirs)
        raw_input('press to exit.')
