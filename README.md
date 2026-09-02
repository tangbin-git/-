# 鸢尾花分类——从模型对比到可解释性

机器学习课程设计项目，题号19。

## 项目简介

对鸢尾花（Iris）数据集进行多分类任务，系统对比 KNN、SVM(RBF)、决策树、逻辑回归 四种分类器的决策边界，并通过决策树规则提取和SHAP分析实现模型可解释性。

## 环境要求

- Python 3.9+
- 核心依赖：scikit-learn, pandas, matplotlib, numpy, shap, python-docx, python-pptx

安装依赖：
```bash
pip install -r requirements.txt
```

## 运行方式

一键运行全流程（数据加载→EDA→训练→评估→可视化→可解释性→报告→PPT）：
```bash
cd src
python main.py
```

运行完成后，所有输出在 `outputs/`、`report/`、`slides/` 目录中。

## 目录结构

```
机器学习课程设计/
├── data/                        # 数据集（iris.csv）
├── src/                         # 源代码
│   ├── config.py                # 全局配置
│   ├── data_loader.py           # 数据加载
│   ├── eda.py                   # 探索性数据分析
│   ├── preprocessing.py         # 数据预处理
│   ├── models.py                # 模型训练
│   ├── evaluate.py              # 模型评估
│   ├── visualize_boundary.py    # 决策边界可视化
│   ├── interpret_tree.py        # 决策树规则提取
│   ├── interpret_shap.py        # SHAP可解释性分析
│   ├── generate_report.py       # 生成.docx报告
│   ├── generate_ppt.py          # 生成.pptx答辩PPT
│   └── main.py                  # 主入口
├── outputs/
│   ├── figures/                 # 18张图表
│   ├── rules/                   # 决策树规则文件
│   └── results/                 # 指标汇总CSV/JSON
├── report/                      # 课程设计报告.docx
├── slides/                      # 答辩PPT.pptx
├── requirements.txt
└── README.md
```

## 实验结果

| 模型 | 准确率 | F1(Macro) | AUC |
|------|--------|-----------|-----|
| KNN | 0.9111 | 0.9095 | 0.9909 |
| SVM-RBF | 0.9333 | 0.9333 | 0.9951 |
| 决策树 | 0.9778 | 0.9778 | 0.9951 |
| 逻辑回归 | 0.9111 | 0.9107 | 0.9938 |
