# 更新订单时间和供应商商品编码
# update_order_time_and_supplier_item_code
import pymysql
import datetime

# 数据库连接配置
config = {
    'host': '192.168.1.82',
    'user': 'gtown',
    'password': 'Gtown123!QA',
    'database': 'fms_order',
    'charset': 'utf8mb4'
}

# 要修改的日期范围
# date_ranges = [
#     (datetime.datetime(2025, 5, 1), datetime.datetime(2025, 5, 7)),
#     (datetime.datetime(2025, 4, 1), datetime.datetime(2025, 4, 30)),
#     (datetime.datetime(2025, 3, 1), datetime.datetime(2025, 3, 31)),
#     (datetime.datetime(2024, 5, 1), datetime.datetime(2024, 5, 31)),
#     (datetime.datetime(2024, 4, 1), datetime.datetime(2024, 4, 30)),
#     (datetime.datetime(2024, 3, 1), datetime.datetime(2024, 3, 31))
# ][::-1]


date_ranges = [
  (datetime.datetime(2025, 5, 1), datetime.datetime(2025, 5, 7)),
  (datetime.datetime(2025, 4, 1), datetime.datetime(2025, 4, 30)),
  (datetime.datetime(2025, 3, 1), datetime.datetime(2025, 3, 31)),
  (datetime.datetime(2024, 5, 1), datetime.datetime(2024, 5, 31)),
  (datetime.datetime(2024, 4, 1), datetime.datetime(2024, 4, 30)),
  (datetime.datetime(2024, 3, 1), datetime.datetime(2024, 3, 31))
]

