import time
import concurrent.futures
import drissionpage_utils
import os_utils
import ai_utils
from DrissionPage import ChromiumPage, ChromiumOptions
from threading import Lock

log_print = False
is_really_write_log = True

def 初始化dp():
    co = ChromiumOptions().set_local_port(9222)
    co.set_timeouts(base=3)
    page = ChromiumPage(addr_or_opts=co)
    return page

page = 初始化dp()

try:
    config, my_resume = os_utils.读取配置()
    # 从配置文件读取日志设置
    log_print = config.get('日志打印', False)
    is_really_write_log = config.get('日志写入文件', True)
except Exception as e:
    print(f"读取配置失败: {e}")
    exit(1)

def 登录():
    drissionpage_utils.打开指定页面并等待跳转到指定页面(page,"https://www.zhipin.com/web/geek/job-recommend")
    drissionpage_utils.等待跳转到指定页面(page,["https://www.zhipin.com/web/geek/job-recommend","https://www.zhipin.com"])
    os_utils.写入日志(
        f"登录成功！时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 
        是否打印=log_print,
        是否写入文件=is_really_write_log
    )

def 开投():
    投递次数 = 0
    投递锁 = Lock()
    检查次数锁 = Lock()
    
    os_utils.写入统计日志(f"开始运行时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)
    def 处理单个岗位(单个岗位信息,新标签页对象):
        nonlocal 投递次数
        global log_print
        global is_really_write_log
        drissionpage_utils.打开页面(新标签页对象,单个岗位信息['job_link'])
        drissionpage_utils.等待元素加载完成(新标签页对象,'text:立即沟通')
        if drissionpage_utils.判断当前HR是否活跃(新标签页对象,config):
            with 检查次数锁:
                if 投递次数 > config['最大沟通次数']:
                    return False
            os_utils.写入日志(f"当前HR活跃，开始与HR沟通  岗位名字：{单个岗位信息['job_name']}", 是否打印=log_print, 是否写入文件=is_really_write_log)
            是否沟通,初步分析结果=drissionpage_utils.AI决定是否与HR沟通(新标签页对象,my_resume,config)
            if 是否沟通:
                os_utils.写入日志(f"AI决定与HR沟通  岗位名字：{单个岗位信息['job_name']}", 是否打印=log_print, 是否写入文件=is_really_write_log)
                岗位详情=drissionpage_utils.找工作需求(新标签页对象)
                os_utils.写入日志(初步分析结果, 是否打印=log_print, 是否写入文件=is_really_write_log)
                os_utils.写入已投递岗位(初步分析结果, 是否打印=log_print, 是否写入文件=is_really_write_log)
                os_utils.写入已投递岗位(f"岗位名字：{单个岗位信息['job_name']} 岗位详情：{岗位详情}\n\n\n", 是否打印=log_print, 是否写入文件=is_really_write_log)
                with 投递锁:
                    投递次数 += 1
                    os_utils.写入日志(f"当前投递次数：{投递次数}", 是否打印=True, 是否写入文件=is_really_write_log)
                    if 投递次数 > config['最大沟通次数']:
                        return True
                return True
        return False
    城市列表=config['要查询的城市']
    岗位列表=config['要查询的岗位']
    新标签页列表 = drissionpage_utils.创建多个标签页对象(page,config['标签页数量'])
    总共查询数量=0
    总共经过ai过滤数量=0
    while 投递次数<=config['最大沟通次数']:
        一轮投递次数=投递次数
        一轮查询次数=0
        一轮ai过滤次数=0
        for 岗位 in 岗位列表:
            config['要查询的岗位']=岗位
            for 城市 in 城市列表:
                config['要查询的城市']=城市
                岗位信息列表=[]
                开始时间=time.time()
                岗位信息列表+=drissionpage_utils.随机查询岗位信息(page,config)
                for _ in range(config['30次数超级加倍']):
                    岗位信息列表+=drissionpage_utils.获取岗位信息点击按钮版(page,config)
                    岗位信息列表+=drissionpage_utils.随机查询岗位信息(page,config)
                print(f"查询岗位信息时间：{time.time()-开始时间}")
                总共查询数量+=len(岗位信息列表)
                一轮查询次数+=len(岗位信息列表)
                os_utils.写入统计日志(f"随机查询岗位信息列表个数:{len(岗位信息列表)} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)
                os_utils.写入日志(f"随机查询岗位信息:{岗位}岗位信息列表个数:{len(岗位信息列表)}", 是否打印=log_print, 是否写入文件=is_really_write_log)
                岗位信息列表=ai_utils.AI过滤岗位(岗位信息列表,config,线程数=100)
                总共经过ai过滤数量+=len(岗位信息列表)
                一轮ai过滤次数+=len(岗位信息列表)
                # 去掉岗位信息列表None元素
                岗位信息列表 = [x for x in 岗位信息列表 if x is not None]
                os_utils.写入统计日志(f"AI过滤初步后岗位列表个数:{len(岗位信息列表)} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)
                os_utils.写入日志(f"AI过滤后的岗位:{岗位}岗位信息列表个数:{len(岗位信息列表)}", 是否打印=log_print, 是否写入文件=is_really_write_log)
                if config['用多线程ai过滤和投简历']:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=len(新标签页列表)) as executor:
                        futures = []
                        for i, 单个岗位信息 in enumerate(岗位信息列表):
                            标签页 = 新标签页列表[i % len(新标签页列表)]
                            future = executor.submit(处理单个岗位, 单个岗位信息, 标签页)
                            futures.append(future)
                        concurrent.futures.wait(futures)
                else:
                    for 单个岗位信息 in 岗位信息列表:
                        处理单个岗位(单个岗位信息, 新标签页列表[0])
        一轮投递次数=投递次数-一轮投递次数
        os_utils.写入统计日志(f"一轮查询结束，一轮投递次数：{一轮投递次数} 一轮查询数量:{一轮查询次数} 一轮经过ai过滤数量:{一轮ai过滤次数} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)   
    os_utils.写入统计日志(f"总共查询数量:{总共查询数量} 总共经过ai过滤数量:{总共经过ai过滤数量} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)   
    os_utils.写入统计日志(f"投递次数：{投递次数} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)   
    for 标签页 in 新标签页列表:
        标签页.close()
    if config['最大沟通次数']>0:
        os_utils.写入统计日志(f"投递次数：{投递次数} 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 是否打印=log_print, 是否写入文件=is_really_write_log)
def 启动():
    if is_really_write_log:
        os_utils.清空本次面试运行日志()
    os_utils.写入日志(
        f"开始运行时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}", 
        模式='w', 
        是否打印=log_print,
        是否写入文件=is_really_write_log
    )
    登录()
    开投()

if __name__ == "__main__":
    启动()