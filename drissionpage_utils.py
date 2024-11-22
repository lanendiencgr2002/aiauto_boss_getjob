import time
import concurrent.futures
import json
import ai_utils
import re
# 读取配置文件
with open('./boss_config.json', 'r', encoding='utf-8') as f:
    BOSS_CONFIG = json.load(f)
with open('./city_list.json', 'r', encoding='utf-8') as f:
    CITY_LIST = json.load(f)

def 通用等待(检查函数, 错误信息, 超时=10):
    剩余时间 = 超时
    while True:
        try:
            if 检查函数():
                break
            time.sleep(1)
            剩余时间 -= 1
            if 剩余时间 < 0:
                raise Exception(f"{错误信息}，超时{超时}秒，退出循环。")
        except Exception as e:
            if 剩余时间 < 0:
                raise e
            time.sleep(1)
            剩余时间 -= 1

def 等待元素加载完成(page, 条件:str, 超时=10):
    """等待页面元素加载完成"""
    def 检查元素存在():
        page.ele(条件)
        return True
    
    通用等待(
        检查元素存在,
        f"等待元素加载完成：{条件}",
        超时
    )

def 等待跳转到指定页面(page, 目标url列表, 超时=10):
    """等待页面跳转到目标URL"""
    def 检查页面URL():
        if page.url in 目标url列表:
            return True
        return False
    
    通用等待(
        检查页面URL,
        f"等待跳转目标页面：{page.url}",
        超时
    )

def 打开指定页面并等待跳转到指定页面(page, 目标url):
    打开页面(page, 目标url)
    等待跳转到指定页面(page, [目标url])

def 打开页面(page, 目标url):
    page.get(目标url)

def 找一个元素(page, 条件:str):
    try:
        return page.ele(条件)
    except:
        return None

def 找多个元素(page, 条件:str):
    return page.eles(条件)

def 获取元素文本(元素):
    return 元素.text.strip()

def 获取元素地址(元素):
    return 元素.link

def 找一个元素的属性(元素, 条件, 属性):
    try:
        if 条件==None:
            return 元素.attr(属性)
        else:
            return 找一个元素(元素,条件).attr(属性)
    except:
        return None

def 找一个元素的文本(元素,条件:str):
    return 找一个元素的属性(元素,条件,'text')

def 创建多个标签页对象(page,标签页数量=5):
    return [page.new_tab() for _ in range(标签页数量)]

def 获取岗位信息点击按钮版(page,config,一页调试功能=False):
    url="https://www.zhipin.com/web/geek/job?"+"city="+str(config['要查询的城市'])+"&query="+str(config['要查询的岗位'])
    page.get(url)
    岗位信息列表 = []
    while True: 
        岗位卡片列表 = 找多个元素(page,'tag:li@class=job-card-wrapper')
        for 岗位卡片 in 岗位卡片列表:
            岗位名字= 找一个元素的属性(岗位卡片,'tag:span@class=job-name','text')
            岗位薪资 = 找一个元素的属性(岗位卡片,'tag:span@class=salary','text')
            岗位链接 = 找一个元素的属性(岗位卡片,'tag:a@class=job-card-left','href')
            岗位信息列表.append({
                'job_name': 岗位名字,
                'job_salary': 岗位薪资,
                'job_link': 岗位链接
            })
        if 一页调试功能:break
        try:
            下一页按钮 = 找一个元素(page,'.ui-icon-arrow-right')
            没有下一页标识=找一个元素的属性(下一页按钮.parent(),None,'class')
            if "disabled" in 没有下一页标识:
                break
            下一页按钮.click()
        except:
            break
    return 岗位信息列表

def 获取岗位信息(page,搜索的url,新标签页数量=10,一页调试功能=False):
    def 拼接上分页查询url(url,页码):
        return url + f"&page={页码}" 
    def 获取岗位信息(标签页,url,一页调试功能=False):
        标签页.listen.start()
        标签页.get(url)
        岗位信息列表 = []
        标签页.listen.wait_silent(timeout=10)
        for i in 标签页.listen.steps():
            if i.url.startswith("https://www.zhipin.com/wapi/zpgeek/history/joblist.json"):
                print(i.url)
                json_data = json.loads(i.response.body)['zpData']['jobList']
                for job in json_data:
                    岗位信息列表.append({
                        'job_name': job['jobName'],
                        'job_salary': job['salary'],
                        'job_link': job['jobUrl']
                    })
                break
        print(岗位信息列表)
        return 岗位信息列表
        
    标签页列表 = 创建多个标签页对象(page,新标签页数量)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=新标签页数量) as executor:
        futures = []
        for index,标签页 in enumerate(标签页列表):
            future = executor.submit(获取岗位信息, 标签页,拼接上分页查询url(搜索的url, index+1),一页调试功能)
            futures.append(future)
        concurrent.futures.wait(futures)
    return 

def 根据岗位id查询岗位信息(page,岗位id):
    url = f"https://www.zhipin.com/wapi/zpgeek/history/joblist.json?jobIds={岗位id}"
    page.get(url)
    json_data = json.loads(page.response.body)['zpData']['jobList']
    for i in json_data:
        print(i)
    return 

