# 调用moka考勤计算加班时长
# 获取指定年月的考勤记录，并计算加班时长
# @date: 2026-01-07
# @author: houhou.song
import datetime
import json
import time

import requests

url = "https://core.mokahr.com/api/abs/attendance/myAttendance/v2/m/detail?bus=20"

# 登录配置
# 参数
employee_id = 1169399
# 你的邮箱密码
LOGIN_EMAIL = "houhou.song@g-town.com.cn"
LOGIN_PASSWORD = "fcs8pw|M_!KIG3h,"

target_year = 2026
target_month = 5

# 法定工作日日期
LEGAL_WORKDAYS = ['2026-01-04', '2026-02-14', '2026-02-28', '2026-05-09', '2026-09-20', '2026-10-10']

# 请求头
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://core.mokahr.com',
    'priority': 'u=1, i',
    'referer': 'https://core.mokahr.com/attendance',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'content-type': 'application/json'
}


# 自动获取 cookie
def get_cookie():
    login_url = "https://passport.mokahr.com/api/outer/moka-unified-account/mokaUid/login"
    payload1 = {"isMobile": False, "bus": 20, "email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}

    res1 = requests.post(login_url, json=payload1, headers=headers).json()
    print(res1)
    data = res1["data"]

    if "rid" in data:
        payload2 = {**payload1, "force": True, "rid": data["rid"]}
        res2 = requests.post(login_url, json=payload2, headers=headers).json()
        print(res2)
        data = res2["data"]

    ticket = data["ticket"]
    uni_url = "https://core.mokahr.com/api/outer/moka-unified-account/mokaUid/uniLogin?bus=20"
    res2 = requests.post(uni_url, json={"loginType": "10", "bus": 20, "ticket": ticket, "isMobile": False},
                         headers=headers).json()
    print(res2)
    jwt = res2["data"]["moka-jwt"]
    uid = res2["data"]["moka-uid"]
    return f"moka-jwt={jwt}; moka-uid={uid}"


# 自动获取
cookie = get_cookie()
headers["Cookie"] = cookie


# 计算指定年月的天数
def get_days_in_month(year, month):
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    return (datetime.date(next_year, next_month, 1) - datetime.date(year, month, 1)).days


# 判断是否为周末（法定工作日不算）
def is_weekend(year, month, day, date_str):
    if date_str in LEGAL_WORKDAYS:
        return False
    w = datetime.date(year, month, day).weekday()
    return w == 5 or w == 6  # 5=周六,6=周日


# 上班时间向上取整30分钟
def round_up_30(h, m):
    total = h * 60 + m
    rem = total % 30
    return total if rem == 0 else total + (30 - rem)


# 下班时间向下取整30分钟
def round_down_30(h, m):
    total = h * 60 + m
    return total - (total % 30)


# 工作日加班
def calculate_weekday_overtime(time_str):
    if not time_str:
        return 0.0
    try:
        h, m = map(int, time_str.split(':'))
        total = h * 60 + m
        base = 20 * 60
        ot = total - base
        if ot < 0:
            return 0.0
        hours = 1.0 + (ot // 30) * 0.5
        return round(hours, 1)
    except:
        return 0.0


# 周末加班
def calculate_weekend_overtime(in_str, out_str):
    if not in_str or not out_str:
        return 0.0
    try:
        ih, im = map(int, in_str.split(':'))
        oh, om = map(int, out_str.split(':'))
        i_total = round_up_30(ih, im)
        o_total = round_down_30(oh, om)

        LUNCH_START = 12 * 60 + 30
        LUNCH_END = 13 * 60 + 30
        DINNER_START = 18 * 60
        DINNER_END = 19 * 60

        work = o_total - i_total
        if work <= 0:
            return 0.0

        if i_total < LUNCH_END and o_total > LUNCH_START:
            s = max(i_total, LUNCH_START)
            e = min(o_total, LUNCH_END)
            work -= (e - s)

        if i_total < DINNER_END and o_total > DINNER_START:
            s = max(i_total, DINNER_START)
            e = min(o_total, DINNER_END)
            work -= (e - s)

        if work <= 0:
            return 0.0
        hours = (work // 30) * 0.5
        return round(hours, 1)
    except:
        return 0.0


days_in_month = get_days_in_month(target_year, target_month)
today = datetime.date.today()

# 打开文件准备写入
with open('my_attendance_records.txt', 'w', encoding='utf-8') as f:
    total_weekday_ot = 0.0
    total_weekend_ot = 0.0

    # 遍历每一天（只到今天）
    max_day = min(days_in_month, today.day)
    for day in range(1, max_day + 1):
        current_date = datetime.date(target_year, target_month, day)
        date_str = current_date.strftime("%Y-%m-%d")

        payload = json.dumps({
            "loginType": "10",
            "year": target_year,
            "month": target_month,
            "startDate": date_str,
            "endDate": date_str,
            "fieldVisiblePageEnum": "VISIBLE_DAY",
            "employeeId": employee_id
        })

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response_data = response.json()
            # print(response_data)

            if response_data.get('code') == 200:
                detail = response_data.get('data', {}).get('detail', {})
                clock_info = detail.get('myAttendanceAttendanceRecord#clockInAndOutTime', {})
                field_value = clock_info.get('fieldValue', [])

                clock_in_time = ""
                clock_out_time = ""
                ot = 0.0
                weekend_day = is_weekend(target_year, target_month, day, date_str)

                if field_value and field_value[0]:
                    clock_in = field_value[0].get('clockInTime', '')
                    clock_out = field_value[0].get('clockOutTime', '')
                    clock_in_time = clock_in.split(' ')[1] if ' ' in clock_in else ''
                    clock_out_time = clock_out.split(' ')[1] if ' ' in clock_out else ''

                    if weekend_day:
                        ot = calculate_weekend_overtime(clock_in_time, clock_out_time)
                        total_weekend_ot += ot
                    else:
                        ot = calculate_weekday_overtime(clock_out_time)
                        total_weekday_ot += ot

                day_type = "周末" if weekend_day else "工作日"
                if clock_out_time:
                    line = f"{date_str} [{day_type}] | 上班: {clock_in_time or '无'} | 下班: {clock_out_time} | 加班: {ot if ot > 0 else '无'}h\n"
                    print(f"已处理: {date_str} [{day_type}] 上班:{clock_in_time or '无'} 下班:{clock_out_time} 加班:{ot}h")
                else:
                    line = f"{date_str} [{day_type}] | 无打卡记录\n"
                    print(f"已处理: {date_str} [{day_type}] 无打卡记录")

                f.write(line)
            else:
                print(f"请求失败 {date_str}: {response_data.get('msg')}")

        except Exception as e:
            print(f"处理失败 {date_str}: {str(e)}")

        time.sleep(0.1)

    total = total_weekday_ot + total_weekend_ot
    print("\n" + "=" * 50)
    print(f"📊 {target_year}年{target_month}月 考勤汇总")
    print(f"工作日加班: {total_weekday_ot:.1f}h")
    print(f"周末加班: {total_weekend_ot:.1f}h")
    print(f"总计: {total:.1f}h")
    print("=" * 50)

print("\n处理完成！记录已保存到 my_attendance_records.txt")
