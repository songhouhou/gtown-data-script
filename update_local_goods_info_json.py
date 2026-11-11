# 更新本地商品信息json
import json

# ====================== 配置区 ======================
# 本地JSON文件路径
JSON_FILE_PATH = r"D:\dy-img\dou_yin_picking_cart.json"
# 浏览器复制下来的完整JSON粘贴此处
browser_new_data = {}
# 【可自定义】只更新以下字段，其他字段保留本地原有值
update_target_fields = ["price", "cos_fee", "cos_ratio"]


# ====================================================

def partial_update_cart_json():
    # 读取本地文件
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        print(f"✅ 成功读取本地文件，本地现有商品总数：{len(local_data)}")
    except FileNotFoundError:
        print("⚠️ 本地文件不存在，将创建全新文件")
        local_data = {}
    except json.JSONDecodeError:
        print("❌ 本地JSON格式损坏，清空重新创建")
        local_data = {}

    update_count = 0
    match_count = 0

    # 逐条遍历浏览器抓取到的商品
    for goods_id, browser_item in browser_new_data.items():
        print(f"\n---------- 商品ID: {goods_id} ----------")
        if goods_id in local_data:
            match_count += 1
            print(f"✅ 本地匹配到此goods_id")
            local_item = local_data[goods_id]
            need_update = False
            # 逐个对比指定字段，不一致则更新
            for field in update_target_fields:
                if field in browser_item and local_item.get(field) != browser_item[field]:
                    local_item[field] = browser_item[field]
                    need_update = True
                    print(f"  更新字段 {field}: {local_item[field]}")
            if need_update:
                update_count += 1
                print(f"👉 本条商品已完成字段更新")
            else:
                print(f"⏭️ 指定字段无变化，跳过更新")
        else:
            print(f"❌ 本地无此goods_id")

    # 写回文件
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(local_data, f, ensure_ascii=False, indent=4)

    # 汇总统计
    print("\n==================== 处理完成汇总 ====================")
    print(f"本地匹配商品数量：{match_count}")
    print(f"执行字段更新商品数：{update_count}")
    print(f"更新后本地总商品数：{len(local_data)}")
    print(f"文件已保存至：{JSON_FILE_PATH}")


if __name__ == "__main__":
    partial_update_cart_json()
