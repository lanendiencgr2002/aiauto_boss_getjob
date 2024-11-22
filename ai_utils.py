import aiohttp
import asyncio
import os_utils
import drissionpage_utils
import time
import concurrent.futures
import re
def 获取ai回答(content):
    """
    使用本地 FastAPI 接口发送请求获取 AI 回答
    """
    async def get_response():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5000/chat",
                json={"问题": content}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"]["message"]
                else:
                    return None

    # 在同步函数中运行异步代码
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(get_response())


def 模拟HR进行简历筛选(
    job_requirements, 
    user_requirements, 
    first_response = None, 
    data_analysis = False,
    匹配值大于=0.7
):
    """
    模拟HR进行简历筛选的AI函数
    
    参数:
        job_requirements: 职位要求
        user_requirements: 应聘者简历
        first_response: 初步分析的结果（可选）
        data_analysis: 是否需要进行最终的匹配度分析
    返回:
        str: AI的分析结果
    """
    
    # 构建消息内容
    if data_analysis:
        content = f"""
        作为一位资深HR，请严格按照以下标准评估候选人与职位的匹配程度：

        职位要求：{job_requirements}
        应聘者简历：{user_requirements}
        初步分析：{first_response}

        评估标准：
        1. 教育背景与专业要求的匹配度（权重25%）
        2. 技术能力与岗位需求的匹配度（权重40%）
        3. 工作经验年限与要求的匹配度（权重25%）
        4. 软实力（沟通能力、团队协作等）的匹配度（权重10%）

        请根据以上标准进行综合评分，如果总匹配度大于{匹配值大于}则返回"true"，小于{1-匹配值大于}则返回"false"。
        只需返回"true"或"false"，无需其他内容。
        """
    else:
        content = f"""
        作为一位资深HR，请对以下候选人进行严格评估：

        职位要求：{job_requirements}
        应聘者简历：{user_requirements}

        请根据以下维度进行评估并给出两行回复：
        评估维度：
        1. 教育背景与专业（25%）
        2. 技术能力（40%）
        3. 工作经验（25%）
        4. 软实力（10%）

        第一行：只输出一个0到1之间的精确数值（保留两位小数），表示总体匹配度。
        第二行：推荐理由（200字以内）
        """
    
    return 获取ai回答(content)

def ai检查岗位匹配度(岗位要求,my_resume,匹配度=0.7):
    初步分析结果 = 模拟HR进行简历筛选(岗位要求, my_resume)
    最终分析结果 = 模拟HR进行简历筛选(岗位要求, my_resume, 初步分析结果, data_analysis=True,匹配值大于=匹配度)
    return 初步分析结果,最终分析结果

def AI过滤岗位(岗位信息列表,config,线程数=100):
    我的期望岗位=config['要查询的岗位']
    我的期望薪资=config['薪资范围']
    不合适岗位关键词=config['不合适岗位关键词']
    def 多线程处理单个岗位(单个岗位信息):
        # 如果岗位名称包含不合适的关键词，则跳过该岗位
        if any(关键词 in 我的期望岗位 for 关键词 in 不合适岗位关键词): 
            os_utils.写入日志(f"不合适岗位关键词:{不合适岗位关键词} 岗位名称:{单个岗位信息['job_name']}", 是否打印=False, 是否写入文件=True)
            return None
        # 过滤控制薪资在范围内 前提是目标岗位薪资有k
        我的薪资范围=config['薪资范围']
        我的薪资范围=re.findall(r'\d+', 我的薪资范围)
        我的薪资范围=list(map(int, 我的薪资范围))
        岗位的薪资=re.findall(r'\d+', 单个岗位信息['job_salary'])
        岗位的薪资=list(map(int, 岗位的薪资))
        if 岗位的薪资[0] < 我的薪资范围[0] or 岗位的薪资[1] > 我的薪资范围[1]:
            if "k" in 单个岗位信息['job_salary']:
                os_utils.写入日志(f"薪资范围不匹配 岗位名称:{单个岗位信息['job_name']} 岗位薪资:{单个岗位信息['job_salary']} 我的薪资范围:{我的期望薪资}", 是否打印=False, 是否写入文件=True)
                return None
        # 如果一定只要实习，和是否只实习不用ai过滤
        if config['一定只要实习吗']: #如果配置了只实习
            if "实习" not in 单个岗位信息['job_name']: #如果岗位名称没有实习
                os_utils.写入日志(f"一定只要实习，且岗位名称没有实习 岗位名称:{单个岗位信息['job_name']}", 是否打印=False, 是否写入文件=True)
                return None
            if config['实习就行不用ai过滤']: #如果不用ai过滤 如果岗位名称有实习
                os_utils.写入日志(f"一定只要实习，且实习就行不用ai过滤，这个可以 岗位名称:{单个岗位信息['job_name']}", 是否打印=False, 是否写入文件=True)
                return 单个岗位信息
            

        # ai判断岗位是否匹配
        content = f'''你是一个经验丰富的HR，你的任务是判断当前招聘岗位和薪资水平是否和应聘者期望匹配。

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
我所期望的岗位为"{我的期望岗位}"，
我所期望的薪资范围为"{config['薪资范围']}"。

请以发展潜力为导向进行评估，宁可错收，不可错过合适的机会。'''
        ai回答 = 获取ai回答(content)
        if not ai回答:
            os_utils.写入日志(f"AI回答为空 岗位名称:{单个岗位信息['job_name']}", 是否打印=False, 是否写入文件=True)
            return None
        if ai回答.lower() == "true":
            os_utils.写入日志(f"AI判断匹配 岗位名称:{单个岗位信息['job_name']}", 是否打印=False, 是否写入文件=True)
            return 单个岗位信息
        else:
            os_utils.写入日志(f"AI判断不匹配 岗位名称:{单个岗位信息['job_name']} 岗位薪资:{单个岗位信息['job_salary']}", 是否打印=False, 是否写入文件=True)
            return None
    过滤后的岗位列表=[]
    if config['用多线程ai过滤和投简历']:
        with concurrent.futures.ThreadPoolExecutor(max_workers=线程数) as executor:
            results = list(executor.map(多线程处理单个岗位, 岗位信息列表))
            过滤后的岗位列表 = [result for result in results if result is not None]
            return 过滤后的岗位列表
    else:
        for 单个岗位信息 in 岗位信息列表:
            过滤后的岗位列表.append(多线程处理单个岗位(单个岗位信息))
        return 过滤后的岗位列表

# 测试代码部分
if __name__ == "__main__":
    # 测试用的职位要求
    job_requirements = """
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
    
    # 测试用的简历信息
    user_requirements = """
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
    
    # 执行测试
    first_response = ai_hr(job_requirements, user_requirements)
    print("初步分析结果:", first_response)
    
    final_analysis = ai_hr(job_requirements, user_requirements, first_response, data_analysis=True)
    print("最终分析结果:", final_analysis)
    