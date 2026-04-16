import os
import random
import re
import pandas as pd
from nlpcda import Homophone
import logging
from nlpcda import RandomDeleteChar

# ================= 可配置参数 =================
NUM_VARIANTS = 3                    # 每个原句生成几个变体

# 语气词库（用于插入句首或句中）
FILLERS = ["嗯", "那个", "就是", "呃", "啊"]

# 句尾可添加的语气词
TAILS = ["吧", "啊", "哦", "呗"]

# 需要避免重复的句尾语气词（包括疑问词“吗”、“呢”等）
TAIL_WORDS = set(["吧", "啊", "哦", "呗", "嗯", "啦", "呀", "嘛", "呐", "哈", "了", "吗", "呢"])

# 同义词映射（可根据需要扩展）
SYNONYMS = {
    "睡觉": ["休息", "睡一下"],
    "晚点": ["晚些", "过一会儿"],
    "打": ["联系", "打电话"],
    "还": ["偿还", "归还"],
    "催": ["催促", "追"],
}

# 否定词集合（用于语序打乱时跳过，避免语义反转）
NEGATION_WORDS = set(["不", "没", "无", "别", "不要", "不用", "未曾"])

# # 自定义同音字词库路径（相对于项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOMOPHONE_DICT_PATH = os.path.join(BASE_DIR, 'resources', 'Homophone_tab.txt')

# 随机删除字符增强器（模拟漏字/吞音）
_random_delete_aug = RandomDeleteChar(create_num=3, change_rate=0.2, seed=42)

print(f"[DEBUG] 项目根目录: {BASE_DIR}")
print(f"[DEBUG] 期望的词库路径: {HOMOPHONE_DICT_PATH}")
if not os.path.exists(HOMOPHONE_DICT_PATH):
    print(f"[WARN] 词库文件不存在，将使用默认词库（可能产生生僻字）")
    _homophone_aug = Homophone(create_num=3, change_rate=0.3, seed=42)
else:
    try:
        _homophone_aug = Homophone(base_file=HOMOPHONE_DICT_PATH, create_num=3, change_rate=0.3, seed=42)
        print(f"[INFO] 成功加载自定义词库: {HOMOPHONE_DICT_PATH}")
    except Exception as e:
        print(f"[ERROR] 加载自定义词库失败: {e}，使用默认词库")
        _homophone_aug = Homophone(create_num=3, change_rate=0.3, seed=42)

'''
================= 增强方法权重配置 =================
说明：调整 weights 列表中的数值可以控制每种增强方法被选中的概率。
顺序必须与 op 列表一致，权重之和不必为 1，程序会自动归一化。

方法说明：
- insert_filler  : 句首或句中插入语气词（如“嗯”、“那个”）
- add_tail       : 句尾添加语气词（如“吧”、“啊”）
- synonym_replace: 使用自定义同义词映射替换（轻量）
- stutter        : 结巴模拟（重复第一个汉字）
- reorder        : 语序打乱（仅交换逗号前后）
- homophone : 调用 nlpcda 库进行同义词替换（更丰富）

=================================================
'''

# ================= 增强函数 =================

