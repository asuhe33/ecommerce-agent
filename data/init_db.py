"""数据库初始化脚本：创建表结构 + 插入 mock 数据。

使用方法:
    python data/init_db.py          # 建表 + 插入数据
    python data/init_db.py --reset  # 删除旧表重新创建
"""

import argparse
import random
import sys
from datetime import datetime, timedelta

# 修复 Windows GBK 编码
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sqlalchemy import text

from config import config
from database.db_manager import db_manager

# ── 建表 SQL ──────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    contact VARCHAR(100),
    phone VARCHAR(50),
    address TEXT,
    rating DECIMAL(3,2) DEFAULT 4.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    supplier_id INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT '已完成',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""

# ── Mock 数据生成 ─────────────────────────────────────────

SUPPLIER_NAMES = [
    ("深圳优品科技有限公司", "张经理", "13800138001", "深圳市南山区科技园"),
    ("广州华美电子科技", "李经理", "13800138002", "广州市天河区天河路"),
    ("上海智联家居", "王经理", "13800138003", "上海市浦东新区陆家嘴"),
    ("杭州时尚服饰", "赵经理", "13800138004", "杭州市西湖区文三路"),
    ("北京数码先锋", "刘经理", "13800138005", "北京市海淀区中关村"),
    ("成都食品批发", "陈经理", "13800138006", "成都市武侯区天府大道"),
    ("武汉运动户外", "周经理", "13800138007", "武汉市洪山区光谷"),
    ("南京母婴用品", "吴经理", "13800138008", "南京市玄武区珠江路"),
    ("西安图书文化", "郑经理", "13800138009", "西安市雁塔区高新路"),
    ("重庆汽车用品", "孙经理", "13800138010", "重庆市渝北区新牌坊"),
]

CATEGORIES = {
    "手机数码": [
        ("iPhone 15 Pro", 8999.00, "苹果最新旗舰手机，钛金属设计"),
        ("iPhone 15", 5999.00, "苹果标准版，灵动岛屏幕"),
        ("华为 Mate 60 Pro", 6999.00, "华为旗舰，麒麟芯片"),
        ("小米 14 Pro", 4999.00, "徕卡影像，骁龙8 Gen3"),
        ("OPPO Find X7", 3999.00, "哈苏影像系统"),
        ("vivo X100 Pro", 4499.00, "蔡司光学镜头"),
        ("三星 Galaxy S24", 5699.00, "AI手机，骁龙8 Gen3"),
        ("一加 12", 4299.00, "哈苏影像，超长续航"),
        ("荣耀 Magic6", 4399.00, "青海湖电池技术"),
        ("红米 K70 Pro", 3299.00, "性价比旗舰"),
    ],
    "电脑办公": [
        ("MacBook Air M3", 8999.00, "轻薄本，M3芯片"),
        ("MacBook Pro 14", 14999.00, "专业级，M3 Pro芯片"),
        ("联想 ThinkPad X1", 9999.00, "商务旗舰笔记本"),
        ("华为 MateBook X Pro", 8999.00, "全面屏轻薄本"),
        ("戴尔 XPS 13", 7999.00, "超窄边框设计"),
        ("微软 Surface Pro 9", 7599.00, "二合一平板电脑"),
        ("联想小新 Pro 16", 5499.00, "高性能轻薄本"),
        ("华硕天选 5 Pro", 8999.00, "游戏本，RTX4060"),
        ("惠普战66", 4299.00, "商务办公本"),
        ("iPad Pro 12.9", 8499.00, "M2芯片平板电脑"),
    ],
    "家用电器": [
        ("戴森 V15 吸尘器", 4990.00, "无线吸尘器，激光探测"),
        ("美的空调 1.5匹", 2899.00, "变频一级能效"),
        ("海尔冰箱 500L", 3599.00, "对开门风冷无霜"),
        ("小米电视 75寸", 3999.00, "4K超清智能电视"),
        ("西门子洗衣机", 4299.00, "滚筒变频10KG"),
        ("九阳豆浆机", 399.00, "全自动多功能"),
        ("飞利浦剃须刀", 599.00, "三刀头防水"),
        ("松下微波炉", 799.00, "变频加热23L"),
        ("科沃斯扫地机器人", 2499.00, "激光导航自动集尘"),
        ("苏泊尔电饭煲", 499.00, "IH加热4L"),
    ],
    "服饰鞋包": [
        ("优衣库羽绒服", 599.00, "轻薄保暖"),
        ("Nike Air Max", 899.00, "经典气垫跑鞋"),
        ("Adidas 三叶草卫衣", 499.00, "运动休闲"),
        ("New Balance 574", 699.00, "复古跑鞋"),
        ("Coach 女包", 2599.00, "经典托特包"),
        ("Levi's 501 牛仔裤", 599.00, "经典直筒"),
        ("ZARA 羊毛大衣", 899.00, "秋冬新款"),
        ("Converse 1970s", 569.00, "高帮帆布鞋"),
        ("北面冲锋衣", 1299.00, "防水防风"),
        ("CK 皮带", 399.00, "头层牛皮"),
    ],
    "食品生鲜": [
        ("三只松鼠坚果礼盒", 168.00, "混合坚果5斤装"),
        ("茅台飞天 53度", 2799.00, "500ml酱香型"),
        ("五粮液普五", 1099.00, "52度浓香型"),
        ("智利车厘子 5斤", 299.00, "JJ级大果"),
        ("新西兰奇异果 24个", 89.00, "黄心大果"),
        ("五常大米 10斤", 79.00, "东北稻花香"),
        ("橄榄油 1L", 128.00, "西班牙进口特级初榨"),
        ("星巴克咖啡豆 500g", 158.00, "深度烘焙"),
        ("费列罗巧克力 48粒", 99.00, "意大利进口"),
        ("澳洲牛排套餐", 268.00, "M3西冷1kg装"),
    ],
}

