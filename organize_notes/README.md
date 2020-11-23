## 笔记整理

依据关键行切分笔记，进行整理和分类

### 依赖

``` bash
# python >=3.6.8
```

### 注意

默认在脚本的所在目录生成 `categories` 目录保存按分类进行整理的笔记

默认在脚本的所在目录生成 `tags` 目录保存按标签进行整理的笔记

``` python
# 切分匹配规则
lineStr.startswith('<!-- //') and lineStr.endswith('// -->')
# 满足上述匹配规则的进行向上查找最近的满足下述规则的行作为标题
lineStr.startswith('## ')

# <!-- // catg1, catg2; tag1, tag2 // -->
# 分号为切分，逗号为列表 => 分类1,分类2 ; 标签1,标签2
```

### 使用

``` bash
python organize_notes.py 'path/f1.md' 'path/f2.md' 'path/f3.md'
  # 不带参数默认整理脚本所在目录的'Notes.md'文件
```
