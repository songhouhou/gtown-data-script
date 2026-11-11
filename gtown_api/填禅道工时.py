# 自动填写禅道工时
# @date: 2026-04-15
import datetime
import re
from datetime import timedelta
import time

import requests

# ====================== 【只需配置这里】 ======================
# 禅道任务url
TASK_VIEW_URL = "https://gtpms.g-town.com.cn/biz/task-view-29052.html"
# 开始日期
START_DATE = "2026-03-23"
# 总工时
TOTAL_WORK_HOUR = 40
# Cookie
cookie_str = """lang=zh-cn; device=desktop; keepLogin=on; za=houhou.song; preProductID=11; lastProduct=11; theme=default; preExecutionID=4141; storyPreExecutionID=4141; preTaskID=1639; preBranch=0; ajax_lastNext=on; zentaosid=76ebb3b86a5002b6efea67609c4c7653; moduleBrowseParam=0; productBrowseParam=0; zp=ff43e233509cd92ef7094263f585bf4f832b15ee; tab=execution; executionStoryOrder=order_desc; lastTaskModule=802; executionTaskOrder=id_desc; recordEstimateType=null; windowWidth=900; windowHeight=204"""
# 工时备注
WORK_DESC = "OMS日清日结检查单"
# 提交间隔秒数
SLEEP_SECONDS = 0.2
# ==============================================================

# ====================== 自动解析任务ID ======================
match = re.search(r"task-view-(\d+)", TASK_VIEW_URL)
if not match:
    print("❌ 未能从URL中解析出任务ID，程序退出")
    exit()

task_id = match.group(1).strip()
if not task_id:
    print("❌ 任务ID为空，程序退出")
    exit()

# 自动构造提交工时的 URL
EFFORT_URL = f"https://gtpms.g-town.com.cn/biz/effort-createForObject-task-{task_id}--.html?onlybody=yes"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://gtpms.g-town.com.cn",
    "referer": "https://gtpms.g-town.com.cn/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Cookie": cookie_str
}

# ====================== 生成工作日（跳过周末） ======================
task_list = []
current_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
left_hour = TOTAL_WORK_HOUR

# 只生成到工时用完为止，不生成多余日期
while left_hour > 0:
    # 跳过周末
    if current_date.weekday() not in (5, 6):
        consume = 8

        if left_hour - consume < 0:
            break

        left_hour -= consume

        task_list.append({
            "day": current_date.strftime("%Y-%m-%d"),
            "consumed": 8,
            "left": left_hour
        })

    # 下一天
    current_date += timedelta(days=1)

# ====================== 无数据判断 ======================
if not task_list:
    print("❌ 没有可提交的工时，请检查总工时/开始日期")
    exit()

# ====================== 预览 ======================
print("=" * 70)
print(f"📋 任务ID：{task_id}")
print(f"📋 总工时：{TOTAL_WORK_HOUR}h")
print("📋 将要提交的工时清单：")
print("=" * 70)
for i, item in enumerate(task_list, 1):
    print(f"第{i}天 | {item['day']} | 耗时：8h | 剩余：{item['left']}h")
print("=" * 70)

# ====================== 确认提交 ======================
confirm = input("✅ 输入 yes 一次性全部提交，其他退出：").strip().lower()
if confirm != "yes":
    print("🚫 已取消提交")
    exit()

# ====================== 批量提交 ======================
print("\n🚀 开始提交...\n")
for item in task_list:
    data = {
        f"id[1]": 1,
        f"dates[1]": item['day'],
        f"objectType[1]": "task",
        f"objectID[1]": task_id,
        f"work[1]": WORK_DESC,
        f"consumed[1]": 8,
        f"left[1]": item['left']
    }
    # print(f"data: {data}")
    try:
        res = requests.post(EFFORT_URL, headers=headers, data=data, timeout=10)
        print(f"✅ {item['day']} 提交成功 | 状态码：{res.status_code}")
    except Exception as e:
        print(f"❌ {item['day']} 提交失败：{str(e)}")

    # 提交后等待
    time.sleep(SLEEP_SECONDS)

print("\n🎉 所有工时提交完成！")