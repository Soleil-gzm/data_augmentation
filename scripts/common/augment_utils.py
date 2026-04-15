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

    # 五种操作类型（可调整权重）
    # op = random.choice(["insert_filler", "add_tail", "synonym_replace", "stutter"])
    op = random.choices(
        ["insert_filler", "add_tail", "synonym_replace", "stutter"],
        weights=[0.3, 0.3, 0.2, 0.2],   # 结巴占20%
        k=1
    )[0]


    # 1. 插入语气词
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

    # 2. 添加句尾语气词
    # elif op == "add_tail":
    #     tail = random.choice(TAILS)
    #     raw = re.sub(r'[。！？!?]+$', '', sentence.rstrip())
    #     raw = raw.rstrip()
    #     if not raw:
    #         return sentence
    #     if raw[-1] in TAIL_WORDS:
    #         return sentence
    #     return raw + tail

    # 3. 同义词替换
    elif op == "synonym_replace":
        for word, syns in SYNONYMS.items():
            if word in sentence:
                new_word = random.choice(syns)
                return sentence.replace(word, new_word, 1)
        filler = random.choice(FILLERS)
        return f"{filler}，{sentence}"

    # 4. 结巴/重复模拟（只重复第一个汉字，避免整句重复）
    elif op == "stutter":
        # 句子太短不处理
        if len(sentence) < 2:
            return sentence
        
        # 找到第一个汉字字符（避免对标点、数字进行重复）
        match = re.search(r'[\u4e00-\u9fa5]', sentence)
        if not match:
            # 没有汉字，尝试重复第一个字符（字母或数字）
            if len(sentence) > 1:
                return sentence[0] * 2 + sentence[1:]
            return sentence
        
        char = match.group()
        # 随机重复1~2次（即总共2或3个相同字符）
        repeat_count = random.randint(1, 2)
        stuttered_char = char * (repeat_count + 1)
        # 替换第一个匹配的汉字
        start = match.start()
        end = match.end()
        new_sentence = sentence[:start] + stuttered_char + sentence[end:]
        return new_sentence
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