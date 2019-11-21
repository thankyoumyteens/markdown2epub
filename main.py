import codecs
import markdown
import os
import sys
import shutil
import re
import mkepub

# 源文件夹
inDir = ''
# 输出文件夹
outDir = ''
epubTitle = '标题'
epubAuthor = '作者'


# todo bug to fix
def makeContent(curPath, book, node):
    """
    生成epub的电子书内容
    :param curPath: 当前路径
    :param book: epub对象
    :param node: 上一级节点
    :return:
    """
    if os.path.isdir(curPath):
        if os.sep in curPath:
            chapter = curPath[curPath.rindex(os.sep) + 1:]
        else:
            chapter = curPath
        if 'img' not in curPath and 'epub' not in curPath:
            n = book.add_page(chapter, '<h1>' + chapter + '</h1>', parent=node)
        else:
            n = None
        # 处理文件夹
        dirList = os.listdir(curPath)
        for subPath in dirList:
            makeContent(os.path.join(curPath, subPath), book, n)
    if os.path.isfile(curPath):
        if curPath[curPath.rindex('.') + 1:] == 'html':
            with open(curPath, 'r', encoding='utf-8') as file:
                title = curPath[curPath.rindex(os.sep) + 1:curPath.rindex('.')]
                book.add_page(title, file.read(), parent=node)
        else:
            with open(curPath, 'rb') as file:
                book.add_image(curPath[curPath.rindex(os.sep) + 1:], file.read())


def makeEPub(rootDir):
    """
    制作epub电子书
    :param rootDir: html文件的根目录
    :return:
    """
    epubDir = os.path.join(outDir, 'epub')
    if not os.path.exists(epubDir):
        os.makedirs(epubDir)
    epubFile = os.path.join(epubDir, epubTitle + '.epub')
    # 删除旧文件
    if os.path.exists(epubFile):
        os.remove(epubFile)
    book = mkepub.Book(title=epubTitle, author=epubAuthor)
    # 封面
    with open('cover.jpg', 'rb') as file:
        book.set_cover(file.read())
    # css
    with open('style.css') as file:
        book.set_stylesheet(file.read())
    # 内容
    makeContent(rootDir, book, None)
    # 写入文件
    book.save(epubFile)


def confirmDestDir(fileName):
    """
    确保输出路径存在
    :param fileName:
    :return:
    """
    if os.sep in fileName:
        fileDestDir = os.path.join(outDir, fileName[:fileName.rindex(os.sep)])
        if not os.path.exists(fileDestDir):
            os.makedirs(fileDestDir)


def replaceMdToHtml(matches):
    """
    将- <a href="study/server/index.md">Linux服务器</a>
    转换成 - <a href="study/server/index.html">Linux服务器</a>
    :param matches:
    :return:
    """
    v1 = matches.group('v1')
    v2 = matches.group('v2')
    v3 = matches.group('v3')
    return v1 + '.html' + v3


def markdownToHtml(filePath):
    """
    markdown文件转换成html文件
    :param filePath:
    :return:
    """
    # 读取 markdown 文本
    input_file = codecs.open(filePath, mode="r", encoding="utf-8")
    text = input_file.read()
    input_file.close()
    # 修正md文件中的a标签指向
    # ?P<v1>指定组名
    regexStr = '(?P<v1>- <a href=".*)(?P<v2>.md)(?P<v3>">.*</a>)'
    # pattern1 = re.compile(regexStr)
    # tmp = pattern1.findall(text)
    # 替换内容
    text = re.sub(regexStr, replaceMdToHtml, text)
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
    output_file.close()


def parseFile(filePath):
    """
    开始转换文件
    :param filePath:
    :return:
    """
    print(filePath + '\t...\n')
    if filePath.endswith('.md'):
        # 生成html文件
        markdownToHtml(filePath)
    else:
        # 拷贝静态文件
        relativePath = filePath[filePath.index(inDir) + len(inDir) + 1:]
        confirmDestDir(relativePath)
        destPath = os.path.join(outDir, relativePath)
        shutil.copy(filePath, destPath)


def makeHtml(fullPath):
    """
    遍历所有文件进行转换
    :param fullPath:
    :return:
    """
    simplePath = fullPath[fullPath.rindex(os.sep) + 1:]
    if simplePath.startswith('.'):
        # 跳过以.开头的文件或文件夹
        return
    if os.path.isdir(fullPath):
        # 处理文件夹
        dirList = os.listdir(fullPath)
        for subPath in dirList:
            # 遍历出所有文件, 注意传入完整路径, 否则判断不了
            makeHtml(os.path.join(fullPath, subPath))
    if os.path.isfile(fullPath):
        # 处理文件
        parseFile(fullPath)


def entry(rootDir):
    """
    程序入口
    :param rootDir: 根目录
    :return: void
    """
    print('开始生成html文件\n')
    makeHtml(rootDir)
    print('生成html文件完成\n')
    print('开始生成epub\n')
    makeEPub(outDir)
    print('生成epub完成\n')


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 3:
        print('输入文件路径啦!混蛋')
        exit(233)
    inDir = args[1]
    outDir = args[2]
    if len(args) == 4:
        epubTitle = args[3]
    if len(args) == 5:
        epubTitle = args[3]
        epubAuthor = args[4]
    entry(inDir)
