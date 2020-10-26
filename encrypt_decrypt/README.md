## 加/解密文件

使用 `cryptography` 模块，对文件进行加/解密，并以base64保存密文。

### 依赖

``` bash
# Python >= 3.6.8
pip install cryptography
```

### 注意

默认在脚本的所在目录生成 `.passwd` 目录保存 `_salt` 和 `_token` 文件。 `_salt` 文件保存与 `password` 合用的 `salt` ， `_token` 文件保存着真正用来加密文件的 `key` 。

***脚本所在位置的 `.passwd` 目录以及其内的文件都是解密文件所必需的，不能删除。***

默认在脚本的所在目录生成 `decrypt` 目录，目录用来保存解密出来的文件。

默认在脚本的所在目录 `encrypt` 保存生成的加密文件。

### 使用

``` bash
python encrypt_decrypt.py -t [enc|dec] -i <input_file_name/path> [-a]
  # -t [enc|dec] 指定加/解密操作，enc 加密 dec 解密
  # -i <input_file_name/path> 指定需要加/解密的文件/目录
  # -a 指定整个文件作为加密对象，默认为文件的行(line)为加密对象
```
