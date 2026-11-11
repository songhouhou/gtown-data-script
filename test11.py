# 导出Archery数据到 CSV 文件（含高德省市区解析）
import csv
import time
from datetime import datetime


import requests

# 请替换为实际的请求 URL
URL = "https://archery.g-town.com.cn/query/"
GD_KEY = "50044b6907d26ac10ef274e04daff150"

_cache = {}
_addr_cnt = 0  # 解析进度计数


def _fmt(v):
    """高德部分字段为空时返回[]，统一转成空字符串"""
    return v if isinstance(v, str) else ""


def parse_address(addr):
    """调用高德地理编码解析省市区，返回 (province, city, district, formatted_address)"""
    global _addr_cnt
    if not addr or addr in _cache:
        return _cache.get(addr, ("", "", "", ""))
    _addr_cnt += 1
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在解析第 {_addr_cnt} 个地址: {addr}", flush=True)
    try:
        p = {"address": addr.replace("市辖区", ""), "key": GD_KEY}
        print(p)
        r = requests.get("https://restapi.amap.com/v3/geocode/geo", params=p, timeout=10).json()
        print(r)
        if r.get("status") == "1" and r.get("geocodes"):
            g = r["geocodes"][0]
            _cache[addr] = (_fmt(g.get("province")), _fmt(g.get("city")),
                            _fmt(g.get("district")), _fmt(g.get("formatted_address")))
        else:
            print(f"解析未命中: {addr} -> info={r.get('info')}")
    except Exception as e:
        print(f"解析失败: {addr} -> {e}")
    return _cache.get(addr, ("", "", "", ""))