# 要修改的supplier_item_code列表
supplier_item_codes = ['GYSI12465','GYSI12468','GYSI12556','GYSI12549','GYSI12547','GYSI12545','GYSI12543','GYSI12540','GYSI12538','GYSI12537','GYSI12527','GYSI12521','GYSI12517','GYSI12513','GYSI12510','GYSI12502','GYSI12500','GYSI12499','GYSI12496','GYSI12493','GYSI12491','GYSI12483','GYSI12477','GYSI12475','GYSI12470','GYSI12592','GYSI12573','GYSI12571','GYSI12569','GYSI12566','GYSI12561','GYSI12558','GYSI12591','GYSI12590','GYSI12589','GYSI12588','GYSI12587','GYSI12586','GYSI12585','GYSI12584','GYSI12583','GYSI12582','GYSI12581','GYSI12580','GYSI12579','GYSI12578','GYSI12577','GYSI12576','GYSI12574','GYSI12575','GYSI12572','GYSI12570','GYSI12568','GYSI12567','GYSI12565','GYSI12564','GYSI12563','GYSI12562','GYSI12560','GYSI12559','GYSI12557','GYSI12555','GYSI12554','GYSI12553','GYSI12552','GYSI12551','GYSI12550','GYSI12548','GYSI12546','GYSI12544','GYSI12542','GYSI12541','GYSI12539','GYSI12536','GYSI12535','GYSI12534','GYSI12533','GYSI12530','GYSI12529','GYSI12528','GYSI12526','GYSI12525','GYSI12524','GYSI12523','GYSI12522','GYSI12520','GYSI12519','GYSI12518','GYSI12516','GYSI12515','GYSI12514','GYSI12512','GYSI12511','GYSI12509','GYSI12508','GYSI12507','GYSI12506','GYSI12505','GYSI12504','GYSI12503','GYSI12501','GYSI12498','GYSI12497','GYSI12495','GYSI12494','GYSI12490','GYSI12492','GYSI12489','GYSI12488','GYSI12487','GYSI12486','GYSI12485','GYSI12484','GYSI12482','GYSI12480','GYSI12481','GYSI12479','GYSI12478','GYSI12476','GYSI12474','GYSI12472','GYSI12473','GYSI12471','GYSI12469','GYSI12466','GYSI12467','GYSI12464','GYSI12462','GYSI12463','GYSI12461','GYSI12460','GYSI12459','GYSI12458','GYSI12457','GYSI12456','GYSI12454','GYSI12453','GYSI12452','GYSI12451','GYSI12450','GYSI12449','GYSI12448','GYSI12447','GYSI12446','GYSI12445','GYSI12444','GYSI12443','GYSI12442','GYSI12441','GYSI12440','GYSI12439','GYSI12438','GYSI12437','GYSI12436','GYSI12435','GYSI12433','GYSI12434','GYSI12429','GYSI12430','GYSI12428','GYSI12427','GYSI12426','GYSI12425','GYSI12424','GYSI12423','GYSI12421','GYSI12422','GYSI12420','GYSI12419','GYSI12418','GYSI12417','GYSI12416','GYSI12415','GYSI12414','GYSI12413','GYSI12412','GYSI12411','GYSI12410','GYSI12409','GYSI12408','GYSI12407','GYSI12406','GYSI12403','GYSI12402','GYSI12401','GYSI12400','GYSI12399','GYSI12398','GYSI12397','GYSI12396','GYSI12395','GYSI12394','GYSI12393','GYSI12392','GYSI12391','GYSI12390','GYSI12389','GYSI12388','GYSI12387','GYSI12386','GYSI12385','GYSI12384','GYSI12383','GYSI12382','GYSI12381','GYSI12380','GYSI12379','GYSI12378','GYSI12377','GYSI12376','GYSI12375','GYSI12374','GYSI12373','GYSI12372','GYSI12370','GYSI12369','GYSI12368','GYSI12367','GYSI12366','GYSI12365','GYSI12364','GYSI12363','GYSI12362','GYSI12361','GYSI12360','GYSI12359','GYSI12358','GYSI12357','GYSI12356','GYSI12355','GYSI12354','GYSI12353','GYSI12352','GYSI12351','GYSI12350','GYSI12349','GYSI12348','GYSI12347','GYSI12346','GYSI12345','GYSI12344','GYSI12343','GYSI12342','GYSI12341','GYSI12340','GYSI12339','GYSI12338','GYSI12337','GYSI12336','GYSI12335','GYSI12334','GYSI12333','GYSI12332','GYSI12331','GYSI12330','GYSI12329','GYSI12328','GYSI12327','GYSI12326','GYSI12325','GYSI12322','GYSI12321','GYSI12320','GYSI12319','GYSI12318','GYSI12317','GYSI12316','GYSI12315','GYSI12314','GYSI12313','GYSI12312','GYSI12311','GYSI12310','GYSI12307','GYSI12306','GYSI12305','GYSI12304','GYSI12303','GYSI12302','GYSI12301','GYSI12300','GYSI12299','GYSI12298','GYSI12297','GYSI12296','GYSI12295','GYSI12294','GYSI12293','GYSI12292','GYSI12291','GYSI12289','GYSI12287','GYSI12286','GYSI12285','GYSI12284','GYSI12283','GYSI12282','GYSI12281','GYSI12280','GYSI12279','GYSI12278','GYSI12277','GYSI12274','GYSI12273','GYSI12272','GYSI12271','GYSI12270','GYSI12269','GYSI12268','GYSI12267','GYSI12266','GYSI12265','GYSI12264','GYSI12263','GYSI12262','GYSI12261','GYSI12260','GYSI12259','GYSI12258','GYSI12256','GYSI12255','GYSI12254','GYSI12253','GYSI12252','GYSI12251','GYSI12250','GYSI12249','GYSI12248','GYSI12247','GYSI12246','GYSI12245','GYSI12244','GYSI12243','GYSI12242','GYSI12241','GYSI12240','GYSI12136','GYSI12238','GYSI12237','GYSI12236','GYSI12235','GYSI12234','GYSI12233','GYSI12232','GYSI12231','GYSI12230','GYSI12229','GYSI12228','GYSI12227','GYSI12226','GYSI12225','GYSI12224','GYSI12223','GYSI12222','GYSI12221','GYSI12220','GYSI12219','GYSI12218','GYSI12217','GYSI12216','GYSI12215','GYSI12214','GYSI12213','GYSI12212','GYSI12211','GYSI12210','GYSI12209','GYSI12208','GYSI12207','GYSI12206','GYSI12205','GYSI12204','GYSI12203','GYSI12202','GYSI12201','GYSI12200','GYSI12199','GYSI12198','GYSI12197','GYSI12196','GYSI12195','GYSI12194','GYSI12193','GYSI12192','GYSI12191','GYSI12190','GYSI12189','GYSI12188','GYSI12187','GYSI12186','GYSI12185','GYSI12184','GYSI12183','GYSI12182','GYSI12181','GYSI12180','GYSI12179','GYSI12178','GYSI12177','GYSI12176','GYSI12175','GYSI12174','GYSI12173','GYSI12172','GYSI12171','GYSI12170','GYSI12169','GYSI12168','GYSI12167','GYSI12166','GYSI12165','GYSI12162','GYSI12161','GYSI12160','GYSI12159','GYSI12158','GYSI12157','GYSI12156','GYSI12155','GYSI12154','GYSI12153','GYSI12152','GYSI12151','GYSI12150','GYSI12149','GYSI12148','GYSI12147','GYSI12146','GYSI12145','GYSI12144','GYSI12143','GYSI12142','GYSI12141','GYSI12140','GYSI12139','GYSI12138','GYSI12137','GYSI12135','GYSI12134','GYSI12133','GYSI12132','GYSI12131','GYSI12130','GYSI12129','GYSI12128','GYSI12127','GYSI12033','GYSI12032','GYSI12036','GYSI12026','GYSI12035','GYSI12038','GYSI12041','GYSI12040','GYSI12043','GYSI12046','GYSI12045','GYSI12048','GYSI12051','GYSI12050','GYSI12053','GYSI12056','GYSI12055','GYSI12058','GYSI12057','GYSI12061','GYSI12060','GYSI12059','GYSI12063','GYSI12062','GYSI12066','GYSI12065','GYSI12064','GYSI12068','GYSI12067','GYSI12071','GYSI12070','GYSI12069','GYSI12073','GYSI12072','GYSI12076','GYSI12075','GYSI12074','GYSI12078','GYSI12077','GYSI12080','GYSI12079','GYSI12084','GYSI12085','GYSI12087','GYSI12086','GYSI12089','GYSI12088','GYSI12094','GYSI12093','GYSI12092','GYSI12091','GYSI12090','GYSI12098','GYSI12097','GYSI12096','GYSI12095','GYSI12102','GYSI12101','GYSI12100','GYSI12099','GYSI12106','GYSI12105','GYSI12104','GYSI12103','GYSI12109','GYSI12108','GYSI12107','GYSI12114','GYSI12113','GYSI12112','GYSI12111','GYSI12110','GYSI12118','GYSI12117','GYSI12116','GYSI12115','GYSI12122','GYSI12126','GYSI12125','GYSI12124','GYSI12123','GYSI12121','GYSI12120','GYSI12119','GYSI12081','GYSI12054','GYSI12052','GYSI12049','GYSI12047','GYSI12044','GYSI12042','GYSI12039','GYSI12037','GYSI12034','GYSI12031','GYSI12030','GYSI12029','GYSI12028','GYSI12027','GYSI12025','GYSI12024','GYSI12023','GYSI12022','GYSI12021','GYSI12020','GYSI12019','GYSI12018','GYSI12017','GYSI12016','GYSI12015','GYSI12014','GYSI12013','GYSI12012','GYSI12011','GYSI11942','GYSI11941','GYSI11944','GYSI11943','GYSI11946','GYSI11945','GYSI11951','GYSI11950','GYSI11949','GYSI11948','GYSI11947','GYSI11952','GYSI11956','GYSI11955','GYSI11954','GYSI11953','GYSI11959','GYSI11958','GYSI11957','GYSI11965','GYSI11964','GYSI11962','GYSI11963','GYSI11961','GYSI11960','GYSI11967','GYSI11966','GYSI11971','GYSI11970','GYSI11969','GYSI11968','GYSI11975','GYSI11974','GYSI11973','GYSI11972','GYSI11978','GYSI11977','GYSI11976','GYSI11980','GYSI11979','GYSI11984','GYSI11983','GYSI11982','GYSI11981','GYSI11988','GYSI11987','GYSI11986','GYSI11985','GYSI11991','GYSI11990','GYSI11989','GYSI11996','GYSI11995','GYSI11994','GYSI11993','GYSI11992','GYSI12000','GYSI11999','GYSI11998','GYSI11997','GYSI12004','GYSI12003','GYSI12002','GYSI12001','GYSI12008','GYSI12007','GYSI12005','GYSI12006','GYSI12010','GYSI12009','GYSI11940','GYSI11929','GYSI11928','GYSI11927','GYSI11926','GYSI11925','GYSI11924','GYSI11923','GYSI11922','GYSI11921','GYSI11920','GYSI11919','GYSI11918','GYSI11917','GYSI11916','GYSI11915','GYSI11914','GYSI11913','GYSI11912','GYSI11911','GYSI11910','GYSI11909','GYSI11908','GYSI11907','GYSI11906','GYSI11905','GYSI11904','GYSI11903','GYSI11902','GYSI11901','GYSI11900','GYSI11899','GYSI11898','GYSI11897','GYSI11896','GYSI11895','GYSI11894','GYSI11893','GYSI11892','GYSI11891','GYSI11890','GYSI11889','GYSI11888','GYSI11887','GYSI11886','GYSI11885','GYSI11884','GYSI11883','GYSI11882','GYSI11881','GYSI11880','GYSI11879','GYSI11876','GYSI11875','GYSI11874','GYSI11873','GYSI11872','GYSI11871','GYSI11870','GYSI11869','GYSI11868','GYSI11867','GYSI11866','GYSI11865','GYSI11864','GYSI11863','GYSI11862','GYSI11861','GYSI11860','GYSI11859','GYSI11858','GYSI11857','GYSI11856','GYSI11855','GYSI11854']
# 分页大小取supplier_item_codes的长度，如果为空则取1
page_size = len(supplier_item_codes) if supplier_item_codes else 1
offset = 0
cnt = 1

