import os
import sys
import base64
import pathlib
import getpass
import getopt
import cryptography.fernet as fernet
import cryptography.hazmat.primitives.kdf.pbkdf2 as pbkdf2
import cryptography.hazmat.primitives as primitives

curr_path = pathlib.Path.cwd()

pwd_path = curr_path.joinpath('.passwd')
salt_path = pwd_path.joinpath('_salt')
token_path = pwd_path.joinpath('_token')

enc_path = curr_path.joinpath('encrypt')
dec_path = curr_path.joinpath('decrypt')


def create_salt_file():
    # 生成salt，并以base64保存
    salt_str = base64.urlsafe_b64encode(os.urandom(32)).decode()
    with open(salt_path, 'w', encoding='utf8') as fd:
        fd.write(salt_str)


def get_salt_bytes():
    # 获取byte类型的salt
    with open(salt_path, 'r', encoding='utf8') as fd:
        salt_str = fd.read()
    return base64.urlsafe_b64decode(salt_str.encode())


def get_salt_str():
    # 获取str类型的salt
    with open(salt_path, 'r', encoding='utf8') as fd:
        salt_str = fd.read()
    return salt_str


def derive_padding_bytes(passwd_bytes):
    # 获取kdf，用于生成fernet加密所需的key，Fernet(key)
    kdf = pbkdf2.PBKDF2HMAC(algorithm=primitives.hashes.SHA256(), length=32, salt=get_salt_bytes(), iterations=100000)
    return kdf.derive(passwd_bytes)


def get_encrypt_obj(passwd):
    # 使用salt和password生成一个Fernet所需的key，并以此生成一个Fernet对象
    enc_obj = fernet.Fernet(base64.urlsafe_b64encode(derive_padding_bytes(f'{get_salt_str()}:{passwd}'.encode())))
    return enc_obj


def create_token_file():
    # 使用salt和password生成的Fernet对象，来加密一个真正用来加密文件的token，并以base64保存
    # 即salt和password加密token，而token加密file
    while True:
        p1 = getpass.getpass(prompt='Init password: ')
        p2 = getpass.getpass(prompt='Init password again: ')
        if p1 and p1 == p2:
            break
        else:
            print('Init password ERROR.')
    enc_real_key_bytes = get_encrypt_obj(p1).encrypt(base64.urlsafe_b64encode(os.urandom(32)))
    enc_real_key = base64.urlsafe_b64encode(enc_real_key_bytes).decode()
    with open(token_path, 'w', encoding='utf8') as fd:
        fd.write(enc_real_key)


def runtime_check():
    # 检查运行环境
    pwd_path.mkdir(parents=True, exist_ok=True)
    enc_path.mkdir(parents=True, exist_ok=True)
    dec_path.mkdir(parents=True, exist_ok=True)
    if not salt_path.exists():
        create_salt_file()
    if not token_path.exists():
        create_token_file()


def get_real_encrypt_obj(passwd):
    # 获取真正用来加密文件的Fernet对象
    with open(token_path, 'r', encoding='utf8') as fd:
        enc_real_key = fd.read()
    enc_obj = get_encrypt_obj(passwd)
    real_enc_obj = fernet.Fernet(enc_obj.decrypt(base64.urlsafe_b64decode(enc_real_key.encode())))
    return real_enc_obj


def encrypt_file(ipath, opath, passwd):
    # 以整个文件为对象进行加密
    with open(ipath, 'r', encoding='utf8') as fd:
        need_enc_str = fd.read()
    store_enc_bytes = get_real_encrypt_obj(passwd).encrypt(need_enc_str.encode())
    store_enc_safe_str = base64.urlsafe_b64encode(store_enc_bytes).decode()
    with open(pathlib.Path(opath), 'w', encoding='utf8') as fd:
        fd.write(store_enc_safe_str)


def encrypt_file_by_lines(ipath, opath, passwd):
    # 以文件的行(line)为对象进行加密
    with open(ipath, 'r', encoding='utf8') as fd:
        need_enc_str_arr = fd.read().split(os.linesep)
    real_encrypt_obj = get_real_encrypt_obj(passwd)
    store_enc_bytes_arr = [real_encrypt_obj.encrypt(enc_str.encode()) for enc_str in need_enc_str_arr]
    store_enc_safe_bytes_arr = [base64.urlsafe_b64encode(store_enc_bytes) for store_enc_bytes in store_enc_bytes_arr]
    store_enc_safe_str_arr = [store_enc_safe_bytes.decode() for store_enc_safe_bytes in store_enc_safe_bytes_arr]
    with open(pathlib.Path(opath), 'w', encoding='utf8') as fd:
        fd.write(os.linesep.join(store_enc_safe_str_arr))


