import os
from typing import List, Dict

class WordGroupParser:
    """解析 frequency_words.txt 分组配置，支持普通词、+必须词、!排除词"""
    def __init__(self, filepath: str = None):
        if filepath is None:
            # 默认在项目根目录
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frequency_words.txt')
        self.filepath = filepath

    def parse(self) -> List[Dict[str, List[str]]]:
        groups = []
        current_group = {"keywords": [], "must_keywords": [], "exclude_keywords": []}
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    # 空行表示新分组
                    if any(current_group.values()):
                        groups.append(current_group)
                        current_group = {"keywords": [], "must_keywords": [], "exclude_keywords": []}
                    continue
                if line.startswith('+'):
                    current_group["must_keywords"].append(line[1:].strip())
                elif line.startswith('!'):
                    current_group["exclude_keywords"].append(line[1:].strip())
                else:
                    current_group["keywords"].append(line)
        # 最后一个分组
        if any(current_group.values()):
            groups.append(current_group)
        return groups

if __name__ == "__main__":
    parser = WordGroupParser()
    groups = parser.parse()
    for idx, group in enumerate(groups, 1):
        print(f"分组{idx}：{group}") 