def 随机查询岗位返回json数据(元素, config):
    """
    通过BOSS直聘API查询岗位信息并返回JSON数据
    
    参数:
        元素: DrissionPage页面对象
        **kwargs: 可选的查询参数
            - 岗位: 查询的职位名称,默认为"python" 
            - 页码: 分页页码,默认为1
            - 每页数量: 每页返回的岗位数量,默认为30
            - 城市编号: 城市代码,默认为"0"(全国)
            - 经验要求: 工作经验要求,默认为"0"(不限)
            - 学历要求: 学历要求,默认为"0"(不限)
            - 薪资范围: 薪资范围,默认为"0"(不限)
            - 工作类型: 全职/兼职/实习,默认为"0"(不限)
            - 行业: 行业类型,默认为"0"(不限)
    
    返回:
        dict: BOSS直聘API返回的JSON数据
    """
    # 设置API查询的默认参数
    params = {
        "岗位": config.get("要查询的岗位", "python"),
        "页码": config.get("页码", 1),
        "每页数量": config.get("每页数量", 30),
        "城市编号": config.get("要查询的城市", "0"),
        "经验要求": config.get("经验要求", "0"),
        "学历要求": config.get("学历筛选", "0"),
        "薪资范围": config.get("查找薪资范围", "0"),
        "全职兼职实习": config.get("工作类型", "0"),
        "行业": config.get("行业", "0")
    }

    # 构造BOSS直聘API的查询URL
    url = (
        f"https://www.zhipin.com/wapi/zpgeek/search/joblist.json?"
        f"scene=1"
        f"&query={params['岗位']}"
        f"&city={params['城市编号']}"
        f"&experience={params['经验要求']}"
        f"&payType="
        f"&partTime={params['全职兼职实习']}"
        f"&degree={params['学历要求']}"
        f"&industry={params['行业']}"
        f"&scale=&stage=&position=&jobType="
        f"&salary={params['薪资范围']}"
        f"&multiBusinessDistrict=&multiSubway="
        f"&page={params['页码']}"
        f"&pageSize={params['每页数量']}"
    )
    
    # 发送请求并解析返回的JSON数据
    元素.get(url)
    json_data=json.loads(元素.ele('tag:pre').text)
    return json_data

def 随机查询岗位信息(元素,config):
    """
    通过BOSS直聘API查询岗位信息并返回JSON数据
    
    参数:
        元素: DrissionPage页面对象
        **kwargs: 可选的查询参数
            - 岗位: 查询的职位名称,默认为"python" 
            - 页码: 分页页码,默认为1
            - 每页数量: 每页返回的岗位数量,默认为30
            - 城市编号: 城市代码,默认为"0"(全国)
            - 经验要求: 工作经验要求,默认为"0"(不限)
            - 学历要求: 学历要求,默认为"0"(不限)
            - 薪资范围: 薪资范围,默认为"0"(不限)
            - 工作类型: 全职/兼职/实习,默认为"0"(不限)
            - 行业: 行业类型,默认为"0"(不限)
    
    返回:
        list: 'job_name':str, 'job_salary':str, 'job_link':str, 'job_experience':str, 'job_degree':str, 'job_encryptid':str
    """
    岗位信息列表=[]
    for _ in range(config['30的次数']):
        json_data=随机查询岗位返回json数据(元素, config)
        if json_data["code"]==0:
            岗位列表=json_data['zpData']['jobList']
            for 岗位 in 岗位列表:
                岗位信息列表.append({
                    'job_name': 岗位['jobName'],
                    'job_salary': 岗位['salaryDesc'],
                    'job_link': "https://www.zhipin.com/job_detail/"+岗位['encryptJobId'],
                    'job_experience': 岗位['jobExperience'],
                    "job_degree": 岗位['jobDegree'],
                    "job_encryptid": 岗位['encryptJobId']
                })
    return 岗位信息列表

def 检查HR是否在线(元素):
    # return bool(soup.find('span', class_='boss-online-tag') 
    #                    and '在线' in soup.find('span', class_='boss-online-tag').text.strip())

    有在线状态标签=找一个元素(元素,'tag:span@class=boss-online-tag')
    if 有在线状态标签:
        在线状态=有在线状态标签.text.strip()
        return bool('在线' in 在线状态)
    return False

def 找工作需求(元素):
    return 找一个元素的文本(元素,'tag:div@class=job-sec-text')


def AI决定是否与HR沟通(标签页,my_resume,config):
    '''
    自动ai判断是否推荐，如果推荐则立即沟通
    '''
    匹配度=config['匹配度']
    岗位要求=获取详细信息(标签页)
    初步分析结果,是否推荐=ai_utils.ai检查岗位匹配度(岗位要求,my_resume,匹配度=匹配度)
    # 用正则表达式获取推荐指数后第一个小数
    推荐指数=re.search(r'(\d+\.\d+)',初步分析结果)
    if 推荐指数:
        推荐指数=float(推荐指数.group(1))
        if 推荐指数>=匹配度 and 是否推荐.lower() == "true":
            立即沟通=标签页.ele('text:立即沟通')
            if 立即沟通:
                立即沟通.click()
            else:
                return False,初步分析结果
            已自定义打招呼=False
            if config['自动打招呼']==False:
                关闭自动打招呼沟通(标签页,config['打招呼自定义'])
                已自定义打招呼=True
            if config['打招呼自定义'] and 已自定义打招呼==False:
                标签页.ele('.btn btn-sure').click()
                标签页.ele('#chat-input').input(config['打招呼自定义']+"\n")
            return True,初步分析结果
    return False,初步分析结果

def 判断当前HR是否活跃(元素,config):
    if 检查HR是否在线(元素):
        return True
    hr_active_time = 找一个元素的属性(元素,'tag:span@class=boss-active-time','text').strip()
    if hr_active_time not in config['过滤不活跃的HR']:
        return True
    return False

def 获取详细信息(tab):
    return tab.ele('.job-detail-section').text
        
def 关闭自动打招呼沟通(tab,自定义打招呼):
    tab.ele('.input-area').input(自定义打招呼+'\n')
