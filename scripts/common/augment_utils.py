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
    "还": ["偿还", "归还"],
    "催": ["催促", "追"],
}

# 否定词集合（用于语序打乱时跳过，避免语义反转）
NEGATION_WORDS = set(["不", "没", "无", "别", "不要", "不用", "未曾"])

# ================= 增强函数 =================

def simple_augment(sentence: str) -> str:
    """对单个句子做一次随机增强（不改语义，避免语气词重复）"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence

    # 五种操作类型，可调整权重
    op = random.choices(
        ["insert_filler", "add_tail", "synonym_replace", "stutter", "reorder"],
        weights=[0.25, 0, 0.2, 0.25, 0.3],
        k=1
    )[0]

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
    # elif op == "add_tail":
    #     tail = random.choice(TAILS)
    #     raw = re.sub(r'[。！？!?]+$', '', sentence.rstrip())
    #     raw = raw.rstrip()
    #     if not raw:
    #         return sentence
    #     if raw[-1] in TAIL_WORDS:
    #         return sentence
    #     return raw + tail

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
                return sentence[0] * 2 + sentence[1:]
            return sentence
        char = match.group()
        repeat_count = random.randint(1, 2)
        stuttered_char = char * (repeat_count + 1)
        start, end = match.start(), match.end()
        return sentence[:start] + stuttered_char + sentence[end:]

    # 5. 语序打乱（倒装/成分移位）
    elif op == "reorder":
        return reorder_sentence(sentence)

    return sentence


def reorder_sentence(sentence: str) -> str:
    """对句子进行安全的语序打乱（倒装），返回新句子；若不适合则返回原句"""
    if len(sentence) < 5:
        return sentence

    # 检测否定词，若有则跳过（避免语义反转）
    if any(neg in sentence for neg in NEGATION_WORDS):
        return sentence

    # 模式1：谓语提前（将第一个动词短语提前到句首）
    verb_match = re.search(r'([还让帮给告诉说解释]\w*)', sentence)
    if verb_match:
        verb = verb_match.group()
        before_verb = sentence[:verb_match.start()].strip()
        after_verb = sentence[verb_match.end():].strip()
        if before_verb and after_verb:
            # 构造倒装句：动词 + 之后的内容 + 之前的主语
            new_sent = f"{verb}{after_verb}，{before_verb}"
            return new_sent

    # 模式2：对于“让/帮”结构，将动作部分提前
    let_match = re.search(r'(让|帮)(\S+?)(\w+)', sentence)
    if let_match:
        let_word = let_match.group(1)
        person = let_match.group(2)
        action = let_match.group(3)
        before = sentence[:let_match.start()].strip()
        after = sentence[let_match.end():].strip()
        new_sent = f"{action}{after}，{before}{let_word}{person}"
        return new_sent

    # 模式3：简单交换逗号前后（如果句子有逗号）
    if ',' in sentence:
        parts = sentence.split(',', 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            return f"{parts[1].strip()}，{parts[0].strip()}"
    if '，' in sentence:
        parts = sentence.split('，', 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            return f"{parts[1].strip()}，{parts[0].strip()}"

    # 如果没有合适变换，返回原句
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