## certbot dns hook

使用 [Certbot](https://certbot.eff.org) ACME客户端进行 [Let’s Encrypt](https://letsencrypt.org) 通配符域名证书的申请。

Certbot 提供了 [Pre and Post Validation Hooks](https://certbot.eff.org/docs/using.html#pre-and-post-validation-hooks) 可以在dns验证的前后执行自定义脚本，通过编写自定义脚本实现dns验证/证书申请的自动化。

### cert_aliyun_dns_hook.sh

使用阿里云提供的cli命令 [aliyun-cli](https://github.com/aliyun/aliyun-cli) 操作云解析DNS，自动操作通配符域名证书申请所需要的 `_acme-challenge` TXT记录。

#### 依赖

``` bash
# jq dig aliyun
dnf install -y jq bind-utils

# https://github.com/aliyun/aliyun-cli TO INSTALL `aliyun`
# `aliyun` 需要配置具有 AliyunDNSFullAccess/管理云解析(DNS)的权限
# https://www.alibabacloud.com/help/zh/doc-detail/121258.htm
```

#### 使用

0 参数

``` bash
cert_aliyun_dns_hook.sh auth # auth 参数用于certbot的 --manual-auth-hook
cert_aliyun_dns_hook.sh clean # clean 参数用于certbot的 --manual-cleanup-hook
```

1 自定义脚本变量

``` bash
# 临时保存新增/修改的dns记录 recordId
ID_FILE="/tmp/cert-hook-dns-record-id.tmp"
# 临时保存dns解析记录
DNS_FILE="/tmp/cert-hook-dns-record-info.tmp"
# aliyun命令的区域，默认为cn-hangzhou
REGION="cn-hangzhou"

```

2 申请证书

``` bash
# hook脚本需要有执行权限
chmod +x /path/to/cert_aliyun_dns_hook.sh

# 首次申请证书
certbot certonly --manual --preferred-challenges=dns --manual-auth-hook "/path/to/cert_aliyun_dns_hook.sh auth" --manual-cleanup-hook "/path/to/cert_aliyun_dns_hook.sh clean" -d <example.com> -d <*.example.com>

# 到期重新申请证书
certbot renew --manual --preferred-challenges=dns  --manual-auth-hook "/path/to/cert_aliyun_dns_hook.sh auth" --manual-cleanup-hook "/path/to/cert_aliyun_dns_hook.sh clean" --deploy-hook  "systemctl restart nginx"
```

3 通常第一次执行会dns验证失败，再执行一次就可以验证成功，生成的证书位于 `/etc/letsencrypt/live/<example.com>/` 目录下。
