import codecs
import markdown
import os
import sys
import shutil
import re

inDir = ''
outDir = ''


# 确保输出路径存在
def confirmDestDir(fileName):
    if os.sep in fileName:
        fileDestDir = os.path.join(outDir, fileName[:fileName.rindex(os.sep)])
        if not os.path.exists(fileDestDir):
            os.makedirs(fileDestDir)


def replaceMdToHtml(matches):
    v1 = matches.group('v1')
    v2 = matches.group('v2')
    v3 = matches.group('v3')
    return v1 + '.html' + v3


def markdownToHtml(filePath):
    # 读取 markdown 文本
    input_file = codecs.open(filePath, mode="r", encoding="utf-8")
    text = input_file.read()
    # 修正md文件中的a标签指向
    # ?P<v1>指定组名
    regexStr = '(?P<v1>- <a href=".*)(?P<v2>.md)(?P<v3>">.*</a>)'
    # pattern1 = re.compile(regexStr)
    # tmp = pattern1.findall(text)

    text = re.sub(regexStr, replaceMdToHtml, text)
    # text = text.replace(regexStr, '.html')
    # 启用扩展来转换表格和代码块
    ext = ['markdown.extensions.extra',
           'markdown.extensions.codehilite',
           'markdown.extensions.tables',
           'markdown.extensions.toc']
    mdConverter = markdown.Markdown(extensions=ext)
    # 转为 html 文本
    html = mdConverter.convert(text)
    # 生成目标文件路径
    relativePath = filePath[filePath.index(inDir) + len(inDir) + 1:]
    relativePath = relativePath[:relativePath.rindex('.md')]
    confirmDestDir(relativePath)
    htmlFile = os.path.join(outDir, relativePath + '.html')
    # 保存为文件
    output_file = codecs.open(htmlFile, mode="w", encoding="utf-8")
    output_file.write(html)


def parseFile(filePath):
    print(filePath + '\n')
    if filePath.endswith('.md'):
        # 生成html文件
        markdownToHtml(filePath)
    else:
        # 拷贝静态文件
        relativePath = filePath[filePath.index(inDir) + len(inDir) + 1:]
        confirmDestDir(relativePath)
        destPath = os.path.join(outDir, relativePath)
        shutil.copy(filePath, destPath)


def entry(fullPath):
    simplePath = fullPath[fullPath.rindex(os.sep) + 1:]
    if simplePath.startswith('.'):
        # 跳过以.开头的文件或文件夹
        return
    if os.path.isdir(fullPath):
        # 处理文件夹
        dirList = os.listdir(fullPath)
        for subPath in dirList:
            # 遍历出所有文件
            entry(os.path.join(fullPath, subPath))
    if os.path.isfile(fullPath):
        # 处理文件
        parseFile(fullPath)


if __name__ == '__main__':
    args = sys.argv
    if not len(args) == 3:
        print('输入文件路径啦!混蛋')
        exit(233)
    inDir = args[1]
    outDir = args[2]
    entry(inDir)
