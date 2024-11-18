import aiohttp
import asyncio

def ai_response(content):
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


def ai_hr(
    job_requirements, 
    user_requirements, 
    first_response = None, 
    data_analysis = False
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
        请结合以上信息和分析结果，精准判断应聘者是否与岗位匹配，如果匹配值大于"0.5"则返回"true"，匹配值小于"0.5"则返回"false"，不要输出任何多余内容，只输出true或false。
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
    
    return ai_response(content)

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
    