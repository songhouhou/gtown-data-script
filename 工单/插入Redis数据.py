# 插入Redis数据
# insert_official_account_verify_code
import redis

# Redis配置
redis_client = redis.Redis(
    host='192.168.1.110',
    port=6379,
    password=None,  # 如果有密码，请设置
    db=3,
    decode_responses=True
)

# 配置参数
VERIFY_CODE_PREFIX = "VERIFY_CODE:"
VERIFY_CODE = "888888"
EXPIRE_DAYS = 15

# 测试手机号列表
phone_list = [
    "13123242443",
    "15738668129",
    "13800138002",
    "18360725526",
    "15856975857",
    "15566214314",
    "15821527065",
    "13123242443",
    "13800000000"
]

# 业务类型列表
business_types = [
    "viewKfcQrcode",  # 查看KFC二维码
    "resendCouponPassword",  # 重发卡密
    "createServiceListAfterSaleRemark",  # 创建服务单售后备注
    "queryLogistics"  # 查询物流
]

# 计算过期时间（秒）
expire_seconds = EXPIRE_DAYS * 24 * 3600

# 插入验证码
for phone in phone_list:
    for business_type in business_types:
        key = f"{VERIFY_CODE_PREFIX}{phone}:{business_type}"
        try:
            redis_client.setex(
                name=key,
                time=expire_seconds,
                value=VERIFY_CODE
            )
            print(f"设置成功 - 手机号: {phone}, 业务类型: {business_type}, 验证码: {VERIFY_CODE}")
        except Exception as e:
            print(f"设置失败 - 手机号: {phone}, 业务类型: {business_type}")
            print(f"错误信息: {str(e)}")

# 关闭连接
redis_client.close()