# 连接数据库
conn = pymysql.connect(**config)

try:
    with conn.cursor() as cursor:
        # 查询orders表中符合条件的总订单数量
        sql_count = "SELECT COUNT(*) as total FROM orders WHERE channel_order_no LIKE 'ZZGT202505%'"
        cursor.execute(sql_count)
        result = cursor.fetchone()
        total_orders = result[0]
        # total_orders = 1000

        # 遍历日期范围
        for start_date, end_date in date_ranges:
            current_date = start_date
            while current_date <= end_date:
                if offset < total_orders:
                    # 查询orders表中符合条件的数据
                    sql_orders = """
                        SELECT order_no, main_order_no, channel_order_no, channel_order_time, create_time, supplier_item_code
                        FROM orders
                        WHERE channel_order_no LIKE 'ZZGT202505%%'
                        LIMIT %s OFFSET %s
                    """
                    cursor.execute(sql_orders, (page_size, offset))
                    orders_data = cursor.fetchall()

                    for index, order in enumerate(orders_data):
                        print(f"cnt:{cnt}")
                        print(order)
                        order_no = order[0]
                        main_order_no = order[1]
                        new_channel_order_time = current_date.replace(hour=12, minute=0, second=0)
                        new_create_time = current_date.replace(hour=12, minute=0, second=0)
                        new_send_time = current_date.replace(hour=12, minute=0, second=0)
                        new_supplier_item_code = supplier_item_codes[index]
                        update_sql_orders = """
                            UPDATE orders
                            SET channel_order_time = %s, create_time = %s, send_time = %s, supplier_item_code = %s, cost_avg_price = %s
                            WHERE order_no = %s
                        """
                        cursor.execute(update_sql_orders, (new_channel_order_time, new_create_time, new_send_time, new_supplier_item_code, 1.00, order_no))
                        print(f"已修改orders表中order_no为{order_no}的数据，日期：{current_date}，supplier_item_code：{new_supplier_item_code}")

                        update_sql_orders_main = """
                            UPDATE orders_main
                            SET send_time = %s
                            WHERE order_no = %s
                        """
                        cursor.execute(update_sql_orders_main, (new_send_time, main_order_no))
                        print(f"已修改orders_main表中order_no为{main_order_no}的send_time，日期：{current_date}")

                        new_channel_settlement_time = current_date.replace(hour=12, minute=0, second=0)
                        new_supplier_settlement_time = current_date.replace(hour=12, minute=0, second=0)
                        update_sql_orders_detail_extra = """
                            UPDATE orders_detail_extra
                            SET channel_settlement_time = %s, supplier_settlement_time = %s, create_time = %s
                            WHERE order_no = %s
                        """
                        cursor.execute(update_sql_orders_detail_extra, (new_channel_settlement_time, new_supplier_settlement_time, new_create_time, order_no))
                        # print(f"已修改orders_detail_extra表中order_no为{order_no}的数据，日期：{current_date}")
                        cnt += 1

                    # 每处理一批数据后提交事务
                    conn.commit()

                offset += page_size
                current_date += datetime.timedelta(days=1)

except pymysql.MySQLError as e:
    print(f"数据库操作出错: {e}")
    conn.rollback()
finally:
    # 关闭连接
    conn.close()



