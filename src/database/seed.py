"""种子数据：3 用户 + 10 商品 + 10 订单 + 5 物流 + 2 退款"""

import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import get_session_factory
from src.database.models import (
    Logistics,
    LogisticsTrack,
    Order,
    OrderItem,
    Product,
    Refund,
    User,
)

# ── 用户 ──────────────────────────────────────────────
USERS = [
    {
        "id": "user_001",
        "username": "zhangsan",
        "display_name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138001",
    },
    {
        "id": "user_002",
        "username": "lisi",
        "display_name": "李四",
        "email": "lisi@example.com",
        "phone": "13800138002",
    },
    {
        "id": "user_003",
        "username": "wangwu",
        "display_name": "王五",
        "email": "wangwu@example.com",
        "phone": "13800138003",
    },
]

# ── 商品 ──────────────────────────────────────────────
PRODUCTS = [
    {
        "id": "prod_001",
        "name": "iPhone 16 Pro 256GB",
        "category": "手机",
        "price": 8999.00,
        "stock": 50,
        "description": "Apple iPhone 16 Pro，256GB 存储空间，沙漠色钛金属设计",
        "specs": "颜色：沙漠色钛金属/黑色钛金属/白色钛金属/原色钛金属 | 芯片：A18 Pro | 屏幕：6.3 英寸 Super Retina XDR | 摄像头：4800 万像素主摄 + 1200 万超广角 + 1200 万长焦",
    },
    {
        "id": "prod_002",
        "name": "MacBook Pro 14 M4 Pro",
        "category": "笔记本",
        "price": 14999.00,
        "stock": 30,
        "description": "Apple MacBook Pro 14 英寸，M4 Pro 芯片，18GB 统一内存，512GB 存储",
        "specs": "芯片：M4 Pro (14 核 CPU / 20 核 GPU) | 内存：18GB 统一内存 | 存储：512GB SSD | 屏幕：14.2 英寸 Liquid Retina XDR | 接口：3×Thunderbolt 4, HDMI, SDXC",
    },
    {
        "id": "prod_003",
        "name": "iPad Air M3 11英寸",
        "category": "平板",
        "price": 4799.00,
        "stock": 80,
        "description": "Apple iPad Air M3 芯片，11 英寸 Liquid Retina 显示屏，128GB 存储",
        "specs": "芯片：M3 | 屏幕：11 英寸 Liquid Retina | 存储：128GB | 支持：Apple Pencil Pro, Magic Keyboard | 颜色：星光色/深空灰/蓝色/紫色",
    },
    {
        "id": "prod_004",
        "name": "AirPods Pro 3",
        "category": "耳机",
        "price": 1899.00,
        "stock": 200,
        "description": "Apple AirPods Pro 3 代，自适应音频，主动降噪，USB-C 充电盒",
        "specs": "芯片：H3 | 降噪：自适应主动降噪 | 音效：支持空间音频 | 续航：单次 8 小时(含充电盒 36 小时) | 防水：IPX4",
    },
    {
        "id": "prod_005",
        "name": "Apple Watch Ultra 3",
        "category": "手表",
        "price": 5999.00,
        "stock": 40,
        "description": "Apple Watch Ultra 3，49 毫米钛金属表壳，精准双频 GPS，超长续航",
        "specs": "表壳：49 毫米钛金属 | 屏幕：3000 尼特峰值亮度 | 续航：最长 36 小时(低功耗模式 72 小时) | 防水：100 米 | 功能：血氧/心率/体温/深度计",
    },
    {
        "id": "prod_006",
        "name": "ShopAgent 降噪耳机 Pro",
        "category": "耳机",
        "price": 499.00,
        "stock": 150,
        "description": "ShopAgent 自研主动降噪头戴耳机，40dB 深度降噪，Hi-Res 音质认证",
        "specs": "降噪：40dB 自适应主动降噪 | 续航：60 小时(ANC 开) | 连接：蓝牙 5.4, 3.5mm 有线 | 重量：250g | 颜色：磨砂黑/陶瓷白",
    },
    {
        "id": "prod_007",
        "name": "智能家居音箱",
        "category": "智能家居",
        "price": 299.00,
        "stock": 100,
        "description": "智能语音助手音箱，支持智能家居控制、语音购物查询、音乐播放",
        "specs": "语音：远场语音唤醒 | 控制：支持 200+ 智能设备品牌 | 音质：双 40mm 全频扬声器 | 连接：Wi-Fi 6 / 蓝牙 5.3 | 尺寸：150×80×80mm",
    },
    {
        "id": "prod_008",
        "name": "15W 无线充电器",
        "category": "配件",
        "price": 89.00,
        "stock": 300,
        "description": "15W 高速无线充电器，Qi2 认证，兼容 iPhone/Android，支持 MagSafe",
        "specs": "功率：15W 最大 | 标准：Qi2 认证 | 兼容：MagSafe | 输入：USB-C | 指示灯：LED 充电状态 | 尺寸：100×100×12mm",
    },
    {
        "id": "prod_009",
        "name": "便携式 SSD 1TB",
        "category": "配件",
        "price": 599.00,
        "stock": 60,
        "description": "1TB 便携式固态硬盘，USB-C 接口，读取速度 1050MB/s，IP65 防水防尘",
        "specs": "容量：1TB | 接口：USB 3.2 Gen 2 Type-C | 读取：1050MB/s | 写入：1000MB/s | 防护：IP65 | 尺寸：95×50×10mm | 重量：45g",
    },
    {
        "id": "prod_010",
        "name": "Type-C 快充线 2米",
        "category": "配件",
        "price": 49.00,
        "stock": 500,
        "description": "USB-C to USB-C 高速快充数据线，2 米长度，支持 PD 100W 快充，编织材质",
        "specs": "接口：USB-C to USB-C | 长度：2 米 | 快充：PD 100W | 数据：USB 3.1 Gen 2 (10Gbps) | 材质：编织尼龙 | 颜色：黑色/白色",
    },
]

