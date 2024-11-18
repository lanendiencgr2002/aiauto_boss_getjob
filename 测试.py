import drissionpage_utils
import main
import time
from DrissionPage import ChromiumPage, ChromiumOptions
def 初始化dp():
    co = ChromiumOptions().set_local_port(9222)
    page = ChromiumPage(addr_or_opts=co)
    page.timeout = 3
    return page
page=初始化dp()

def 测试点击按钮版的时长():
    开始时间 = time.time()
    res=drissionpage_utils.获取岗位信息点击按钮版(page)
    print(len(res))
    print(f"运行时间：{time.time()-开始时间}")

def 测试():
    标签页列表 = drissionpage_utils.创建多个标签页对象(page,2)
    搜索的url = main.搜索关键词("Linux运维","郑州")
    开始时间 = time.time()
    drissionpage_utils.获取岗位信息(page,搜索的url,len(标签页列表))
    print(f"运行时间：{time.time()-开始时间}")
    for i in 标签页列表:i.close()
def 测试随机查询岗位信息():
    res=drissionpage_utils.随机查询岗位信息(page,岗位="python",城市="深圳")
    for i in res:
        print(i)

def 测试检查HR是否在线():
    有在线状态标签=drissionpage_utils.找一个元素(page,'tag:span@class=boss-online-tag')
    在线状态=有在线状态标签.text.strip()
    print(在线状态)
if __name__ == "__main__":
    # 测试点击按钮版的时长()
    # 测试随机查询岗位信息()
    测试检查HR是否在线()
