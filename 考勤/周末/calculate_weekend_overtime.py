"""
@desc: Moka周末加班时长计算脚本
@date: 2026-02-10

功能说明：
    读取Excel文件中的员工打卡记录，根据特定规则计算周末加班时长，
    并将结果输出到新的Excel文件中。
依赖库安装：
    pip install pandas
    pip install openpyxl
使用方法：
    python calculate_weekend_overtime.py
输入文件格式：
    部门  员工  上班打卡时间  下班打卡时间
    运营二组  小明  2026-01-31 14:17:00 2026-01-31 16:24:00
输出文件格式：
    id  姓名  开始时间  结束时间  上午时间段  上午时长  下午时间段  下午时长  晚上时间段  晚上时长  加班时长
    1   小明  2026-01-31 14:17:00  2026-01-31 16:24:00  14:00-16:00  2.0  16:00-16:30  0.5  ""  0  2.5
"""

import pandas as pd
import datetime
from datetime import time

def round_up_to_half_hour(dt):
    """
    将时间向上取整到最近的0分或30分
    参数:
        dt: datetime对象，表示需要取整的时间
    返回:
        取整后的datetime对象
    示例:
        9:00  -> 9:00
        9:05  -> 9:30
        9:30  -> 9:30
        9:31  -> 10:00
    """
    minutes = dt.minute  # 获取当前时间的分钟数
    if minutes == 0:  # 如果正好是整点，保持不变
        return dt.replace(minute=0, second=0, microsecond=0)
    elif minutes <= 30:  # 如果分钟数在1-30之间，向上取整到30分
        return dt.replace(minute=30, second=0, microsecond=0)
    else:  # 如果分钟数在31-59之间，向上取整到下一小时的整点
        return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

def round_down_to_half_hour(dt):
    """
    将时间向下取整到最近的0分或30分
    参数:
        dt: datetime对象，表示需要取整的时间
    返回:
        取整后的datetime对象
    示例:
        9:00  -> 9:00
        9:05  -> 9:00
        9:30  -> 9:30
        9:31  -> 9:30
    """
    minutes = dt.minute  # 获取当前时间的分钟数
    if minutes == 0:  # 如果正好是整点，保持不变
        return dt.replace(minute=0, second=0, microsecond=0)
    elif minutes < 30:  # 如果分钟数在1-29之间，向下取整到整点
        return dt.replace(minute=0, second=0, microsecond=0)
    else:  # 如果分钟数在30-59之间，向下取整到30分
        return dt.replace(minute=30, second=0, microsecond=0)

def calculate_daytime_hours(start_dt, end_dt):
    """
    计算白天加班时长（18:00之前），扣除午休时间
    参数:
        start_dt: datetime对象，开始时间
        end_dt: datetime对象，结束时间
    返回:
        dict: 包含时间段和时长信息的字典
            - morning_hours: 上午加班时长（小时）
            - afternoon_hours: 下午加班时长（小时）
            - total_hours: 白天总加班时长（小时）
            - morning_range: 上午时间段字符串
            - afternoon_range: 下午时间段字符串
            - start_rounded: 取整后的开始时间
            - end_rounded: 取整后的结束时间
    规则:
        - 只统计18:00之前的时间
        - 扣除午休时间：12:30-13:30
        - 时间已经过取整处理，直接计算
    示例:
        9:30-18:00 -> 上午3小时，下午4.5小时，总计7.5小时
        10:00-18:00 -> 上午2.5小时，下午4.5小时，总计7小时
        14:00-18:00 -> 上午0小时，下午4小时，总计4小时
    """
    start_rounded = round_up_to_half_hour(start_dt)  # 开始时间向上取整
    end_rounded = round_down_to_half_hour(end_dt)  # 结束时间向下取整
    
    lunch_start = time(12, 30)  # 午休开始时间
    lunch_end = time(13, 30)  # 午休结束时间
    cutoff_time = time(18, 0)  # 白天加班截止时间
    
    # 如果开始时间 >= 18:00，直接返回0（无白天加班）
    if start_rounded.time() >= cutoff_time:
        return {
            'morning_hours': 0.0,
            'afternoon_hours': 0.0,
            'total_hours': 0.0,
            'morning_range': '',
            'afternoon_range': '',
            'start_rounded': start_rounded,
            'end_rounded': end_rounded
        }
    
    # 检查时间有效性：如果取整后的开始时间 >= 结束时间，直接返回0
    if start_rounded >= end_rounded:
        return {
            'morning_hours': 0.0,
            'afternoon_hours': 0.0,
            'total_hours': 0.0,
            'morning_range': '',
            'afternoon_range': '',
            'start_rounded': start_rounded,
            'end_rounded': end_rounded
        }
    
    end_time = end_rounded.time()  # 获取结束时间部分
    if end_time > cutoff_time:  # 如果结束时间超过18:00，则截断到18:00
        end_rounded = end_rounded.replace(hour=18, minute=0, second=0, microsecond=0)
    
    start_time = start_rounded.time()  # 获取开始时间部分
    end_time = end_rounded.time()  # 获取结束时间部分
    
    morning_hours = 0.0  # 上午加班时长
    afternoon_hours = 0.0  # 下午加班时长
    morning_range = ""  # 上午时间段
    afternoon_range = ""  # 下午时间段
    
    if start_time >= lunch_end or end_time <= lunch_start:  # 不包含午休时间
        total_minutes = int((end_rounded - start_rounded).total_seconds() / 60)  # 直接计算时长
        total_hours = total_minutes / 60
        
        if start_time >= lunch_end:  # 纯下午加班
            afternoon_hours = total_hours
            afternoon_range = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        else:  # 纯上午加班
            morning_hours = total_hours
            morning_range = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
    else:  # 包含午休时间，拆成两段计算
        morning_end = start_rounded.replace(hour=12, minute=30, second=0, microsecond=0)  # 上午结束时间
        afternoon_start = start_rounded.replace(hour=13, minute=30, second=0, microsecond=0)  # 下午开始时间
        
        morning_minutes = int((morning_end - start_rounded).total_seconds() / 60)  # 上午时长
        afternoon_minutes = int((end_rounded - afternoon_start).total_seconds() / 60)  # 下午时长
        
        # 检查时长是否为负数，如果为负数则设为0
        if morning_minutes < 0:
            morning_minutes = 0
        if afternoon_minutes < 0:
            afternoon_minutes = 0
        
        morning_hours = morning_minutes / 60  # 转换为小时
        afternoon_hours = afternoon_minutes / 60  # 转换为小时
        
        # 只有当时长 > 0 时，才生成时间段字符串
        if morning_hours > 0:
            morning_range = f"{start_time.strftime('%H:%M')}-12:30"  # 上午时间段
        else:
            morning_range = ""
        
        if afternoon_hours > 0:
            afternoon_range = f"13:30-{end_time.strftime('%H:%M')}"  # 下午时间段
        else:
            afternoon_range = ""
    
    total_hours = morning_hours + afternoon_hours  # 总时长
    
    return {
        'morning_hours': morning_hours,
        'afternoon_hours': afternoon_hours,
        'total_hours': total_hours,
        'morning_range': morning_range,
        'afternoon_range': afternoon_range,
        'start_rounded': start_rounded,
        'end_rounded': end_rounded
    }

