import aiohttp
import asyncio
from dataclasses import dataclass
import requests
from typing import Optional
from 配置类 import 配置类
import concurrent.futures
import re
from 日志类 import LoggerManager
AIClasslog=LoggerManager(name="AI过滤").get_logger()

def 统一错误返回装饰器(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'服务器发生错误：{e}')
            return None
    return wrapper
def 判断返回是否符合要求(value_type="string"):
    """返回值验证装饰器，会去除换行符空行等
    不符合要求则返回None
    
    Args:
        value_type: 期望的返回值类型
            - "int": 整数
            - "float": 浮点数
            - "bool": 布尔值("true"/"false")
            - "string": 字符串(默认)
            
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 处理 None 返回值
            if result is None:
                return None
            # 处理换行符空行等
            result = result.strip()
            try:
                # 根据不同类型进行验证
                if value_type == "int":
                    int(result)  # 尝试转换为整数
                elif value_type == "float":
                    float(result)  # 尝试转换为浮点数
                elif value_type == "bool":
                    if result.lower() not in ["true", "false"]:
                        return None
                # string类型不需要特殊验证
                
                return result
            except (ValueError, AttributeError):
                return None
                
        return wrapper
    return decorator
def 专用响应格式处理(func):
    def wrapper(*args, **kwargs):
        try:
            result=func(*args, **kwargs)
            result=result.strip()
            # 去除'''json'''
            if result.startswith('```json') and result.endswith('```'):
                result=result[6:-3]
            # 去除''' '''
            if result.startswith('```') and result.endswith('```'):
                result=result[3:-3]
            # 如果是大写True或False 则转换为小写
            if 'True' in result:
                result=result.replace('True', 'true')
            if 'False' in result:
                result=result.replace('False', 'false')
        except Exception as e:
            print(f'服务器发生错误：{e}')
            return None
        return result
    return wrapper

@dataclass
class APIResponse:
    url = "http://localhost:5000/chat"
    @classmethod
    def return_response(cls, result):
        """从API响应中提取消息内容
        
        Args:
            result (dict): API返回的JSON响应数据
            
        Returns:
            str: 提取的消息内容
        """
        return result["data"]["message"]
    @classmethod
    @专用响应格式处理
    async def asnyc_get_response(cls, content):
        """异步获取API响应
        
        向本地FastAPI服务发送POST请求并获取响应
        
        Args:
            content: 要发送的问题内容
            
        Returns:
            str: API返回的消息内容
            None: 请求失败时返回None
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cls.url,
                json={"问题": content}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return cls.return_response(result)
                else:
                    return None
    @classmethod
    @专用响应格式处理
    def sync_get_response(cls, content):
        """同步方式获取API响应
        
        在同步环境中调用异步get_response方法
        
        Args:
            content: 要发送的问题内容
            
        Returns:
            str: API返回的消息内容
            None: 请求失败时返回None
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(cls.asnyc_get_response(content))
    @classmethod
    @专用响应格式处理
    def normal_get_response(cls, content):
        """同步方式使用requests获取API响应
        
        使用requests库发送POST请求获取响应
        
        Args:
            content: 要发送的问题内容
            
        Returns:
            str: API返回的消息内容
            None: 请求失败时返回None
        """
        响应 = requests.post(cls.url, json={
            "问题": content,
        })
        if 响应.status_code == 200:
            return cls.return_response(响应.json())
        else:
            return None

@dataclass
class AI初步过滤类(APIResponse):
    config=配置类.读取toml文件('config.toml')
    用多线程ai过滤和投简历=config['use_multi_thread']
    AI过滤岗位名线程数=config['ai_filter_threads']
    单个岗位信息:dict
    岗位信息列表:list
    已查询岗位数:int
    过滤后岗位数:int
    沟通次数:int
    @classmethod
    def 过滤岗位列表(cls,岗位信息列表):
        过滤后的岗位列表=[]
        if cls.用多线程ai过滤和投简历:
            with concurrent.futures.ThreadPoolExecutor(max_workers=cls.AI过滤岗位名线程数) as executor:
                results = list(executor.map(cls.过滤当前岗位, 岗位信息列表))
                过滤后的岗位列表 = [result for result in results if result is not None]
        else:
            for 单个岗位信息 in 岗位信息列表:
                result = cls.过滤当前岗位(单个岗位信息)
                if result is not None:
                    过滤后的岗位列表.append(result)
        return 过滤后的岗位列表
    @classmethod
    def 过滤当前岗位(cls, 单个岗位信息):
        # 过滤不合适的关键词
        if any(关键词 in cls.config['job_positions'] for 关键词 in cls.config['unsuitable_keywords']): 
            return None
        # 过滤范围外薪资
        # 
        if "k" in 单个岗位信息['job_salary'] or "K" in 单个岗位信息['job_salary']:
            if cls._获取岗位薪资(单个岗位信息)[0] < cls._获取我的期望薪资()[0] or cls._获取岗位薪资(单个岗位信息)[1] > cls._获取我的期望薪资()[1]:
                return None
        elif '天' in 单个岗位信息['job_salary']:
            # 映射为月薪
            # todo
            pass
        # 是否只要实习
        if cls.config['only_internship']: #如果配置了只实习
            if "实习" not in 单个岗位信息['job_name']: #如果岗位名称没有实习
                return None
            if cls.config['no_filter_internship']: #如果不用ai过滤 如果岗位名称有实习
                return 单个岗位信息
        # AI判断岗位是否匹配
        ai回答 = super().normal_get_response(cls._岗位与薪资是否匹配提示词(单个岗位信息))
        AIClasslog.info(f"AI判断岗位是否匹配: 岗位信息:{单个岗位信息['job_name']} 薪资:{单个岗位信息['job_salary']} AI回答:{ai回答}")
        if not ai回答:
            return None
        if ai回答.lower() == "true":
            return 单个岗位信息
        else:
            return None
    @classmethod
    def _获取岗位薪资(cls,单个岗位信息:dict):
        岗位的薪资=cls._提取薪资范围(单个岗位信息['job_salary'])
        return 岗位的薪资
    @classmethod
    def _获取我的期望薪资(cls):
        我的期望薪资=cls._提取薪资范围(cls.config['salary_range'])
        return 我的期望薪资
    @classmethod
    def _提取薪资范围(cls,targetstring:str):
        薪资范围=re.findall(r'\d+', targetstring)
        薪资范围=list(map(int, 薪资范围))
        return 薪资范围
    @classmethod
    def _岗位与薪资是否匹配提示词(cls,单个岗位信息:dict):
        return f'''你是一个经验丰富的HR，你的任务是判断当前招聘岗位和薪资水平是否和应聘者期望匹配。

请注意以下重要规则：
1. 岗位匹配原则：
   - 岗位名称与应聘者期望岗位的技术方向要匹配
   - 岗位要求的主要技能应与应聘者的技能背景相符
   - 如果是实习岗位，重点关注基础技能要求的匹配度
   - 如果职位描述中包含应聘者擅长的技术栈，应优先考虑

2. 薪资匹配规则：
   - 如果岗位没有标明具体薪资，则返回true
   - 如果薪资在应聘者期望范围内或以上，则返回true
   - 对于实习岗位可适当放宽薪资要求

3. 只需要输出true或false，不要有任何其他文字

基本信息：
当前招聘的岗位为"{单个岗位信息['job_name']}"，
招聘的岗位薪资为"{单个岗位信息['job_salary']}"，
我所期望的岗位为"{cls.config['job_positions']}"，
我所期望的薪资范围为"{cls.config['salary_range']}"。

请以发展潜力为导向进行评估，宁可错收，不可错过合适的机会。'''

@dataclass
class AI岗位处理类(APIResponse):
    config=配置类.读取toml文件('config.toml')
    匹配值=config['match_rate']
    @classmethod
    def 获取初步分析和最终匹配程度值(cls, 职位要求: str, 应聘者简历: str) -> tuple[str, bool]:
        初步分析=cls.获取初步分析岗位匹配值(职位要求, 应聘者简历)
        最终匹配程度值=cls.获取是否最终匹配(职位要求, 应聘者简历, 初步分析)
        return 初步分析, 最终匹配程度值
    @classmethod
    @判断返回是否符合要求(value_type="string")
    def 获取初步分析岗位匹配值(cls, 职位要求: str, 应聘者简历: str) -> Optional[str]:
        return super().normal_get_response(cls._初步分析提示词(职位要求, 应聘者简历))
    @classmethod
    @判断返回是否符合要求(value_type="bool")
    def 获取是否最终匹配(cls, 职位要求: str, 应聘者简历: str,初步分析: str) -> Optional[bool]:
        return super().normal_get_response(cls._最终分析提示词(职位要求, 应聘者简历, 初步分析))
    @classmethod
    def _初步分析提示词(cls, 职位要求: str, 应聘者简历: str) -> str:
        return f"""
        作为一位资深HR，请对以下候选人进行严格评估：

        职位要求：{职位要求}
        应聘者简历：{应聘者简历}

        请根据以下维度进行评估并给出两行回复：
        评估维度：
        1. 教育背景与专业（25%）
        2. 技术能力（40%）
        3. 工作经验（25%）
        4. 软实力（10%）

        第一行：只输出一个0到1之间的精确数值（保留两位小数），表示总体匹配度。
        第二行：推荐理由（200字以内）
        """
    @classmethod 
    def _最终分析提示词(cls, 职位要求: str, 应聘者简历: str, 初步分析: str) -> str:
        return f"""
        作为一位资深HR，请严格按照以下标准评估候选人与职位的匹配程度：

        职位要求：{职位要求}
        应聘者简历：{应聘者简历}
        初步分析：{初步分析}

        评估标准：
        1. 教育背景与专业要求的匹配度（权重25%）
        2. 技术能力与岗位需求的匹配度（权重40%）
        3. 工作经验年限与要求的匹配度（权重25%）
        4. 软实力（沟通能力、团队协作等）的匹配度（权重10%）

        请根据以上标准进行综合评分，如果总匹配度大于{cls.匹配值}则返回"true"，小于{1-cls.匹配值}则返回"false"。
        只需返回"true"或"false"，无需其他内容。
        """


@dataclass
class 测试类:
    @staticmethod
    def 测试用的职位要求():
        return """
    岗位名称：Python开发工程师

    岗位职责：
    1. 负责公司后台系统的开发和维护；
    2. 参与系统架构设计，优化系统性能；
    3. 编写相关的技术文档。

    任职要求：
    1. 计算机相关专业本科及以上学历；
    2. 熟练掌握Python，熟悉Django或Flask框架；
    3. 有至少2年以上的Python开发经验；
    4. 熟悉数据库设计与优化，掌握MySQL或PostgreSQL；
    5. 良好的团队合作精神和沟通能力。
    """
    @staticmethod
    def 测试用的应聘者简历():
        return """
    姓名：张三
    学历：本科，市场营销专业
    工作经验：
    1. 在ABC公司担任Java开发工程师1年，主要负责Web应用的开发，使用Spring框架；
    2. 熟悉Oracle数据库，参与过数据库设计和优化项目；
    3. 有良好的团队协作经验，参与过多个跨部门项目的开发。

    技能：
    - 熟悉Java编程；
    - 了解Spring框架；
    - 掌握Oracle数据库；
    - 了解前端技术，如HTML、CSS、JavaScript。

    自我评价：
    热爱技术，学习能力强，善于解决复杂问题，具有良好的沟通和协作能力。
    """




if __name__ == "__main__":
    AI岗位处理类.e()
    exit()
    初步分析=AIHr.获取初步分析岗位是否合适(测试类.测试用的职位要求(), 测试类.测试用的应聘者简历())
    print(初步分析)
    最终匹配程度值=AIHr.获取最终匹配程度值(测试类.测试用的职位要求(), 测试类.测试用的应聘者简历(),初步分析)
    print(最终匹配程度值)
    
