# 用户语义增强

## 项目结构
Data_Augmentation_human/
├── data/                                 # 原始数据目录
│   ├── test.xlsx                         # 测试数据（少量样本）
│   └── all_data.xlsx                     # 全量原始数据（可能未提交）
│
├── output_excel/                         # 增强结果输出目录（自动生成）
│   └── *_augmented_*.xlsx                # 单步增强结果
│   └── *_multi_augmented_*.xlsx          # 多步叠加增强结果
│
├── logs/                                 # 日志目录（自动生成）
│   └── augment_*.log                     # 单步增强日志
│   └── augment_multi_*.log               # 多步叠加增强日志
│
├── resources/                            # 自定义资源文件（词库等）
│   ├── Homophone_tab.txt                 # 同音字替换词库（制表符分隔，拼音开头）
│   ├── entities.txt                      # 随机实体替换词库（每行一个实体）
│   ├── synonyms.txt                   # 自定义同义词词库（空格分隔，id+同义词列表）
│   └──
│
├── models/                               # 预训练模型存放目录（可选）
│   └── chinese_simbert_L-4_H-312_A-12/   # SimBERT 小模型（未成功集成）
│
├── scripts/                              # 主要脚本目录
│   ├── common/                           # 公共模块包
│   │   ├── __init__.py                   # 空文件，使 common 成为包
│   │   ├── augment_utils.py              # 单步增强核心函数（
│   │   └── augment_utils_add.py          # 多步叠加增强核心函数（独立增强函数 + multi_step_augment）
│   ├── main_augment.py                   # 单步增强主程序（支持命令行参数）
│   └── main_augment_add.py               # 多步叠加增强主程序（支持 min_steps, max_steps）
│
├── scripts_test/                         # 测试脚本目录（独立验证）
│   ├── test_nlpcda.py                    # 测试 nlpcda 同音字替换
│   ├── test_nlpcda_similarword.py        # 测试同义词替换
│   ├── test_homophone.py                 # 测试同音字替换自定义词库
│   ├── test_entity_replace.py            # 测试随机实体替换
│   ├── test_similarword.py               # 测试同义词替换自定义词库
│   ├── test_similarword_custom.py        # 使用自定义词库测试同义词替换
│   ├── test_random_delete.py             # 测试随机删除字符
│   ├── test_simbert.py                   # 测试 SimBERT（未成功）
│   ├── test_simbert_bert4keras.py        # 使用 bert4keras 测试 SimBERT
│   └── test_multi_augment.py             # 测试多步叠加增强（可选）
│
├── .gitignore                            # Git 忽略配置（忽略 output_excel/, logs/, __pycache__/, *.pyc, 敏感数据等）
└── README.md                             # 项目说明文档（待完善）



## 项目环境

    nlpcda_env.yml
## @ nlpcda模型下载网址 

    https://github.com/ZhuiyiTechnology/pretrained-models?tab=readme-ov-file
    
    nlpcda github: https://gitcode.com/gh_mirrors/nl/nlpcda/blob/master/README.md
