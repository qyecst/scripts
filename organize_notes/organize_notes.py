import os
import re
import sys
import pathlib

curr_path = pathlib.Path.cwd()
catgs_path = curr_path.joinpath('categories')
tags_path = curr_path.joinpath('tags')


def runtime_check():
    # 创建文件夹
    catgs_path.mkdir(parents=True, exist_ok=True)
    tags_path.mkdir(parents=True, exist_ok=True)


def md_file_read(ipath):
    # 读取文件按行切分
    with open(ipath, 'r', encoding='utf8') as f:
        file_str_arr = f.read().split(os.linesep)
    return file_str_arr


def md_content_split(str_arr):
    # 关键字切分字符串数组内容，记录索引以及关键字信息
    split_idx_arr = []
    for i, s in enumerate(str_arr):
        if s.startswith('<!-- //') and s.endswith('// -->'):
            for j in range(i - 1, split_idx_arr[-1][0] if len(split_idx_arr) else 0, -1):
                if str_arr[j].startswith('## '):
                    split_idx_arr.append([j, s])
                    break
    # 提取信息，合并字符串数组为字符串
    split_content_arr = []
    for i in range(0, len(split_idx_arr)):
        info = re.match('<!-- //(.*)// -->', split_idx_arr[i][1]).group(1).strip()
        content = str_arr[split_idx_arr[i][0]: (split_idx_arr[i + 1][0] if i < len(split_idx_arr) - 1 else None)]
        # content.insert(1, '')
        content.insert(1, '> ' + info)
        content.insert(1, '')
        split_content_arr.append({
            'categories': [s.strip() for s in info.split(';')[0].split(',')],
            'tags': [s.strip() for s in info.split(';')[1].split(',')],
            'content': os.linesep.join(content)
        })
    return split_content_arr


def md_content_organize(info_arr):
    # 按categories和tags进行分类
    categories_dict = {}
    tags_dict = {}
    for split_info in info_arr:
        for e in split_info:
            for c in e['categories']:
                if categories_dict.get(c):
                    categories_dict[c].append(e['content'])
                else:
                    categories_dict[c] = []
                    categories_dict[c].append(e['content'])
            for t in e['tags']:
                if tags_dict.get(t):
                    tags_dict[t].append(e['content'])
                else:
                    tags_dict[t] = []
                    tags_dict[t].append(e['content'])
    return categories_dict, tags_dict


def save_to_file(info):
    # 保存至文件
    catgs, tags = info
    for k, v in catgs.items():
        with open(catgs_path.joinpath(f'{k}.md'), 'w', encoding='utf8') as f:
            f.write(os.linesep.join(v))
    for k, v in tags.items():
        with open(tags_path.joinpath(f'{k}.md'), 'w', encoding='utf8') as f:
            f.write(os.linesep.join(v))


if __name__ == "__main__":
    runtime_check()
    # python3.6后dict为有序，以此进行参数数组去重
    input_files = list({}.fromkeys(sys.argv[1:]).keys())
    split_info_arr = []
    if len(input_files) > 0:
        for f in input_files:
            split_info_arr.append(md_content_split(md_file_read(f)))
    else:
        # 默认值
        split_info_arr.append(md_content_split(md_file_read('Notes.md')))
    save_to_file(md_content_organize(split_info_arr))