# ── 订单 ──────────────────────────────────────────────
ORDERS = [
    # user_001 (张三) — 4 笔
    {
        "id": "ord_001",
        "order_no": "ORD-20260501-001",
        "user_id": "user_001",
        "total_amount": 18998.00,
        "status": "delivered",
        "shipping_address": "北京市朝阳区建国路 88 号 1608 室",
        "items": [
            {"id": "oi_001", "product_id": "prod_001", "quantity": 1, "price": 8999.00},
            {"id": "oi_002", "product_id": "prod_005", "quantity": 1, "price": 5999.00},
            {"id": "oi_003", "product_id": "prod_010", "quantity": 2, "price": 49.00},
        ],
    },
    {
        "id": "ord_002",
        "order_no": "ORD-20260508-001",
        "user_id": "user_001",
        "total_amount": 4799.00,
        "status": "shipped",
        "shipping_address": "北京市朝阳区建国路 88 号 1608 室",
        "items": [
            {"id": "oi_004", "product_id": "prod_003", "quantity": 1, "price": 4799.00},
        ],
    },
    {
        "id": "ord_003",
        "order_no": "ORD-20260512-001",
        "user_id": "user_001",
        "total_amount": 499.00,
        "status": "paid",
        "shipping_address": "北京市朝阳区建国路 88 号 1608 室",
        "items": [
            {"id": "oi_005", "product_id": "prod_006", "quantity": 1, "price": 499.00},
        ],
    },
    {
        "id": "ord_004",
        "order_no": "ORD-20260501-002",
        "user_id": "user_001",
        "total_amount": 299.00,
        "status": "cancelled",
        "shipping_address": "北京市朝阳区建国路 88 号 1608 室",
        "items": [
            {"id": "oi_006", "product_id": "prod_007", "quantity": 1, "price": 299.00},
        ],
    },
    # user_002 (李四) — 3 笔
    {
        "id": "ord_005",
        "order_no": "ORD-20260503-001",
        "user_id": "user_002",
        "total_amount": 14999.00,
        "status": "delivered",
        "shipping_address": "上海市浦东新区张江路 100 号 301 室",
        "items": [
            {"id": "oi_007", "product_id": "prod_002", "quantity": 1, "price": 14999.00},
        ],
    },
    {
        "id": "ord_006",
        "order_no": "ORD-20260510-001",
        "user_id": "user_002",
        "total_amount": 1899.00,
        "status": "shipped",
        "shipping_address": "上海市浦东新区张江路 100 号 301 室",
        "items": [
            {"id": "oi_008", "product_id": "prod_004", "quantity": 1, "price": 1899.00},
        ],
    },
    {
        "id": "ord_007",
        "order_no": "ORD-20260514-001",
        "user_id": "user_002",
        "total_amount": 136.00,
        "status": "paid",
        "shipping_address": "上海市浦东新区张江路 100 号 301 室",
        "items": [
            {"id": "oi_009", "product_id": "prod_008", "quantity": 1, "price": 89.00},
            {"id": "oi_010", "product_id": "prod_010", "quantity": 1, "price": 49.00},
        ],
    },
    # user_003 (王五) — 3 笔
    {
        "id": "ord_008",
        "order_no": "ORD-20260505-001",
        "user_id": "user_003",
        "total_amount": 8999.00,
        "status": "delivered",
        "shipping_address": "广州市天河区体育西路 200 号 502 室",
        "items": [
            {"id": "oi_011", "product_id": "prod_001", "quantity": 1, "price": 8999.00},
        ],
    },
    {
        "id": "ord_009",
        "order_no": "ORD-20260511-001",
        "user_id": "user_003",
        "total_amount": 599.00,
        "status": "shipped",
        "shipping_address": "广州市天河区体育西路 200 号 502 室",
        "items": [
            {"id": "oi_012", "product_id": "prod_009", "quantity": 1, "price": 599.00},
        ],
    },
    {
        "id": "ord_010",
        "order_no": "ORD-20260513-001",
        "user_id": "user_003",
        "total_amount": 499.00,
        "status": "pending",
        "shipping_address": "广州市天河区体育西路 200 号 502 室",
        "items": [
            {"id": "oi_013", "product_id": "prod_006", "quantity": 1, "price": 499.00},
        ],
    },
]

