# 用户语义增强

## 项目结构

```
├── .gitignore
├── data/       # 原始数据目录
├── resources/  # 增强结果输出目录（自动生成）
├── logs/       # 日志目录（自动生成）
├── models/     # 预训练模型存放目录
├── README.md
├── nlpcda_env.yml
├── resources
│   ├── Homophone.txt
│   ├── Homophone_tab.txt
│   ├── bank.txt
│   └── synonyms.txt
└── scripts             # 主要脚本目录
    ├── common
    │   ├── __init__.py
    │   ├── augment_utils.py            # 单步增强核心函数
    │   └── augment_utils_add.py        # 多步叠加增强核心函数
    ├── homophone_formatting.py
    ├── main_augment.py                 # 单步增强主程序
    └── main_augment_add.py             # 多步叠加增强主程序
```
## 主要特性

-   **多步随机叠加增强**：支持对同一句子依次应用多种增强方法（可控制叠加次数），生成更贴近真实口语的复杂噪声。
    
-   **丰富的增强方法库**：
    
    -   语气词插入（句首/句中）
        
    -   结巴模拟（单字重复）
        
    -   词语重复（多字词重复 + 可选混合重复）
        
    -   语序打乱（逗号前后交换、简单谓语前置）
        
    -   同音字替换（模拟口音/打字错误）
        
    -   随机字符删除（模拟吞音/漏字）
        
    -   实体名称替换（机构/公司名）
        
    -   同义词替换（基于自定义词库）
        
-   **自定义词库支持**：同音字、实体、同义词均可使用用户提供的词库文件，适配电催业务术语。
    
-   **批量 Excel 处理**：输入 Excel 文件，自动识别 `human` 列，输出带增强结果的新列 `human_augmented`，支持多工作表。
    
-   **灵活的命令行参数**：可指定输入/输出文件、工作表名、变体数量、叠加次数范围。
    
-   **日志记录**：详细日志同时输出到控制台（INFO 级别）和文件（DEBUG 级别），便于追溯。

## 项目环境

    -   Python 3.8+
        
    -   依赖库：见 nlpcda_env.yml    # 项目环境配置
    
#### 克隆项目

    git clone https://github.com/your-repo/Data_Augmentation_human.git
    cd Data_Augmentation_human

#### 创建虚拟环境（推荐）

    conda env create -f environment.yml  # 不指定环境名
    conda env create -n 新环境名 -f environment.yml   # 指定环境名
 
## nlpcda模型下载网址

    https://github.com/ZhuiyiTechnology/pretrained-models?tab=readme-ov-file
    
    nlpcda github: https://gitcode.com/gh_mirrors/nl/nlpcda/blob/master/README.md

## 扩展与自定义

### 添加新的增强方法

    1.  在 augment_utils_add.py 中编写新的 apply_xxx(sentence: str) -> str 函数。
        
    2.  将函数名加入 AUGMENT_FUNCS 列表。
        
    3.  如需调整各方法被选中的概率，可修改 multi_step_augment 中的 random.choice 为加权随机选择。
    

### 调整增强参数

    -   修改 augment_utils_add.py 顶部的全局变量：FILLERS、TAILS、NUM_VARIANTS 等。
        
    -   调整 nlpcda 增强器的 change_rate（替换概率）。
    

## 常见问题

### Q: 自定义词库不生效怎么办？

A: 请检查：

-   文件路径是否正确（项目根目录下的 `resources/`）
    
-   文件编码是否为 UTF-8 无 BOM
    
-   分隔符是否符合要求（同音字词库为制表符，同义词词库为空格，实体词库为换行）
    

### Q: 多步增强结果过于混乱？

A: 可降低 `max_steps` 值（如设为 2），或减少 `AUGMENT_FUNCS` 中的方法数量。

### Q: 运行时报错 `No module named 'nlpcda'`？

A: 请执行 `pip install nlpcda`。若仍报错，尝试升级：`pip install --upgrade nlpcda`。

