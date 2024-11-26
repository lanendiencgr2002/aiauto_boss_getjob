from pathlib import Path
import json
import sys

def 更新markdown图片配置(markdown文件路径):
    # 转换为Path对象
    md_path = Path(markdown文件路径)
    
    # 确保当前文件是.md结尾
    if md_path.suffix != '.md':
        print("当前文件不是Markdown文件")
        return

    markdown文件名 = md_path.stem
    资源文件夹 = f"{markdown文件名}.assets"
    
    # 确保资源文件夹存在
    完整资源路径 = md_path.parent / 资源文件夹
    完整资源路径.mkdir(exist_ok=True)
    
    # 更新全局MarkdownImage配置
    设置文件路径 = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
    
    try:
        if 设置文件路径.exists():
            设置内容 = 设置文件路径.read_text(encoding='utf-8')
            设置 = json.loads(设置内容)
            # 更新Markdown-image的设置
            设置['markdown-image.local.path'] = 资源文件夹
            设置文件路径.write_text(json.dumps(设置, indent=4, ensure_ascii=False), encoding='utf-8')
            print(f"已更新全局Markdown-image设置：路径设为 {资源文件夹}")
        else:
            print(f"全局settings.json 文件不存在")
    except json.JSONDecodeError as e:
        print(f"警告：{设置文件路径} 文件格式错误。错误信息：{str(e)}")

if __name__ == "__main__":
    # 当前目录下的一个md文件
    当前文件 = Path(__file__)
    print(f"当前文件: {当前文件}")

    if 当前文件 and 当前文件.exists():
        # 获取当前文件所在目录下的所有 .md 文件
        md_files = list(当前文件.parent.glob("*.md"))
        if md_files:
            for md_file in md_files:
                更新markdown图片配置(md_file)
                print(f"已处理: {md_file.name}")
        else:
            print(f"在 {当前文件.parent} 中没有找到 Markdown 文件")
    else:
        print("请在 VS Code 中打开任意文件并运行此任务")

