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
        职位要求：{job_requirements}
        应聘者简历：{user_requirements}
        初步分析：{first_response}
        请结合以上信息和分析结果，精准判断应聘者是否与岗位匹配，如果匹配值大于"{匹配值大于}"则返回"true"，匹配值小于"{1-匹配值大于}"则返回"false"，不要输出任何多余内容，只输出true或false。
        """
    else:
        content = f"""
        作为一个经验丰富的HR，请根据以下信息进行分析：
        
        职位要求：{job_requirements}
        应聘者简历：{user_requirements}
        
        请给出：
        1. 推荐指数（0-1之间的数值）
        2. 推荐理由（200字以内）
        """
    
    return 获取ai回答(content)

def ai检查岗位匹配度(元素,my_resume,匹配度=0.7):
    岗位要求=drissionpage_utils.找工作需求(元素)
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
        # 严格控制薪资在范围内 前提是目标岗位薪资有k
        我的薪资范围=config['薪资范围']
        我的薪资范围=re.findall(r'\d+', 我的薪资范围)
        我的薪资范围=list(map(int, 我的薪资范围))
        
        岗位的薪资=re.findall(r'\d+', 单个岗位信息['job_salary'])
        岗位的薪资=list(map(int, 岗位的薪资))
        if 岗位的薪资[0] < 我的薪资范围[0] or 岗位的薪资[1] > 我的薪资范围[1]:
            if "k" in 单个岗位信息['job_salary']:
                os_utils.写入日志(f"薪资范围不匹配 岗位名称:{单个岗位信息['job_name']} 岗位薪资:{单个岗位信息['job_salary']} 我的薪资范围:{我的期望薪资}", 是否打印=False, 是否写入文件=True)
                return None
        # ai判断岗位是否匹配
        content = f'''你是一个经验丰富的HR，你的任务是判断当前招聘岗位和薪资水平是否和我所期望的岗位匹配。
                        请注意以下重要规则：
                        1. 如果是实习岗位，只要岗位名称相关就一定要输出true
                        2. 岗位名称包含我期望岗位的关键词就可以认为匹配
                        3. 模糊匹配即可，不需要完全一致
                        4. 只需要输出true或false，不要有任何其他文字
                        
                        基本信息：
                        当前招聘的岗位为"{单个岗位信息['job_name']}"，
                        招聘的岗位薪资为"{单个岗位信息['job_salary']}"，
                        我所期望的岗位为"{我的期望岗位}"，
                        我所期望的薪资范围为"{config['薪资范围']}"。
                        
                        请记住：如果岗位名称相关或包含"实习"字样，尽量返回true。'''
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=线程数) as executor:
        results = list(executor.map(多线程处理单个岗位, 岗位信息列表))
        过滤后的岗位列表 = [result for result in results if result is not None]
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
    