def decrypt_file(ipath, opath, passwd):
    # 将输入作为整个文件进行解密
    with open(ipath, 'r', encoding='utf8') as fd:
        store_enc_safe_str = fd.read()
    store_enc_bytes = base64.urlsafe_b64decode(store_enc_safe_str.encode())
    need_enc_str = get_real_encrypt_obj(passwd).decrypt(store_enc_bytes).decode()
    with open(pathlib.Path(opath), 'w', encoding='utf8') as fd:
        fd.write(need_enc_str)


def decrypt_file_by_lines(ipath, opath, passwd):
    # 将输入作为文件的行进行解密
    with open(ipath, 'r', encoding='utf8') as fd:
        store_enc_safe_str_arr = fd.read().split(os.linesep)
    real_encrypt_obj = get_real_encrypt_obj(passwd)
    store_enc_bytes_arr = [base64.urlsafe_b64decode(enc_str.encode()) for enc_str in store_enc_safe_str_arr]
    need_enc_bytes_arr = [real_encrypt_obj.decrypt(store_enc_bytes) for store_enc_bytes in store_enc_bytes_arr]
    need_enc_str_arr = [need_enc_bytes.decode() for need_enc_bytes in need_enc_bytes_arr]
    with open(pathlib.Path(opath), 'w', encoding='utf8') as fd:
        fd.write(os.linesep.join(need_enc_str_arr))


if __name__ == "__main__":
    op_type = ''
    in_path = ''
    enc_type = 'lines'

    tip_str = f'用法:  python {sys.argv[0]} -t [enc|dec] -i <input_file_name/path> [-a]'

    try:
        opts, _args = getopt.getopt(sys.argv[1:], "ht:i:a", ["type=", "ifile="])
    except getopt.GetoptError as e:
        print(e)
        print(f'{tip_str}')
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(f'{tip_str}')
            sys.exit(0)
        elif opt in ("-t", "--type"):
            op_type = arg
        elif opt in ("-i", "--ifile"):
            in_path = arg
        elif opt == '-a':
            enc_type = 'all'

    if not op_type:
        print('-t [enc|dec] 不能为空')
        print(f'{tip_str}')
        sys.exit(1)
    if op_type not in ('enc', 'dec'):
        print(f'-t [enc|dec] 的有效值为 "enc" 或 "dec" 而不是 {op_type}')
        print(f'{tip_str}')
        sys.exit(1)
    if not in_path:
        print('-i <input_file_name/path> 不能为空')
        print(f'{tip_str}')
        sys.exit(1)

    runtime_check()

    files_arr = []
    dirs_arr = []
    input_path = pathlib.Path(in_path)
    if input_path.is_dir():
        for i in input_path.rglob('*'):
            dirs_arr.append(i) if i.is_dir() else files_arr.append(i)
    else:
        files_arr.append(input_path)

    passwd = getpass.getpass(prompt='Input password: ')
    if op_type == 'enc':
        try:
            for i in dirs_arr:
                enc_path.joinpath(i.absolute().relative_to(dec_path)).mkdir(parents=True, exist_ok=True)
            for i in files_arr:
                opath = enc_path.joinpath(i.absolute().relative_to(dec_path))
                encrypt_file_by_lines(i, opath, passwd) if enc_type == 'lines' else encrypt_file(i, opath, passwd)
            print('转换完成')
        except fernet.InvalidToken as e:
            print('密码错误，转换失败')
        except Exception as e:
            print(e)
            print('转换失败')
    elif op_type == 'dec':
        try:
            for i in dirs_arr:
                dec_path.joinpath(i.absolute().relative_to(enc_path)).mkdir(parents=True, exist_ok=True)
            for i in files_arr:
                opath = dec_path.joinpath(i.absolute().relative_to(enc_path))
                decrypt_file_by_lines(i, opath, passwd) if enc_type == 'lines' else decrypt_file(i, opath, passwd)
            print('还原完成')
        except fernet.InvalidToken as e:
            print('密码错误，转换失败')
        except Exception as e:
            print(e)
            print('还原失败')