def main():
    cookie = "csrftoken=XKpFAQqz1osqq88xi2ws0oxRoQ0WNZcY; sessionid=e394b21lle8ai3bcpb87pwyc83j7bl58"
    xCSRFToken = cookie.split("csrftoken=")[1].split(";")[0].strip()

    instance_name = "prod-ob-omp"
    db_name = "omp_order_sec"
    ####末尾不能加;
    ####
    sql = """
SELECT
    t.channel_order_no                                   AS '项目订单号',
    t.order_no                                           AS '订单号',
    t.order_detail_no                                    AS '子订单编号',
    t.channel_order_detail_no                            AS '项目子订单',
    t.channel_name                                       AS '销售项目',
    t.channel_code                                       AS '项目编码',
    t.b2b_order_no                                       AS 'B端订单号',
    t.third_order_no                                     AS '第三方订单号',
    t.refund_no                                          AS '换货关联订单号',
    t.refund_order_no                                    AS '换货关联子订单号',
    t.error_msg                                          AS '错误描述',
    t.channel_sku_code                                   AS '项目商品编号',
    t.brand_name                                         AS '品牌名称',
    t.sku_code                                           AS '商品SKU',
    t.sku_name                                           AS '商品名称',
    t.order_detail_type                                  AS '商品类型',
    t.group_sku_code                                     AS '组合商品SKU',
    t.product_user_name                                  AS '产品经理',
    t.order_status                                       AS '订单状态',
    t.type                                               AS '发货优先级',
    t.refund_num                                         AS '退换货数量',
    t.error_code                                         AS '异常类型',
    t.order_type                                         AS '订单类型',
    t.num                                                AS '数量',
    t.weight                                             AS '重量(克)',
    ROUND(IFNULL(t.price, 0) / 100, 2)                   AS '单价(元)',
    ROUND(IFNULL(t.amount, 0) / 100, 2)                  AS '商品总价(元)',
    ROUND(IFNULL(t.receivable_amount, 0) / 100, 2)       AS '应收总金额(元)',
    ROUND(IFNULL(t.pay_amount, 0) / 100, 2)              AS '个人实付金额(元)',
    ROUND(IFNULL(t.integral, 0) / 100, 2)                AS '积分支付金额(元)',
    ROUND(IFNULL(t.fee_amount, 0) / 100, 2)              AS '佣金金额(元)',
    ROUND(IFNULL(t.bank_discount_amount, 0) / 100, 2)    AS '渠道方补贴(元)',
    ROUND(IFNULL(t.discount_amount, 0) / 100, 2)         AS '公司补贴(元)',
    ROUND(IFNULL(t.national_subsidy_amount, 0) / 100, 2) AS '政府补贴-全国性(元)',
    ROUND(IFNULL(t.city_subsidy_amount, 0) / 100, 2)     AS '政府补贴-地方性(元)',
    ROUND(IFNULL(t.settlement, 0) / 100, 2)              AS '结算总价(元)',
    CASE WHEN t.is_gift = 1 THEN '是' ELSE '否' END      AS '是否赠品',
    t.carrier_name                                       AS '快递公司',
    t.carrier_no                                         AS '物流单号',
    t.express_time                                       AS '发货日期',
    t.warehouse_code                                     AS '仓库编号',
    t.create_time                                        AS '导单时间',
    t.update_time                                        AS '修改时间',
    od.address                                           AS '收货地址',
    IFNULL(o.enterprise_subject_name, '上海海牙湾贸易有限公司') AS '企业主体',
    t.out_no                                             AS '出库单号',
    t.out_detail_no                                      AS '出库明细单号',
    t.pay_time                                           AS '支付完成时间',
    t.remark2                                            AS '客服备注',
    t.remark                                             AS '备注',
    t.sign_type                                          AS '物流完成状态',
    t.channel_sku_installment                            AS '分期数'
FROM omp_order_detail t
LEFT JOIN omp_order od ON t.order_id = od.id
LEFT JOIN omp_order_extra o ON t.order_no = o.order_no
LEFT JOIN omp_order_detail_extra ex ON t.order_detail_no = ex.order_detail_no
WHERE t.channel_code = 'PC000821'
  AND t.create_time >= '2026-11-01 00:00:00'
  AND t.create_time <= '2026-11-30 23:59:59'
  AND t.is_del = 0
ORDER BY t.create_time DESC, t.id DESC
"""
    sql = sql.replace(";", "")
    # 设置请求头
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "Cookie": cookie,
        "X-CSRFToken": xCSRFToken,
        "X-Requested-With": "XMLHttpRequest"
    }

    offset = 0
    # page_size = 20000
    page_size = 1000
    column_has_write = False
    addr_idx = None
    file_name = f"data_export_{db_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"

    with open(file_name, mode='w', newline='', encoding='utf-8') as file_writer:
        csv_writer = csv.writer(file_writer)
        cnt = 1
        while True:
            print(f"正在处理第 {cnt} 页数据...")
            # 构建请求数据
            data = {
                "instance_name": instance_name,
                "db_name": db_name,
                "schema_name": "",
                "tb_name": "",
                "sql_content": f"{sql} LIMIT {page_size} OFFSET {offset};",
                "limit_num": "0"
            }

            # 发送请求
            response = requests.post(URL, headers=headers, data=data)
            response_body = response.json()
            # print(response_body)

            # 解析响应
            data_obj = response_body.get("data")
            # print(data_obj)
            if data_obj is None:
                break

            # print(data_obj)
            column_list = data_obj.get("column_list")
            # print(column_list)
            if not column_has_write:
                addr_idx = column_list.index("收货地址")
                csv_writer.writerow(column_list + ["高德-省", "高德-市", "高德-区", "高德-详细地址"])
                column_has_write = True

            rows = data_obj.get("rows")
            # print(rows)
            if rows is None or not rows:
                break

            # 处理每一行数据
            for row in rows:
                csv_writer.writerow(row + list(parse_address(row[addr_idx])))
                # print(row)

            # 增加偏移量
            offset += page_size
            time.sleep(0.001)
            # break
            cnt += 1


if __name__ == "__main__":
    main()