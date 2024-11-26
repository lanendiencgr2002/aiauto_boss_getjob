import os
import ast
import sys
from pathlib import Path
from typing import Set, List
import subprocess

class DependencyAnalyzer:
    """项目依赖分析器"""
    
    def __init__(self):
        # 替换 sys.stdlib_module_names 的实现
        self.标准库 = self._获取标准库模块()
        # 本地模块（项目内的模块）
        self.本地模块 = set()
        
    def _获取标准库模块(self) -> Set[str]:
        """获取 Python 标准库模块列表"""
        标准库模块 = set()
        # 获取 Python 安装目录
        python路径 = sys.prefix
        标准库路径 = os.path.join(python路径, 'Lib')
        
        try:
            # 遍历标准库目录
            for 项目 in os.listdir(标准库路径):
                if 项目.endswith('.py'):
                    标准库模块.add(项目[:-3])
                elif os.path.isdir(os.path.join(标准库路径, 项目)) and not 项目.startswith('__'):
                    标准库模块.add(项目)
            
            # 添加一些常见的内置模块
            内置模块 = {'sys', 'os', 'math', 're', 'time', 'datetime', 'json', 
                    'random', 'collections', 'itertools', 'functools', 'typing',
                    'pathlib', 'subprocess', 'shutil', 'tempfile', 'copy', 'ast'}
            标准库模块.update(内置模块)
            
        except Exception as e:
            print(f"警告: 获取标准库模块列表时出错: {e}")
        
        return 标准库模块
    
    def 分析文件导入(self, 文件路径: Path) -> Set[str]:
        """分析单个Python文件中的导入语句"""
        导入集合 = set()
        
        try:
            with open(文件路径, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                # 处理 import xxx 语句
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        导入集合.add(alias.name.split('.')[0])
                
                # 处理 from xxx import yyy 语句
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # 排除 from . import xxx 的情况
                        导入集合.add(node.module.split('.')[0])
                        
        except Exception as e:
            print(f"警告: 分析文件 {文件路径} 时出错: {e}")
            
        return 导入集合
    
    def 收集本地模块(self, 项目路径: Path):
        """收集项目中的本地模块名称"""
        for py文件 in 项目路径.rglob('*.py'):
            # 将文件路径转换为模块名
            相对路径 = py文件.relative_to(项目路径)
            模块名 = str(相对路径.with_suffix('')).replace(os.sep, '.')
            self.本地模块.add(模块名.split('.')[0])
    
    def 获取已安装版本(self, 包名: str) -> str:
        """获取已安装包的版本号"""
        try:
            结果 = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', 包名],
                capture_output=True,
                text=True
            )
            for 行 in 结果.stdout.split('\n'):
                if 行.startswith('Version:'):
                    return 行.split(':')[1].strip()
        except Exception:
            pass
        return ''
    
    def 分析项目依赖(self, 项目路径: str = '.') -> List[str]:
        """分析项目依赖并返回pip安装命令"""
        项目路径 = Path(项目路径)
        所有导入 = set()
        
        # 首先收集本地模块
        self.收集本地模块(项目路径)
        
        # 分析所有.py文件的导入
        for py文件 in 项目路径.rglob('*.py'):
            所有导入.update(self.分析文件导入(py文件))
        
        # 过滤掉标准库和本地模块
        第三方包 = 所有导入 - self.标准库 - self.本地模块
        
        # 生成pip命令，包含版本信息
        pip命令列表 = []
        for 包名 in sorted(第三方包):
            版本 = self.获取已安装版本(包名)
            if 版本:
                pip命令列表.append(f"{包名}=={版本}")
            else:
                pip命令列表.append(包名)
        
        return pip命令列表

def 生成依赖文件():
    """生成requirements.txt文件"""
    当前脚本路径 = Path(__file__).parent
    分析器 = DependencyAnalyzer()
    依赖列表 = 分析器.分析项目依赖(当前脚本路径)
    
    if not 依赖列表:
        print("未找到任何第三方依赖。")
        return
    
    print("\n项目依赖及其版本信息:")
    for 依赖 in 依赖列表:
        包名 = 依赖.split('==')[0]  # 处理可能已经包含版本号的情况
        版本 = 分析器.获取已安装版本(包名)
        if 版本:
            print(f"- {包名} (版本: {版本})")
        else:
            print(f"- {包名} (未安装)")
    
    # 生成requirements.txt
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(依赖列表))
    
    print("\n已生成 requirements.txt 文件")
    print("\n可以使用以下命令安装依赖:")
    print(f"pip install -r requirements.txt")

if __name__ == '__main__':
    生成依赖文件() 