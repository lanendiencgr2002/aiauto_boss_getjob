import os
import json
def 读取txt文件(文件路径):
    if not os.path.exists(文件路径):
        with open(文件路径, "w", encoding="utf-8") as f:
            f.write("")
            # print(f"文件不存在，已创建空文件：{文件路径}")
    with open(文件路径, "r", encoding="utf-8") as f:
        文件内容 = f.read().strip()
    return 文件内容

def 追加模式写入日志txt(文件路径, 内容):
    with open(文件路径, "a", encoding="utf-8") as f:
        f.write(内容+"\n")

def 写入模式写入日志txt(文件路径, 内容):
    with open(文件路径, "w", encoding="utf-8") as f:
        f.write(内容+"\n")

def 写入本次面试运行日志(内容):
    追加模式写入日志txt("./本次面试运行日志.txt", 内容)
def 清空本次面试运行日志():
    写入模式写入日志txt("./本次面试运行日志.txt", "")

def 读取配置():
    """读取并解析配置文件"""
    try:
        # 读取所有配置文件
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        with open('./city_list.json', 'r', encoding='utf-8') as f:
            city_list = json.load(f)
        with open('./boss_config.json', 'r', encoding='utf-8') as f:
            boss_config = json.load(f)
        with open('./我的简历.txt', 'r', encoding='utf-8') as f:
            my_resume = f.read().strip()
            
        # 将城市名称转换为城市ID
        城市列表 = []
        for city in config['要查询的城市']:
            if city in city_list:
                城市列表.append(city_list[city])
        config['要查询的城市'] = 城市列表
        
        # 转换学历代码
        if config['学历筛选'] in boss_config['degree']:
            config['学历筛选'] = boss_config['degree'][config['学历筛选']]

        return config, my_resume
        
    except FileNotFoundError as e:
        print(f'配置文件不存在: {e.filename}')
        raise
    except KeyError as e:
        print(f'配置项错误: {e}')
        raise
    except Exception as e:
        print(f'发生未知错误: {e}')
        raise
    

def 写入日志(内容, 文件路径="./本次面试运行日志.txt", 模式='a', 是否打印=True, 是否写入文件=True):
    """
    统一的日志处理函数
    :param 内容: 要写入的内容
    :param 文件路径: 日志文件路径
    :param 模式: 'w' 为覆盖写入，'a' 为追加写入
    :param 是否打印: 是否同时打印到控制台
    :param 是否写入文件: 是否写入到日志文件
    """
    if 是否写入文件:
        with open(文件路径, 模式, encoding='utf-8') as f:
            f.write(f"{内容}\n")
    
    if 是否打印:
        print(内容)
def 写入统计日志(内容, 文件路径="./统计日志.txt", 模式='a', 是否打印=True, 是否写入文件=True):
    """
    写入统计日志
    """
    if 是否写入文件:
        with open(文件路径, 模式, encoding='utf-8') as f:
            f.write(f"{内容}\n")
    if 是否打印:
        print(内容)

def 写入已投递岗位(内容, 文件路径="./已投递岗位详情.txt", 模式='a', 是否打印=True, 是否写入文件=True):
    """
    写入统计日志
    """
    if 是否写入文件:
        with open(文件路径, 模式, encoding='utf-8') as f:
            f.write(f"{内容}\n")
    if 是否打印:
        print(内容)