def calculate_night_overtime(end_dt):
    """
    计算20:00之后的加班时长
    参数:
        end_dt: datetime对象，下班时间
    返回:
        dict: 包含晚上加班时长和时间段信息的字典
            - hours: 晚上加班时长（小时）
            - range: 晚上加班时间段字符串
    规则:
        - 20:00起算，基准1小时
        - 每增加半小时，加班时长增加0.5小时
        - 20:00 -> 1.0小时
        - 20:30 -> 1.5小时
        - 21:00 -> 2.0小时
        - 21:30 -> 2.5小时
        - 以此类推
    示例:
        19:30 -> 0.0小时（未到20:00）
        20:00 -> 1.0小时，时间段：20:00-20:00
        20:15 -> 1.0小时，时间段：20:00-20:00（向下取整）
        20:30 -> 1.5小时，时间段：20:00-20:30
        21:45 -> 2.5小时，时间段：20:00-21:30
    """
    end_time = end_dt.time()  # 提取下班时间
    base_time = time(20, 0)  # 加班起算基准时间：20:00
    
    if end_time < base_time:  # 如果下班时间早于20:00，无晚上加班
        return {
            'hours': 0.0,
            'range': ""
        }
    
    total_minutes = end_time.hour * 60 + end_time.minute  # 将下班时间转换为总分钟数
    base_minutes = 20 * 60  # 20:00转换为分钟数：1200分钟
    overtime_minutes = total_minutes - base_minutes  # 计算超出20:00的分钟数
    
    overtime_hours = 1.0 + (overtime_minutes // 30) * 0.5  # 计算加班时长：基准1小时 + 每半小时加0.5小时
    
    # 计算实际结束时间（向下取整到最近的30分钟）
    actual_end_minutes = base_minutes + (overtime_minutes // 30) * 30
    actual_end_hour = actual_end_minutes // 60
    actual_end_minute = actual_end_minutes % 60
    night_range = f"20:00-{actual_end_hour:02d}:{actual_end_minute:02d}"  # 晚上加班时间段
    
    return {
        'hours': overtime_hours,
        'range': night_range
    }

def process_excel(input_file):
    """
    处理Excel文件，计算每条记录的加班时长
    参数:
        input_file: str，输入Excel文件路径
    返回:
        None，结果直接写入Excel文件
    流程:
        1. 读取Excel文件
        2. 遍历每一行，提取员工姓名、开始时间、结束时间
        3. 检查是否跨天，跨天则加班时长为None
        4. 计算白天加班时长（扣除午休）
        5. 计算20:00之后的加班时长
        6. 汇总总加班时长
        7. 将结果写入新的Excel文件
    异常处理:
        - 如果解析时间失败，加班时长设为None
        - 跨天加班，加班时长设为None并打印特殊日志
    """
    df = pd.read_excel(input_file)  # 读取Excel文件
    
    results = []
    for idx, row in df.iterrows():
        name = row['员工']
        start_time_str = row['上班打卡时间']
        end_time_str = row['下班打卡时间']
        
        try:
            start_dt = pd.to_datetime(start_time_str)
            end_dt = pd.to_datetime(end_time_str)
            
            if start_dt.date() != end_dt.date():  # 检查是否跨天
                print(f"特殊日志: {name} 跨天加班 开始时间: {start_time_str} 结束时间: {end_time_str}")
                results.append({  # 跨天加班，加班时长设为None
                    'id': idx + 1,
                    '姓名': name,
                    '开始时间': start_time_str,
                    '结束时间': end_time_str,
                    '上午时间段': None,
                    '上午时长': None,
                    '下午时间段': None,
                    '下午时长': None,
                    '晚上时间段': None,
                    '晚上时长': None,
                    '加班时长': None
                })
                continue
            
            work_hours = calculate_daytime_hours(start_dt, end_dt)  # 计算白天加班时长（扣除午休）
            night_overtime = calculate_night_overtime(end_dt)  # 计算20:00之后的加班时长
            total_overtime = work_hours['total_hours'] + night_overtime['hours']  # 计算总加班时长
            
            results.append({
                'id': idx + 1,
                '姓名': name,
                '开始时间': start_time_str,
                '结束时间': end_time_str,
                '上午时间段': work_hours['morning_range'],
                '上午时长': work_hours['morning_hours'],
                '下午时间段': work_hours['afternoon_range'],
                '下午时长': work_hours['afternoon_hours'],
                '晚上时间段': night_overtime['range'],
                '晚上时长': night_overtime['hours'],
                '加班时长': total_overtime
            })
            
            print(f"已处理: {name} {start_time_str} - {end_time_str}")
            print(f"  取整时间: {work_hours['start_rounded'].strftime('%H:%M')} - {work_hours['end_rounded'].strftime('%H:%M')}")
            if work_hours['morning_range']:
                print(f"  上午: {work_hours['morning_range']}, 时长: {work_hours['morning_hours']}h")
            if work_hours['afternoon_range']:
                print(f"  下午: {work_hours['afternoon_range']}, 时长: {work_hours['afternoon_hours']}h")
            if night_overtime['range']:
                print(f"  晚上: {night_overtime['range']}, 时长: {night_overtime['hours']}h")
            print(f"  总加班时长: {total_overtime}h")
            
        except Exception as e:  # 异常处理
            print(f"处理失败: {name} {start_time_str} - {end_time_str} 错误: {str(e)}")
            results.append({  # 处理失败，加班时长设为None
                'id': idx + 1,
                '姓名': name,
                '开始时间': start_time_str,
                '结束时间': end_time_str,
                '上午时间段': None,
                '上午时长': None,
                '下午时间段': None,
                '下午时长': None,
                '晚上时间段': None,
                '晚上时长': None,
                '加班时长': None
            })
    
    result_df = pd.DataFrame(results)
    output_file = f"周末加班时长_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"  # 生成输出文件名（包含时间戳）
    result_df.to_excel(output_file, index=False)  # 将结果写入Excel文件（不包含索引列）
    print(f"\n处理完成！结果已写入 {output_file}")

if __name__ == "__main__":
    """
    主程序入口
    整体流程:
        1. 指定输入Excel文件路径（默认为"周末.xlsx"）
        2. 调用process_excel函数处理文件
        3. 读取Excel中的打卡记录
        4. 对每条记录计算加班时长
        5. 输出结果到新的Excel文件（文件名包含时间戳）
    加班时长计算规则:
        规则0: 9:00上班，18:00下班
        
        规则1: 扣除休息时间
            - 午休：12:30-13:30
            - 晚饭：18:00-20:00
        
        规则2: 按整点计算（开始时间向上取最近的0分/30分，结束时间向下取最近的0分/30分）
            - 示例1: 9:05-18:05，按9:30-18:00计算，扣除12:30-13:30，实际为7.5小时
            - 示例2: 9:40-19:30，按10:00-18:00计算，扣除12:30-13:30及18:00-19:00，实际为7小时
        
        规则3: 20:00之后的加班时长计算
            - >=20:00 且 <20:30，则加1小时
            - >=20:30 且 <21:00，则加1.5小时
            - >=21:00 且 <21:30，则加2小时
            - >=21:30 且 <22:00，则加2.5小时
            - 以此类推，即20:00加1h，每增加半小时加0.5h
        
        规则4: 跨天加班处理
            - 如果开始时间和结束时间不在同一天，说明跨天加班
            - 加班时长设为None，并打印特殊日志
        
        规则5: 输出格式
            - 文件名：周末加班时长_yyyy-MM-dd-HH-MM-ss.xlsx
            - 列格式：id(自增) | 姓名 | 开始时间 | 结束时间 | 上午时间段 | 上午时长 | 下午时间段 | 下午时长 | 晚上时间段 | 晚上时长 | 加班时长
    """
    input_file = "/周末加班测试用例_最终版.xlsx"
    process_excel(input_file)