CUSTOMER_NAMES = [
    "张伟", "李娜", "王芳", "刘洋", "陈静", "杨光", "赵磊", "黄海",
    "周敏", "吴强", "徐丽", "孙杰", "马超", "朱琳", "郑宇", "冯丹",
    "韩雪", "曹阳", "彭辉", "曾艳", "肖勇", "田甜", "董明", "袁梦",
    "蒋涛", "沈艳", "韦刚", "秦丽", "阎军",
]

ORDER_STATUSES = ["已完成", "已完成", "已完成", "已发货", "处理中", "已取消"]


def create_tables():
    """创建所有表结构。"""
    with db_manager.engine.connect() as conn:
        for statement in SCHEMA_SQL.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("[DB] 表结构创建完成")


def drop_tables():
    """删除所有表（用于 reset）。"""
    tables = ["order_items", "orders", "customers", "products", "suppliers"]
    with db_manager.engine.connect() as conn:
        for t in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {t}"))
        conn.commit()
    print("[DB] 旧表已清除")


def insert_mock_data():
    """插入 mock 数据。"""
    with db_manager.engine.connect() as conn:
        # 1. 供应商
        for name, contact, phone, address in SUPPLIER_NAMES:
            conn.execute(
                text(
                    "INSERT INTO suppliers (name, contact, phone, address, rating) "
                    "VALUES (:name, :contact, :phone, :address, :rating)"
                ),
                {
                    "name": name,
                    "contact": contact,
                    "phone": phone,
                    "address": address,
                    "rating": round(random.uniform(3.5, 5.0), 2),
                },
            )
        print(f"[DB] 已插入 {len(SUPPLIER_NAMES)} 个供应商")

        # 2. 商品
        product_id = 0
        for category, products in CATEGORIES.items():
            for name, price, desc in products:
                product_id += 1
                conn.execute(
                    text(
                        "INSERT INTO products (name, category, price, stock, supplier_id, description) "
                        "VALUES (:name, :category, :price, :stock, :supplier_id, :description)"
                    ),
                    {
                        "name": name,
                        "category": category,
                        "price": price,
                        "stock": random.randint(5, 500),
                        "supplier_id": random.randint(1, len(SUPPLIER_NAMES)),
                        "description": desc,
                    },
                )
        print(f"[DB] 已插入 {product_id} 个商品")

        # 3. 客户
        for i, name in enumerate(CUSTOMER_NAMES, 1):
            conn.execute(
                text(
                    "INSERT INTO customers (name, phone, email) "
                    "VALUES (:name, :phone, :email)"
                ),
                {
                    "name": name,
                    "phone": f"138{random.randint(10000000, 99999999)}",
                    "email": f"customer{i}@example.com",
                },
            )
        print(f"[DB] 已插入 {len(CUSTOMER_NAMES)} 个客户")

        # 4. 订单 + 订单明细
        today = datetime.now().date()
        order_id = 0
        for _ in range(200):
            order_id += 1
            customer_id = random.randint(1, len(CUSTOMER_NAMES))
            order_date = today - timedelta(days=random.randint(0, 90))
            status = random.choice(ORDER_STATUSES)

            # 每个订单 1-4 个商品
            num_items = random.randint(1, 4)
            items = random.sample(range(1, product_id + 1), min(num_items, product_id))
            total = 0.0

            conn.execute(
                text(
                    "INSERT INTO orders (customer_id, order_date, total_amount, status) "
                    "VALUES (:cid, :odate, :total, :status)"
                ),
                {
                    "cid": customer_id,
                    "odate": order_date,
                    "total": 0,  # 先占位，后面更新
                    "status": status,
                },
            )

            for pid in items:
                qty = random.randint(1, 3)
                # 获取商品价格
                result = conn.execute(
                    text("SELECT price FROM products WHERE id = :pid"), {"pid": pid}
                )
                price = result.scalar()
                total += float(price) * qty

                conn.execute(
                    text(
                        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                        "VALUES (:oid, :pid, :qty, :price)"
                    ),
                    {"oid": order_id, "pid": pid, "qty": qty, "price": price},
                )

            # 更新订单总金额
            conn.execute(
                text("UPDATE orders SET total_amount = :total WHERE id = :oid"),
                {"total": round(total, 2), "oid": order_id},
            )

        print(f"[DB] 已插入 {order_id} 条订单")
        conn.commit()

    print("[DB] ✅ Mock 数据全部插入完成")


def main():
    parser = argparse.ArgumentParser(description="初始化电商数据库")
    parser.add_argument("--reset", action="store_true", help="删除旧表重新创建")
    args = parser.parse_args()

    if not db_manager.test_connection():
        print("[DB] ❌ 数据库连接失败，请检查 .env 中的 MySQL 配置")
        return

    if args.reset:
        drop_tables()

    create_tables()
    insert_mock_data()
    print("[DB] 🎉 数据库初始化完成！")


if __name__ == "__main__":
    main()
