import time
import concurrent.futures
import json
import re
from dataclasses import dataclass
from 配置类 import 配置类
from AIClass import AI岗位处理类
# 读取配置文件
with open('./boss_config.json', 'r', encoding='utf-8') as f:
    BOSS_CONFIG = json.load(f)
with open('./city_list.json', 'r', encoding='utf-8') as f:
    CITY_LIST = json.load(f)
# 拿到简历内容
with open('./我的简历.txt', 'r', encoding='utf-8') as f:
    MY_RESUME = f.read()
@dataclass
class DPClass:
    config=配置类.读取toml文件('config.toml')
    打招呼自定义=config['custom_greeting']
    自动打招呼=config['auto_greeting']
    最大沟通次数=config['max_chat_count']
    匹配度=config['match_rate']
    过滤不活跃的HR=config['inactive_hr_filters']
    页查询次数=config['batch_count']
    是否使用自定义打招呼=config['auto_greeting_setting']
    @classmethod
    def 处理单个岗位(cls,单个岗位信息,tab):
        if cls.打开岗位页面判断是否活跃(tab,单个岗位信息):
            是否沟通,初步分析结果=cls.尝试沟通当前HR页面岗位(tab,MY_RESUME)
            return 是否沟通,f'是否沟通：{是否沟通} 岗位信息：{单个岗位信息} 初步分析结果：{初步分析结果}'
        return False,f'当前岗位不活跃：岗位信息：{单个岗位信息}'

    @classmethod
    def 尝试沟通当前HR页面岗位(cls,tab,我的简历)->tuple[bool,str]:
        岗位要求=获取详细信息(tab)
        初步分析结果,是否推荐=AI岗位处理类.获取初步分析和最终匹配程度值(岗位要求,我的简历)
        推荐指数=cls._获取推荐指数(初步分析结果)
        if 推荐指数>=cls.匹配度:
            # 点击立即沟通
            try:
                tab.ele('text:立即沟通').click()
            except:
                return False,初步分析结果
            # 判断是否设置了自动招呼
            # #chat-input
            if not cls.是否使用自定义打招呼:
                time.sleep(3)
                tab.ele('#chat-input').input(cls.打招呼自定义+"\n") 
                time.sleep(6)
                return True,f'推荐指数为：{推荐指数} 初步分析结果：{初步分析结果}'
            # 处理自动打招呼
            if cls.自动打招呼:
                if cls.打招呼自定义:
                    # tab.ele('.btn btn-sure').click()
                    # tab.ele('#chat-input').input(cls.打招呼自定义+"\n")
                    tab.ele('.input-area').input(cls.打招呼自定义+"\n")
            return True,f'推荐指数为：{推荐指数} 初步分析结果：{初步分析结果}'
        else:
            return False,f'推荐指数为：{推荐指数} 初步分析结果：{初步分析结果}'
    @classmethod
    def 打开岗位页面判断是否活跃(cls,tab,单个岗位信息)->bool:
        打开页面(tab,单个岗位信息['job_link'])
        等待元素加载完成(tab,'text:立即沟通')
        if cls.判断当前HR是否活跃(tab):
            return True
        return False
    @classmethod
    def 判断当前HR是否活跃(cls,tab)->bool:
        if cls.检查HR是否在线(tab):
            return True
        hr_active_time = 找一个元素的属性(tab,'tag:span@class=boss-active-time','text').strip()
        if hr_active_time not in cls.过滤不活跃的HR:
            return True
        return False
    @classmethod
    def 检查HR是否在线(cls,tab):
        有在线状态标签=找一个元素(tab,'tag:span@class=boss-online-tag')
        if 有在线状态标签:
            在线状态=有在线状态标签.text.strip()
            return bool('在线' in 在线状态)
        return False
    @classmethod
    def 找工作需求(cls,tab):
        return 找一个元素的文本(tab,'tag:div@class=job-sec-text')
    @classmethod
    def 随机查询岗位信息(cls,tab):
        岗位信息列表=[]
        for _ in range(cls.页查询次数):
            json_data=cls.随机查询岗位返回json数据(tab)
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
    @classmethod
    def 随机查询岗位返回json数据(cls,tab):
        # 从配置中获取查询参数
        params = {
            "query": cls.config.get("job_positions", ["python"])[0],     # 取第一个岗位
            "page": cls.config.get("page", 1),                           # 页码
            "pageSize": cls.config.get("items_per_page", 30),            # 每页数量
            "city": cls.config.get("target_cities", ["0"])[0],           # 取第一个城市
            "experience": cls.config.get("experience_requirement", "0"), # 经验要求
            "degree": cls.config.get("education_requirement", "0"),      # 学历要求
            "salary": cls.config.get("search_salary_range", "0"),        # 薪资范围
            "partTime": cls.config.get("job_type", "0"),                 # 工作类型
            "industry": cls.config.get("industry", "0")                  # 行业
        }
        # 构造BOSS直聘API的查询URL
        url = (
            "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?"
            "scene=1"
            f"&query={params['query']}"
            f"&city={params['city']}"
            f"&experience={params['experience']}"
            "&payType="
            f"&partTime={params['partTime']}"
            f"&degree={params['degree']}"
            f"&industry={params['industry']}"
            "&scale=&stage=&position=&jobType="
            f"&salary={params['salary']}"
            "&multiBusinessDistrict=&multiSubway="
            f"&page={params['page']}"
            f"&pageSize={params['pageSize']}"
        )

        # 发送请求并解析返回的JSON数据
        tab.get(url)
        json_data=json.loads(tab.ele('tag:pre').text)
        return json_data
    @classmethod
    def 获取岗位信息点击按钮版(cls, tab):
        try:
            tab.get(cls._构建查询URL(str(cls.config['target_cities'][0]), str(cls.config['job_positions'][0])))
            return []
            岗位信息列表 = []
            下一页次数=cls.config['next_page_count']
            while True:
                if 下一页次数 <= 0:
                    break
                岗位卡片列表 = 找多个元素(tab, 'tag:li@class=job-card-wrapper')
                for 岗位卡片 in 岗位卡片列表:
                    岗位信息列表.append(cls._提取岗位信息(岗位卡片))
                if not cls._检查是否有下一页(tab):
                    break
                下一个按钮=找一个元素(tab, '.ui-icon-arrow-right')
                下一个按钮.click()
                下一页次数 -= 1
        except:
            return []
        return 岗位信息列表
    @classmethod
    def _获取推荐指数(cls,初步分析结果):
        # 用正则表达式获取推荐指数后第一个小数
        推荐指数=re.search(r'(\d+\.\d+)',初步分析结果)
        if 推荐指数:
            推荐指数=float(推荐指数.group(1))
            return 推荐指数
        return 0
    @classmethod
    def _构建查询URL(cls,城市, 岗位):
        return f"https://www.zhipin.com/web/geek/job?city={城市}&query={岗位}"
    @classmethod
    def _提取岗位信息(cls,岗位卡片):
        return {
            'job_name': 找一个元素的属性(岗位卡片, 'tag:span@class=job-name', 'text'),
            'job_salary': 找一个元素的属性(岗位卡片, 'tag:span@class=salary', 'text'), 
            'job_link': 找一个元素的属性(岗位卡片, 'tag:a@class=job-card-left', 'href')
        }
    @classmethod
    def _检查是否有下一页(cls,tab):
        try:
            下一页按钮 = 找一个元素(tab, '.ui-icon-arrow-right')
            没有下一页标识 = 找一个元素的属性(下一页按钮.parent(), None, 'class')
            if "disabled" in 没有下一页标识:
                return False
        except:
            return False
        return True

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

def 获取岗位信息点击按钮版(page,config):

    下一页次数=config['下一页次数']
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
        if 下一页次数<=0:
            break
        try:
            下一页按钮 = 找一个元素(page,'.ui-icon-arrow-right')
            没有下一页标识=找一个元素的属性(下一页按钮.parent(),None,'class')
            if "disabled" in 没有下一页标识:
                break
            下一页按钮.click()
            下一页次数-=1
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

def 获取详细信息(tab):
    return tab.ele('.job-detail-section').text
        
def 关闭自动打招呼沟通(tab,自定义打招呼):
    tab.ele('.input-area').input(自定义打招呼+'\n')


if __name__ == "__main__":
    pass