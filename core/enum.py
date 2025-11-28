from enum import Enum


class GenderEnum(str, Enum):
    """性别枚举 """
    Male = "Male"      # 男
    Female = "Female"  # 女


class CityEnum(str, Enum):
    """城市枚举 """
    Tokyo = "Tokyo"              # 东京
    Paris = "Paris"              # 巴黎
    London = "London"            # 伦敦
    NewYork = "NewYork"          # 纽约
    Bangkok = "Bangkok"          # 曼谷
    Rome = "Rome"                # 罗马
    Madrid = "Madrid"            # 马德里
    Istanbul = "Istanbul"        # 伊斯坦布尔
    Milan = "Milan"              # 米兰
    Singapore = "Singapore"      # 新加坡
    Dubai = "Dubai"              # 迪拜
    Beijing = "Beijing"          # 北京
    Shenzhen = "Shenzhen"        # 深圳
    Berlin = "Berlin"            # 柏林
    KualaLumpur = "KualaLumpur"  # 吉隆坡
    Seoul = "Seoul"              # 首尔
    Shanghai = "Shanghai"        # 上海
    HongKong = "HongKong"        # 香港
    Amsterdam = "Amsterdam"      # 阿姆斯特丹
    Sydney = "Sydney"            # 悉尼


class ModeEnum(str, Enum):
    """模式枚举 """
    Easy = "Easy"      # 轻松模式
    Master = "Master"  # 大师模式


class StyleEnum(str, Enum):
    """风格枚举 """
    FrenchElegant = "FrenchElegant"    # 法式优雅
    JapaneseSimple = "JapaneseSimple"  # 日系简约
    FutureTech = "FutureTech"          # 未来科技
    AIRandom = "AIRandom"              # AI随机匹配


class MaterialEnum(str, Enum):
    """材质枚举 """
    Denim = "Denim"        # 牛仔
    Silk = "Silk"          # 丝绸
    Cotton = "Cotton"      # 棉料
    Metal = "Metal"        # 金属
    AIRandom = "AIRandom"  # AI随机匹配


class ColorEnum(str, Enum):
    """色调枚举 """
    Warm = "Warm"          # 暖色调
    Cold = "Cold"          # 冷色调
    Neutral = "Neutral"    # 中性色调
    AIRandom = "AIRandom"  # AI随机匹配


class TypeEnum(str, Enum):
    """类型枚举 """
    Suit = "Suit"                  # 套装
    Dress = "Dress"                # 连衣裙
    Coat = "Coat"                  # 外套
    LocalCostume = "LocalCostume"  # 当地特色服饰
    AIRandom = "AIRandom"          # AI随机匹配


class ClothesCategory(str, Enum):
    """服装类别枚举 """
    MaleTop = "MaleTop"        # 男上装
    MaleBottom = "MaleBottom"  # 男下装
    FemaleTop = "FemaleTop"    # 女上装
    FemaleBottom = "FemaleBottom"  # 女下装
    Dress = "Dress"            # 连衣裙