def simple_augment(sentence: str) -> str:
    """对单个句子做一次随机增强（不改语义，避免语气词重复）"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence

    # 定义操作列表和对应权重（权重之和建议为1.0）
    op_list = ["insert_filler","synonym_replace", "stutter", "reorder", "homophone", "random_delete"]
    weights = [0.25, 0.20, 0.10, 0.10, 0.10, 0.25]   # 可根据需求修改

    # test 
    # op_list = ["random_delete"]
    # weights = [0.9]   # 可根据需求修改

    #五种操作类型，可调整权重
    op = random.choices(op_list, weights=weights, k=1)[0]

    # 1. 插入语气词（句首或句中第一个标点后）
    if op == "insert_filler":
        '''
        80% 概率直接加在句首（如“嗯，你好吗？”）。
        20% 概率寻找第一个标点（逗号、句号、问号、感叹号），在其后插入语气词；若标点位置太靠后（>80%句子长度），则改到句首。
        如果没有标点且句子有至少两个词，则在第一个词后插入；否则句首插入。
        '''
        filler = random.choice(FILLERS)
        if random.random() < 0.8:
            return f"{filler}，{sentence}"
        else:
            match = re.search(r'[，,。？!]', sentence)
            if match:
                pos = match.end()
                if pos > len(sentence) * 0.8:
                    return f"{filler}，{sentence}"
                return sentence[:pos] + filler + "，" + sentence[pos:]
            else:
                words = sentence.split()
                if len(words) >= 2:
                    return words[0] + filler + "，" + " ".join(words[1:])
                else:
                    return f"{filler}，{sentence}"

    # 2. 添加句尾语气词（先去除句尾所有标点，再检查是否已有语气词）
    elif op == "add_tail":
        tail = random.choice(TAILS)
        raw = re.sub(r'[。！？!?]+$', '', sentence.rstrip())
        raw = raw.rstrip()
        if not raw:
            return sentence
        if raw[-1] in TAIL_WORDS:
            return sentence
        return raw + tail

    # 3. 同义词替换（只替换第一个匹配的词）
    elif op == "synonym_replace":
        for word, syns in SYNONYMS.items():
            if word in sentence:
                new_word = random.choice(syns)
                return sentence.replace(word, new_word, 1)
        filler = random.choice(FILLERS)
        return f"{filler}，{sentence}"

    # 4. 结巴模拟（只重复第一个汉字，避免整句重复）
    elif op == "stutter":
        if len(sentence) < 2:
            return sentence
        match = re.search(r'[\u4e00-\u9fa5]', sentence)
        if not match:
            if len(sentence) > 1:
                return sentence[0] * 2 + sentence[1:]       # 若无汉字，则重复第一个字符（可能是字母、数字）。
            return sentence
        char = match.group()
        repeat_count = random.randint(1, 2)         # 随机重复 1~2 次（即总共 2 或 3 个相同字符），替换原字符。
        stuttered_char = char * (repeat_count + 1)
        start, end = match.start(), match.end()
        return sentence[:start] + stuttered_char + sentence[end:]

    # 5. 语序打乱（倒装/成分移位）
    elif op == "reorder":
        return reorder_sentence(sentence)
     
    # 6. 同音字替换
    elif op == "homophone":
        return homophone_augment(sentence)
    
    elif op == "random_delete":
        return random_delete_augment(sentence)

    return sentence

def reorder_sentence(sentence: str) -> str:
    """安全的语序打乱：交换逗号前后，或简单谓语前置"""
    if len(sentence) < 5:
        return sentence

    # 检测否定词，若有则跳过
    if any(neg in sentence for neg in NEGATION_WORDS):
        return sentence

    # 保存末尾标点
    end_punct = ''
    if sentence and sentence[-1] in '。！？!?':
        end_punct = sentence[-1]
        sentence = sentence[:-1].rstrip()

    # 模式1：交换逗号前后（最安全）
    if '，' in sentence:
        parts = sentence.split('，', 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            new_sent = f"{parts[1].strip()}，{parts[0].strip()}"
            return new_sent + end_punct
    if ',' in sentence:
        parts = sentence.split(',', 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            new_sent = f"{parts[1].strip()}，{parts[0].strip()}"
            return new_sent + end_punct


    # 模式2：简单谓语前置（匹配“我/你 + 已经/也/就 + 动词 + 了/过 + 其他”）
    # 例如“我已经还了” -> “还了，我已经”
    match = re.match(r'^(我|你)(已经|也|就|都)?(\w+?)(了|过)?(.*)$', sentence)
    if match:
        subject = match.group(1)      # 我/你
        adverb = match.group(2) or ''
        verb = match.group(3)         # 动词
        aspect = match.group(4) or '' # 了/过
        rest = match.group(5).strip()
        if verb and len(verb) >= 1:
            # 构造倒装：动词+了/过 + 其他 + 主语
            new_sent = f"{verb}{aspect}{rest}，{subject}{adverb}"
            # 清理多余空格
            new_sent = re.sub(r'\s+', '', new_sent)
            return new_sent + end_punct

    # 无变换则返回原句
    return sentence + end_punct

def homophone_augment(sentence: str) -> str:
    """使用同音字替换进行增强（模拟常见打字错误）"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence
    try:
        results = _homophone_aug.replace(sentence)
        # results[0] 是原句，后续为变体
        if len(results) > 1:
            # 随机选择一个变体（也可以固定取第一个变体）
            return random.choice(results[1:])
        else:
            return sentence
    except Exception as e:
        print(f"同音字替换出错: {e}")
        return sentence

def random_delete_augment(sentence: str) -> str:
    """使用随机删除字符进行增强（模拟漏字、吞音）"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence
    try:
        results = _random_delete_aug.replace(sentence)
        if len(results) > 1:
            return random.choice(results[1:])   # 随机选择一个变体
        else:
            return sentence
    except Exception as e:
        print(f"随机删除字符出错: {e}")
        return sentence

''' ==================== excel 格式处理 ===================='''
def augment_cell(cell_value, num_variants=NUM_VARIANTS) -> str:
    """处理一个单元格（可能含 '/' 分隔的多条句子）"""
    if pd.isna(cell_value):
        return ""
    raw_sentences = [s.strip() for s in str(cell_value).split('/') if s.strip()]
    if not raw_sentences:
        return ""
    result = []
    for sent in raw_sentences:
        variants = [simple_augment(sent) for _ in range(num_variants)]
        result.append("/".join(variants))
    return "/".join(result)


def move_column_to_right(df, col_name, new_col_name):
    """将新列移动到原列右侧"""
    cols = df.columns.tolist()
    if new_col_name not in cols:
        return df
    idx = cols.index(col_name)
    cols.remove(new_col_name)
    cols.insert(idx + 1, new_col_name)
    return df[cols]