# ── 物流 ──────────────────────────────────────────────
LOGISTICS = [
    {
        "id": "log_001",
        "order_id": "ord_001",
        "tracking_no": "SF1487654321",
        "carrier": "顺丰速运",
        "status": "delivered",
        "address": "北京市朝阳区建国路 88 号 1608 室",
        "tracks": [
            {"status": "已揽收", "message": "快递员已揽收，预计 2026-05-01 18:00 前发出", "offset_days": -14},
            {"status": "运输中", "message": "已到达北京中转中心", "offset_days": -13},
            {"status": "派送中", "message": "快递员正在派送，电话 13800138001", "offset_days": -12},
            {"status": "已签收", "message": "已由本人签收", "offset_days": -12},
        ],
    },
    {
        "id": "log_002",
        "order_id": "ord_002",
        "tracking_no": "SF1498765432",
        "carrier": "顺丰速运",
        "status": "delivering",
        "address": "北京市朝阳区建国路 88 号 1608 室",
        "tracks": [
            {"status": "已揽收", "message": "快递员已揽收", "offset_days": -3},
            {"status": "运输中", "message": "已到达北京中转中心", "offset_days": -2},
            {"status": "派送中", "message": "正在派送中，预计今日 18:00 前送达", "offset_days": -1},
        ],
    },
    {
        "id": "log_003",
        "order_id": "ord_005",
        "tracking_no": "SF1456789012",
        "carrier": "顺丰速运",
        "status": "delivered",
        "address": "上海市浦东新区张江路 100 号 301 室",
        "tracks": [
            {"status": "已揽收", "message": "快递员已揽收", "offset_days": -11},
            {"status": "运输中", "message": "已到达上海浦东北蔡中转中心", "offset_days": -10},
            {"status": "派送中", "message": "快递员正在派送", "offset_days": -9},
            {"status": "已签收", "message": "已由本人签收", "offset_days": -9},
        ],
    },
    {
        "id": "log_004",
        "order_id": "ord_006",
        "tracking_no": "YT20260510001",
        "carrier": "圆通速递",
        "status": "in_transit",
        "address": "上海市浦东新区张江路 100 号 301 室",
        "tracks": [
            {"status": "已揽收", "message": "快递员已揽收", "offset_days": -4},
            {"status": "运输中", "message": "已到达上海分拣中心", "offset_days": -3},
        ],
    },
    {
        "id": "log_005",
        "order_id": "ord_008",
        "tracking_no": "SF1567890123",
        "carrier": "顺丰速运",
        "status": "delivered",
        "address": "广州市天河区体育西路 200 号 502 室",
        "tracks": [
            {"status": "已揽收", "message": "快递员已揽收", "offset_days": -9},
            {"status": "运输中", "message": "已到达广州中转中心", "offset_days": -8},
            {"status": "派送中", "message": "快递员正在派送", "offset_days": -7},
            {"status": "已签收", "message": "已由本人签收", "offset_days": -7},
        ],
    },
]

# ── 退款 ──────────────────────────────────────────────
REFUNDS = [
    {
        "id": "ref_001",
        "order_id": "ord_001",
        "user_id": "user_001",
        "amount": 8999.00,
        "reason": "商品颜色与描述不符",
        "status": "approved",
    },
    {
        "id": "ref_002",
        "order_id": "ord_005",
        "user_id": "user_002",
        "amount": 14999.00,
        "reason": "收到后屏幕有坏点",
        "status": "pending",
    },
]


async def seed_database():
    factory = get_session_factory()

    async with factory() as session:
        # 检查是否已有数据
        existing = (await session.execute(select(User))).scalars().first()
        if existing:
            return  # 已 seed 过，跳过

        # 用户
        for u in USERS:
            session.add(User(**u))

        # 商品
        for p in PRODUCTS:
            session.add(Product(**p))

        await session.commit()

    # 订单和物流单独提交（依赖用户和商品已存在）
    now = datetime.datetime.now()

    async with factory() as session:
        for o in ORDERS:
            items = o.pop("items")
            order = Order(**o)
            session.add(order)
            for item in items:
                session.add(OrderItem(order_id=order.id, **item))
        await session.commit()

    async with factory() as session:
        for lg in LOGISTICS:
            tracks = lg.pop("tracks")
            logistics = Logistics(**lg)
            session.add(logistics)
            for t in tracks:
                offset = t.pop("offset_days")
                session.add(
                    LogisticsTrack(
                        logistics_id=logistics.id,
                        timestamp=now + datetime.timedelta(days=offset),
                        **t,
                    )
                )
        await session.commit()

    async with factory() as session:
        for r in REFUNDS:
            session.add(Refund(**r))
        await session.commit()
