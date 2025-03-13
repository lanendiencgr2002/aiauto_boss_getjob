import time
from DrissionPage.common import Actions
from DrissionPage import ChromiumPage, ChromiumOptions
from dataclasses import dataclass

@dataclass
class Dp标签类:
    page: ChromiumPage
    def __init__(self,page:ChromiumPage):
        self.page=self.dp配置()


    @classmethod
    def dp配置(cls):
        co = ChromiumOptions().set_local_port(8077)
        co.set_timeouts(base=5)
        page = ChromiumPage(addr_or_opts=co)
        print(f"浏览器启动端口: {page.address}")
        return page
    @staticmethod
    def 创建多个标签页对象(page,count=5):
        return [page.new_tab() for _ in range(count)]

    @staticmethod
    def 根据标题取当前tab(page,标题):
        """
        根据标题查找当前打开的标签页
        
        Args:
            ele: DrissionPage对象
            标题: 要查找的标签页标题 包含即可
            
        Returns:
            Tab对象: 如果找到匹配的标签页则返回该Tab对象
            None: 如果未找到匹配的标签页则返回None
        """
        tabs=page.get_tabs()
        for tab in tabs:
            if 标题 in tab.title:
                return tab
        return None
    @staticmethod
    def 根据url获取当前tab(page,url):
        """
        根据URL查找当前打开的标签页
        
        Args:
            ele: DrissionPage对象 
            url: 要查找的标签页URL 包含即可
            
        Returns:
            Tab对象: 如果找到匹配的标签页则返回该Tab对象
            None: 如果未找到匹配的标签页则返回None
        """
        tabs=page.get_tabs()
        for tab in tabs:
            if url in tab.url:
                return tab
        return None

    @staticmethod
    def 返回最新tab(page):
        return page.latest_tab


if __name__ == '__main__':
    page=Dp标签类.dp配置()
    tab=Dp标签类.返回最新tab(page)
    print(tab.title)




