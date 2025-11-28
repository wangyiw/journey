from enum import IntEnum


class GenderEnum(IntEnum):
    """性别枚举"""
    MALE = 0  # 男
    FEMALE = 1  # 女

class CityEnum(IntEnum):
    """城市枚举"""
    Tokyo = 0           # 东京
    Paris = 1           # 巴黎
    London = 2          # 伦敦
    NewYork = 3         # 纽约
    Bangkok = 4         # 曼谷
    Rome = 5            # 罗马
    Madrid = 6          # 马德里
    Istanbul = 7        # 伊斯坦布尔
    Milan = 8           # 米兰
    Singapore = 9       # 新加坡
    Dubai = 10          # 迪拜
    Beijing = 11        # 北京
    Shenzhen = 12       # 深圳
    Berlin = 13         # 柏林
    KualaLumpur = 14    # 吉隆坡
    Seoul = 15          # 首尔
    Shanghai = 16       # 上海
    HongKong = 17       # 香港
    Amsterdam = 18      # 阿姆斯特丹
    Sydney = 19         # 悉尼


class ModeEnum(IntEnum):
    """模式枚举"""
    EASY = 0  # 轻松模式
    MASTER = 1  # 大师模式


class StyleEnum(IntEnum):
    """风格枚举"""
    FRENCH_ELEGANT = 0  # 法式优雅
    JAPANESE_SIMPLE = 1  # 日系简约
    FUTURE_TECH = 2  # 未来科技
    AI_RANDOM = 3  # AI随机匹配


class MaterialEnum(IntEnum):
    """材质枚举"""
    DENIM = 0  # 牛仔
    SILK = 1  # 丝绸
    COTTON = 2  # 棉料
    METAL = 3  # 金属
    AI_RANDOM = 4  # AI随机匹配


class ColorEnum(IntEnum):
    """色调枚举"""
    WARM = 0  # 暖色调
    COLD = 1  # 冷色调
    NEUTRAL = 2  # 中性色调
    AI_RANDOM = 3  # AI随机匹配


class TypeEnum(IntEnum):
    """类型枚举"""
    SUIT = 0  # 套装
    DRESS = 1  # 连衣裙
    COAT = 2  # 外套
    LOCAL_COSTUME = 3  # 当地特色服饰
    AI_RANDOM = 4  # AI随机匹配


class ClothesCategory(IntEnum):
    """服装类别枚举"""
    MALE_TOP = 0  # 男上装
    MALE_BOTTOM = 1  # 男下装
    FEMALE_TOP = 2  # 女上装
    FEMALE_BOTTOM = 3  # 女下装
    DRESS = 4  # 连衣裙
