import os
from pathlib import Path
from DrissionPage import Chromium,ChromiumPage, ChromiumOptions
import tomli

class 配置类:
    @staticmethod
    def 切换到脚本所在目录():
        当前目录 = Path(__file__).resolve()
        os.chdir(当前目录.parent)
    @staticmethod
    def dp配置():
        co = ChromiumOptions().set_local_port(8077)
        co.set_timeouts(base=5)
        page = ChromiumPage(addr_or_opts=co)
        print(f"浏览器启动端口: {page.address}")
        return page
    @staticmethod
    def dp配置使用手机环境():
        co = ChromiumOptions().set_local_port(8077)
        co.set_user_agent(user_agents["Chrome_Android"])
        tab = Chromium(co).latest_tab
        user_agents = {
    "Chrome_Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Firefox_Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Safari_macOS": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.1 Safari/537.36",
    "Edge_Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Edge/110.0.1587.57",
    "Chrome_Android": "Mozilla/5.0 (Linux; Android 12; Pixel 5 Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36",
    "Safari_iOS": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1",
    "Opera_Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 OPR/97.0.4692.71"
        }
        # 设置界面模式
        zoom = {
            "command": "Emulation.setDeviceMetricsOverride",
            "parameters": {
                "width": 360,          # 设备的宽度 (像素)
                "height": 740,         # 设备的高度 (像素)
                "deviceScaleFactor": 1, # 设置设备的缩放比例 (相当于屏幕 DPI)
                "mobile": True,        # 设置是否为手机模拟 (选填为 "true" 或 "false")
                "scale": 1            # 页面缩放比例 (0.8 表示页面缩小到 80%)
            }
        }
        tab.run_cdp(zoom["command"], **zoom["parameters"])
        tab.get("https://www.baidu.com/")
    @staticmethod
    def 读取toml文件(文件路径: str) -> dict:
        with open(文件路径, 'rb') as f:
            return tomli.load(f)
    @staticmethod
    def 写入toml文件(文件路径: str, 配置文件数据: dict):
        with open(文件路径, 'wb') as f:
            tomli.dump(配置文件数据, f)

if __name__ == "__main__":
    配置类.切换到脚本所在目录()
    配置类.dp配置()
