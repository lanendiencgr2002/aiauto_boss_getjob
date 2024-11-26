# AI自动投递简历助手

## 项目简介
本项目基于AI接口实现智能简历投递，支持多线程并发投递和智能匹配。理论上20分钟可投递100份简历（支持同时开启多个标签页与HR沟通），实际速度取决于岗位匹配效率和系统稳定性。

## 核心功能
- ✨ AI智能岗位匹配
  - 自定义匹配度阈值（0-1）
  - 支持多线程并发匹配
  - 智能过滤不合适岗位
- 🔍 多维度筛选
  - 城市范围（支持多城市）
  - 薪资范围（如：2-6k）
  - 学历要求（支持：本科/硕士等）
  - 经验要求（可配置）
  - 行业类型
- 👋 智能沟通
  - 自动打招呼（可自定义内容）
  - HR活跃度过滤
  - 批量沟通（可配置最大沟通次数）
- 🚀 高效投递
  - 多标签页并发（可配置标签页数量）
  - 支持批量查询
  - 自动翻页功能
- 📊 完整日志
  - 实时运行日志
  - 投递统计
  - 匹配分析记录

## 配置说明
主要配置项（config.json）：
```json
{
    "要查询的岗位": ["java"],  // 支持多个岗位
    "要查询的城市": ["不限"],   // 支持多个城市
    "薪资范围": "2-6k",
    "匹配度": 0.8,           // AI匹配阈值
    "标签页数量": 3,         // 并发标签页数
    "最大沟通次数": 50,      // 单次运行最大投递数
    "用多线程ai过滤和投简历": true
}
```

## 使用步骤

### 1. 环境准备
```bash
pip install -r requirements.txt
```

### 2. 浏览器配置
1. 为Chrome/Edge浏览器创建快捷方式
2. 在快捷方式属性中的"目标"后添加调试端口参数：
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```
   ![浏览器配置示例](README.assets/2024-11-26-1732603491069.png)

### 3. 系统配置
1. 使用配置好的快捷方式打开浏览器
2. 登录BOSS直聘网站
3. 配置 `config.json`：
   - 设置目标岗位
   - 设置目标城市
   - 设置学历要求
   - 设置薪资范围
4. 在`我的简历.txt`中填入您的简历内容
5. 启动本地AI服务（端口5000）
6. 运行 `main.py`

## 注意事项
1. ⚠️ 已知问题：长时间运行后可能出现找不到合适岗位的情况
2. 💡 如需使用自定义AI模型，请修改 `aiconfig.py` 中的 `ai_response()` 函数
3. 📝 运行日志说明：
   - `本次面试运行日志.txt`：实时运行日志（每次运行清空）
   - `已投递的岗位.txt`：累计投递记录（追加模式）
   - `统计日志.txt`：每轮循环的统计数据（追加模式）

## 致谢
本项目基于 [SanThousand/auto_get_jobs](https://github.com/SanThousand/auto_get_jobs) 重构，感谢原作者的开源贡献。

## 联系方式
- 📧 Email: lanendiencgr@gmail.com
- 🐱 GitHub: lanendiencgr
