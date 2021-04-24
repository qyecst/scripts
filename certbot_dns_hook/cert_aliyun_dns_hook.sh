#!/usr/bin/env bash

# certbot传递的变量 https://certbot.eff.org/docs/using.html#pre-and-post-validation-hooks
# CERTBOT_DOMAIN : The domain being authenticated
# CERTBOT_VALIDATION : The validation string

set -o pipefail

# 临时保存新增/修改的dns记录 recordId
ID_FILE="/tmp/cert-hook-dns-record-id.tmp"
# 临时保存dns解析记录
DNS_FILE="/tmp/cert-hook-dns-record-info.tmp"
# aliyun命令的区域，默认为cn-hangzhou
REGION="cn-hangzhou"

check_env() {
    # 需要安装jq、dig 和 aliyun => https://github.com/aliyun/aliyun-cli
    type jq >/dev/null 2>&1 || { echo 'Need Command `jq`' >&2 && exit 1; }
    type dig >/dev/null 2>&1 || { echo 'Need Command `dig`' >&2 && exit 1; }
    type aliyun >/dev/null 2>&1 || { echo 'Need Command `aliyun`' >&2 && exit 1; }
}

list_dns() {
    # 显示域名的dns记录
    echo "\(.DomainName) \(.Status) \(.Type) \(.RR) \(.Value)" >"$DNS_FILE" &&
        aliyun alidns DescribeDomainRecords --region "$REGION" --DomainName "$CERTBOT_DOMAIN" |
        jq -r '.DomainRecords.Record[]|"\(.DomainName) \(.Status) \(.Type) \(.RR) \(.Value)"' >>"$DNS_FILE" &&
        cat "$DNS_FILE" | sort | column -t && rm -f "$DNS_FILE"
}

check_dns() {
    # 检测dns记录修改是否生效，默认超时1分钟，默认使用8.8.8.8
    for ((i = 0; i < 10; ++i)); do
        if [[ $(dig +noall +answer -t TXT "_acme-challenge.$CERTBOT_DOMAIN" @8.8.8.8 |
            awk '{print $NF}' | jq -r '.') == "$CERTBOT_VALIDATION" ]]; then
            list_dns
            sleep 10
            break
        else
            sleep 6
        fi
    done
}

modify_dns() {
    # 新增/修改dns记录，新增则将recordId记录在$ID_FILE中
    if [[ (-e "$ID_FILE") && (-s "$ID_FILE") ]]; then
        aliyun alidns UpdateDomainRecord --region "$REGION" --RecordId "$(cat "$ID_FILE")" --RR _acme-challenge \
            --Type TXT --Value "$CERTBOT_VALIDATION" &&
            check_dns
    else
        aliyun alidns AddDomainRecord --region "$REGION" --DomainName "$CERTBOT_DOMAIN" --RR _acme-challenge \
            --Type TXT --Value "$CERTBOT_VALIDATION" | jq -r '.RecordId' >"$ID_FILE" &&
            check_dns
    fi
}

delete_dns() {
    # 删除$ID_FILE对应的dns记录
    if [[ (-e "$ID_FILE") && (-s "$ID_FILE") ]]; then
        aliyun alidns DeleteDomainRecord --region "$REGION" --RecordId "$(cat "$ID_FILE")" &&
            rm -f "$ID_FILE" &&
            list_dns
    else
        echo "Already Cleanup"
    fi
}

main() {
    local op="$1"
    case "$op" in
    auth)
        modify_dns
        ;;
    clean)
        delete_dns
        ;;
    *)
        echo "Unknown Options: $op" >&2
        echo "Usage: \`$0 auth\` or \`$0 clean\`" >&2
        ;;
    esac
}

[[ "$0" == "$BASH_SOURCE" ]] && check_env && main "$@"

