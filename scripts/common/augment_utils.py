import random
import re
import pandas as pd

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
}

# ================= 增强函数 =================
def simple_augment(sentence: str) -> str:
    """对单个句子做一次随机增强（不改语义，避免语气词重复）"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence

    op = random.choice(["insert_filler", "add_tail", "synonym_replace"])

    # 1. 插入语气词（句首或句中第一个标点后）
    if op == "insert_filler":
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
        # 去除句尾所有标点符号
        raw = re.sub(r'[。！？!?]+$', '', sentence.rstrip())
        raw = raw.rstrip()
        if not raw:
            return sentence
        if raw[-1] in TAIL_WORDS:
            return sentence
        return raw + tail

    # 3. 同义词替换
    elif op == "synonym_replace":
        for word, syns in SYNONYMS.items():
            if word in sentence:
                new_word = random.choice(syns)
                return sentence.replace(word, new_word, 1)
        filler = random.choice(FILLERS)
        return f"{filler}，{sentence}"

    return sentence

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