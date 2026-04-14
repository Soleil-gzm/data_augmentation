import pandas as pd
import random
import re

# ================= 配置 =================
INPUT_EXCEL = "data/test1.xlsx"      # 输入文件名
OUTPUT_EXCEL = "output_excel/output.xlsx"    # 输出文件名
NUM_VARIANTS = 3                # 每个句子生成的变体数量

# 语气词（只用于插入，不改变语义）
FILLERS = ["嗯", "那个", "就是", "呃", "啊"]
TAILS = ["吧", "啊", "哦", "呗"]

# 极少量同义词（只针对日常动词，避免改变语义）
SYNONYMS = {
    "睡觉": ["休息", "睡一下"],
    "晚点": ["晚些", "过一会儿"],
    "打": ["联系", "打电话"],
}

def simple_augment(sentence: str) -> str:
    """只做口语化噪声添加，不改语义"""
    if not isinstance(sentence, str) or len(sentence.strip()) == 0:
        return sentence
    
    op = random.choice(["insert_filler", "add_tail", "synonym_replace"])
    
    if op == "insert_filler":
        filler = random.choice(FILLERS)
        if random.random() < 0.8:
            return f"{filler}，{sentence}"
        else:
            match = re.search(r'[，,。！？]', sentence)
            if match:
                pos = match.end()
                return sentence[:pos] + filler + "，" + sentence[pos:]
            else:
                words = sentence.split()
                if words:
                    return words[0] + filler + "，" + " ".join(words[1:])
                return sentence
    
    elif op == "add_tail":
        tail = random.choice(TAILS)
        if sentence.rstrip() and sentence.rstrip()[-1] in "吧啊哦呗嗯":
            return sentence
        return sentence + tail
    
    elif op == "synonym_replace":
        for word, syns in SYNONYMS.items():
            if word in sentence:
                new_word = random.choice(syns)
                return sentence.replace(word, new_word, 1)
        filler = random.choice(FILLERS)
        return f"{filler}，{sentence}"
    
    return sentence

def augment_cell(cell_value, num_variants=NUM_VARIANTS) -> str:
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

def main():
    xl = pd.ExcelFile(INPUT_EXCEL)
    print(f"读取文件: {INPUT_EXCEL}")
    print(f"发现的工作表: {xl.sheet_names}\n")
    
    output_dict = {}
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet_name)
        print(f"处理工作表: {sheet_name}")
        print(f"  列名: {list(df.columns)}")
        
        # 查找 human 列（支持多种写法）
        human_col = None
        for col in df.columns:
            col_str = str(col).strip()
            if col_str == "human(客户)" or col_str == "human" or ("human" in col_str and "客户" in col_str):
                human_col = col
                break
        
        if human_col is None:
            print(f"  警告: 未找到 human 列，跳过该工作表")
            output_dict[sheet_name] = df
            continue
        
        print(f"  找到 human 列: '{human_col}'，开始增强...")
        
        # 执行增强
        df["human_augmented"] = df[human_col].apply(augment_cell)
        
        # ========== 关键修改：将新列移动到 human 列的右侧 ==========
        cols = df.columns.tolist()
        # 找到 human 列和 human_augmented 列的索引
        human_idx = cols.index(human_col)
        # 移除 human_augmented 列（当前在最后）
        cols.remove("human_augmented")
        # 在 human_idx+1 位置插入
        cols.insert(human_idx + 1, "human_augmented")
        df = df[cols]   # 重新排列列顺序
        # ========================================================
        
        # 显示增强后示例
        sample = df[[human_col, "human_augmented"]].head(2)
        print("  增强示例（原句 → 增强后）：")
        for idx, row in sample.iterrows():
            print(f"    原句: {row[human_col]}")
            print(f"    增强: {row['human_augmented']}\n")
        
        output_dict[sheet_name] = df
        print(f"  完成，共 {len(df)} 行\n")
    
    # 保存结果
    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        for sheet_name, df in output_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n✅ 增强完成！结果保存至: {OUTPUT_EXCEL}")

if __name__ == "__main__":
    random.seed(42)
    main()