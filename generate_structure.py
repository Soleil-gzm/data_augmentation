import os
import subprocess

def get_git_tracked_files(project_path):
    """返回 Git 跟踪的文件列表（相对于项目根目录）"""
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().splitlines()
        return [f for f in files if f]  # 过滤空行
    except subprocess.CalledProcessError:
        print("错误：当前目录不是 Git 仓库或 git 命令不可用")
        return []

def build_tree(files):
    """从文件列表构建树形结构字符串"""
    tree = {}
    for file_path in files:
        parts = file_path.split('/')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    lines = []
    def walk(node, prefix=''):
        items = list(node.items())
        for i, (name, subnode) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = '└── ' if is_last else '├── '
            lines.append(f"{prefix}{connector}{name}")
            if subnode:
                extension = '    ' if is_last else '│   '
                walk(subnode, prefix + extension)
    walk(tree)
    return lines

def main():
    project_path = "/home/GUO_Zimeng/coding/Data_Augmentation_human"
    readme_path = os.path.join(project_path, "README.md")
    print(f"README 文件路径: {readme_path}")
    print(f"文件是否存在: {os.path.exists(readme_path)}")
    
    files = get_git_tracked_files(project_path)
    if not files:
        print("未获取到 Git 跟踪的文件")
        return
    print(f"获取到 {len(files)} 个文件")
    
    tree_lines = build_tree(files)
    structure_text = "\n".join(tree_lines)
    print("生成的目录树预览（前10行）：")
    for line in tree_lines[:10]:
        print(line)
    
    # 追加到 README.md
    with open(readme_path, 'a', encoding='utf-8') as f:
        f.write("\n\n## 项目结构\n\n```\n")
        f.write(structure_text)
        f.write("\n```\n")
    
    print(f"✅ 已追加到 {readme_path}")
    # 验证写入
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "项目结构（Git 跟踪）" in content:
            print("验证成功：内容已写入")
        else:
            print("验证失败：未找到写入标记")

if __name__ == "__main__":
    main()