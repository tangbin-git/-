"""
主入口：一键运行全流程。
执行顺序：EDA → 预处理 → 训练 → 评估 → 决策边界 → 决策树规则 → SHAP → 报告 → PPT
"""
import sys
import os
import time

# 将 src 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_matplotlib, ensure_dirs, MODEL_NAMES_CN
from data_loader import load_iris_data
from eda import run_eda
from preprocessing import split_and_scale
from models import train_all_models
from evaluate import (
    evaluate_model, plot_confusion_matrices, plot_roc_curves,
    plot_metrics_bar, save_metrics_table,
)
from visualize_boundary import plot_decision_boundaries
from interpret_tree import interpret_decision_tree
from interpret_shap import run_shap_analysis


def main():
    print("=" * 60)
    print("  鸢尾花分类——从模型对比到可解释性")
    print("=" * 60)

    total_start = time.time()

    # 0. 初始化
    print("\n[0] 初始化环境...")
    setup_matplotlib()
    ensure_dirs()

    # 1. 加载数据
    print("\n[1] 加载 Iris 数据集...")
    X, y, feature_names, target_names, df = load_iris_data()
    print(f"  数据形状: X={X.shape}, y={y.shape}")
    print(f"  特征: {feature_names}")
    print(f"  类别: {target_names}")

    # 2. EDA
    print("\n[2] 探索性数据分析...")
    run_eda(df, X, y, feature_names, target_names)

    # 3. 预处理
    print("\n[3] 数据预处理（划分 + 标准化）...")
    X_train_std, X_test_std, X_train_raw, X_test_raw, y_train, y_test, scaler = \
        split_and_scale(X, y)

    # 4. 训练模型
    print("\n[4] 训练四个模型...")
    models, uses_std = train_all_models(X_train_std, X_train_raw, y_train)

    # 5. 评估
    print("\n[5] 模型评估...")
    metrics_all = []
    for name, model in models.items():
        X_test = X_test_std if uses_std[name] else X_test_raw
        m = evaluate_model(model, X_test, y_test, name)
        metrics_all.append(m)
        print(f"  {MODEL_NAMES_CN[name]}: 准确率={m['准确率']:.4f}, F1={m['F1(Macro)']:.4f}, AUC={m['AUC(micro)']:.4f}" if m['AUC(micro)'] else
              f"  {MODEL_NAMES_CN[name]}: 准确率={m['准确率']:.4f}, F1={m['F1(Macro)']:.4f}")

    # 6. 评估图表
    print("\n[6] 生成评估图表...")
    plot_confusion_matrices(models, uses_std, X_test_std, X_test_raw, y_test)
    plot_roc_curves(models, uses_std, X_test_std, X_test_raw, y_test)
    plot_metrics_bar(metrics_all)
    metrics_df = save_metrics_table(metrics_all)
    print("\n  指标汇总表:")
    print(metrics_df.to_string(index=False))

    # 7. 决策边界
    print("\n[7] 决策边界可视化...")
    plot_decision_boundaries(X, y, feature_names)

    # 8. 决策树规则
    print("\n[8] 决策树规则提取...")
    interpret_decision_tree(models['tree'], feature_names, target_names)

    # 9. SHAP 分析
    print("\n[9] SHAP 可解释性分析...")
    run_shap_analysis(models, uses_std, X_train_std, X_train_raw,
                      X_test_std, X_test_raw, y_train, feature_names)

    # 10. 生成报告和 PPT
    print("\n[10] 生成课程设计报告 (.docx)...")
    try:
        from generate_report import generate_report
        generate_report(metrics_all, metrics_df, feature_names, target_names)
    except Exception as e:
        print(f"  [报告生成失败] {e}")

    print("\n[11] 生成答辩 PPT (.pptx)...")
    try:
        from generate_ppt import generate_ppt
        generate_ppt(metrics_all, metrics_df, feature_names, target_names)
    except Exception as e:
        print(f"  [PPT生成失败] {e}")

    # 总结
    total_time = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"  全流程完成！总耗时: {total_time:.1f}s")
    print(f"  图表输出: outputs/figures/")
    print(f"  规则文件: outputs/rules/")
    print(f"  指标结果: outputs/results/")
    print(f"  报告文件: report/鸢尾花分类课程设计报告.docx")
    print(f"  PPT文件:  slides/鸢尾花分类答辩PPT.pptx")
    print("=" * 60)


if __name__ == '__main__':
    main()
