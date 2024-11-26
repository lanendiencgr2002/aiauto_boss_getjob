本项目理论基于ai接口的查询匹配度20分钟可投完100份简历（超大量合适岗位，开10个标签页都同时沟通hr），但是由于查找合适岗位的速度较慢，并且有些bug，实际时间未知

已实现功能
自动过滤不活跃的HR
学历、城市、薪资、岗位筛选
AI岗位匹配度分析，可调节匹配度
自动打招呼（BOSS内默认设置）
自定义打招呼内容

使用本脚本步骤：
1. 给谷歌或者edge浏览器弄个快捷方式，属性，目标指定端口，如下图
参考："C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
<img alt="图 1" src="README.assets/2024-11-26-1732603491069.png" />  
2. 用这个快捷方式打开浏览器，登录boss直聘网站
3. 在config.json中配置好参数，例如岗位，城市，学历筛选，薪资等，看着改，有些配置可以不用改
4. 启动本地端口5000的fastapi的ai服务，是本地仓库的local_ai_sever，也可以自己写一个
5. 运行main.py脚本


注意：
1. 有个bug，投多了会找不到合适的岗位了，不知道为啥，有知道原因的佬可以教一下我吗，我改一下代码
2. 本项目是基于https://github.com/SanThousand/auto_get_jobs进行重构的，感谢SanThousand大佬的开源
3. 如果想用自己认识的模型，修改aiconfig.py文件，把def ai_response(content):函数修改为自己的模型
4. 本地运行日志，在本次面试运行日志.txt文件中可以看到实时的脚本运行日志
5. 已投递的岗位，在已投递的岗位.txt文件中可以看到，第一次要自己清空（留个样式可以看），不然会保留以前的所有岗位

联系方式：
- lanendiencgr@gmail.com
- GitHub: lanendiencgr
