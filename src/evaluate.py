"""
模型评估：准确率、F1-Macro、混淆矩阵、ROC曲线、指标柱状图。
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc,
)
from sklearn.preprocessing import label_binarize
from sklearn.metrics import ConfusionMatrixDisplay

from config import FIGURES_DIR, RESULTS_DIR, TARGET_NAMES_SHORT, MODEL_NAMES_CN, setup_matplotlib


def evaluate_model(model, X_test, y_test, name):
    """评估单个模型，返回指标字典。"""
    y_pred = model.predict(X_test)

    metrics = {
        '模型': MODEL_NAMES_CN.get(name, name),
        '准确率': accuracy_score(y_test, y_pred),
        '精确率(Macro)': precision_score(y_test, y_pred, average='macro'),
        '召回率(Macro)': recall_score(y_test, y_pred, average='macro'),
        'F1(Macro)': f1_score(y_test, y_pred, average='macro'),
    }

    # AUC（需要 predict_proba 或 decision_function）
    try:
        y_proba = model.predict_proba(X_test)
        y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
        fpr, tpr, _ = roc_curve(y_test_bin.ravel(), y_proba.ravel())
        metrics['AUC(micro)'] = auc(fpr, tpr)
    except Exception:
        metrics['AUC(micro)'] = None

    report = classification_report(y_test, y_pred, target_names=TARGET_NAMES_SHORT, output_dict=True)
    metrics['classification_report'] = report

    return metrics


def plot_confusion_matrices(models, uses_std, X_test_std, X_test_raw, y_test):
    """图5：四模型混淆矩阵（2×2子图）。"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for idx, (name, model) in enumerate(models.items()):
        X = X_test_std if uses_std[name] else X_test_raw
        y_pred = model.predict(X)
        cm = confusion_matrix(y_test, y_pred)

        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=TARGET_NAMES_SHORT)
        disp.plot(ax=axes[idx], cmap='Blues', values_format='d', colorbar=False)
        axes[idx].set_title(f'{MODEL_NAMES_CN[name]}', fontsize=13, fontweight='bold')

    plt.suptitle('图5  四模型混淆矩阵对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '05_confusion_matrices.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def plot_roc_curves(models, uses_std, X_test_std, X_test_raw, y_test):
    """图6：四模型ROC曲线（OvR micro-average，叠加在一张图上）。"""
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    colors = ['#E74C3C', '#2ECC71', '#3498DB', '#F39C12']

    fig, ax = plt.subplots(figsize=(8, 7))

    for idx, (name, model) in enumerate(models.items()):
        X = X_test_std if uses_std[name] else X_test_raw
        try:
            y_proba = model.predict_proba(X)
            fpr, tpr, _ = roc_curve(y_test_bin.ravel(), y_proba.ravel())
            roc_auc = auc(fpr, tpr)
            ax.plot(fpr, tpr, color=colors[idx], linewidth=2,
                    label=f'{MODEL_NAMES_CN[name]} (AUC={roc_auc:.4f})')
        except Exception:
            ax.plot([], [], color=colors[idx], label=f'{MODEL_NAMES_CN[name]} (N/A)')

    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='随机分类')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.05])
    ax.set_xlabel('假阳性率 (FPR)', fontsize=12)
    ax.set_ylabel('真阳性率 (TPR)', fontsize=12)
    ax.set_title('图6  四模型ROC曲线对比 (OvR Micro-Average)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '06_roc_curves.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def plot_metrics_bar(metrics_all):
    """图7：准确率与F1-Macro柱状对比图。"""
    names = [m['模型'] for m in metrics_all]
    acc = [m['准确率'] for m in metrics_all]
    f1 = [m['F1(Macro)'] for m in metrics_all]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, acc, width, label='准确率', color='#3498DB', alpha=0.8)
    bars2 = ax.bar(x + width/2, f1, width, label='F1(Macro)', color='#E74C3C', alpha=0.8)

    # 在柱上标数值
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.005, f'{h:.3f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.005, f'{h:.3f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.set_ylabel('分数', fontsize=12)
    ax.set_title('图7  四模型准确率与F1-Macro对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim([0.8, 1.02])
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '07_metrics_bar.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def save_metrics_table(metrics_all):
    """指标汇总表导出 CSV 和 JSON。"""
    # CSV
    rows = []
    for m in metrics_all:
        rows.append({
            '模型': m['模型'],
            '准确率': f"{m['准确率']:.4f}",
            '精确率(Macro)': f"{m['精确率(Macro)']:.4f}",
            '召回率(Macro)': f"{m['召回率(Macro)']:.4f}",
            'F1(Macro)': f"{m['F1(Macro)']:.4f}",
            'AUC(micro)': f"{m['AUC(micro)']:.4f}" if m['AUC(micro)'] else 'N/A',
        })
    df = pd.DataFrame(rows)
    csv_path = os.path.join(RESULTS_DIR, 'metrics_summary.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"  -> {csv_path}")

    # JSON（含分类报告）
    json_data = {}
    for m in metrics_all:
        json_data[m['模型']] = {
            '准确率': m['准确率'],
            '精确率(Macro)': m['精确率(Macro)'],
            '召回率(Macro)': m['召回率(Macro)'],
            'F1(Macro)': m['F1(Macro)'],
            'AUC(micro)': m['AUC(micro)'],
            '分类报告': m['classification_report'],
        }
    json_path = os.path.join(RESULTS_DIR, 'metrics_summary.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {json_path}")

    return df
