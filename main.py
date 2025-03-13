import time
import concurrent.futures
import queue
from 日志类 import LoggerManager
from 配置类 import 配置类
from DPClass import DPClass
from dp标签类 import Dp标签类
from AIClass import AI初步过滤类
import threading
page=Dp标签类.dp配置()
最终日志类=LoggerManager(name="最终沟通日志").get_logger()
# 统计日志类=LoggerManager(name="统计日志").get_logger()
config=配置类.读取toml文件('config.toml')
投递次数 = 0

def result_consumer(queue, stop_event):
    """结果消费者线程"""
    global 投递次数
    while not stop_event.is_set():
        if not queue.empty():
            result = queue.get()
            投递次数 += 1
            最终日志类.info(f"实时处理完成的岗位: {result}")
        time.sleep(.5)  # 避免空转消耗CPU

def main():
    global 投递次数
    # 创建结果队列
    result_queue = queue.Queue()
    stop_event = threading.Event()
    新标签页列表=Dp标签类.创建多个标签页对象(page,config['tab_count'])
    # 启动消费者线程
    consumer = threading.Thread(target=result_consumer, args=(result_queue, stop_event))
    consumer.start()
    try:
        while 投递次数<=config['max_chat_count']:
            for todo城市 in config['job_positions']:
                for todo岗位 in config['target_cities']:
                    岗位信息列表=DPClass.随机查询岗位信息(新标签页列表[0])
                    岗位信息列表+=DPClass.获取岗位信息点击按钮版(新标签页列表[0])
                    岗位信息列表=AI初步过滤类.过滤岗位列表(岗位信息列表)
                    # 尝试沟通
                    if config['use_multi_thread']:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=len(新标签页列表)) as executor:
                            futures = []
                            for i, 单个岗位信息 in enumerate(岗位信息列表):
                                if 投递次数>=config['max_chat_count']:
                                    break
                                标签页 = 新标签页列表[i % len(新标签页列表)]
                                # 包装处理函数,将结果放入队列
                                def process_job_wrapper(job_info, tab):
                                    try:
                                        是否沟通,初步分析结果 = DPClass.处理单个岗位(job_info, tab)
                                        result_queue.put((是否沟通,初步分析结果))
                                    except Exception as e:
                                        最终日志类.error(f"处理岗位时发生错误: {str(e)}")
                                future = executor.submit(process_job_wrapper, 单个岗位信息, 标签页)
                                futures.append(future)
                            concurrent.futures.wait(futures)
                    else:
                        for 单个岗位信息 in 岗位信息列表:
                            if 投递次数>=config['max_chat_count']:
                                break
                            标签页 = 新标签页列表[i % len(新标签页列表)]
                            是否沟通,初步分析结果=DPClass.处理单个岗位(单个岗位信息, 标签页)
                            result_queue.put((是否沟通,初步分析结果))
    finally:
        stop_event.set()
        consumer.join()

if __name__ == "__main__":
    main()