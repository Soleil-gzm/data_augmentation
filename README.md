# 用户语义增强

## 项目结构
Data_Augmentation_human/
├── data/                           # 原始数据目录
│   ├── test.xlsx                  	# 测试数据（少量样本）
│   └── all_data.xlsx               # 全量原始数据
├── output_excel/                   # 增强结果输出目录（自动生成）
│   └── *_augmented_*.xlsx          # 例：all_data_augmented_20250415_143022.xlsx
├── logs/                           # 日志目录（自动生成）
│   └── augment_*.log               # 例：augment_20250415_143022.log
├── scripts/                        # 脚本目录
│   ├── common/                     # 公共模块包
│   │   ├── __init__.py             # 空文件，使 common 成为 Python 包
│   │   ├── augment_utils.py        # 增强核心函数（simple_augment, augment_cell 等）
│   │   └── __pycache__/            # Python 字节码缓存（自动生成，已忽略）
│   └── main_augment.py             # 主入口脚本（命令行参数、日志、流程控制）
├── .gitignore                      # Git 忽略文件配置
└── README.md                       # 项目说明文档（待完善）

# nlpcda模型下载网址 https://github.com/ZhuiyiTechnology/pretrained-models?tab=readme-ov-file
nlpcda github: https://gitcode.com/gh_mirrors/nl/nlpcda/blob/master/README.md
model1: SimBERT Tiny
model2: SimBERT Small