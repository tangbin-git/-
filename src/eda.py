"""
探索性数据分析（EDA）：特征分布、箱线图、散点矩阵、相关性热力图、统计摘要。
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from config import FIGURES_DIR, RESULTS_DIR, TARGET_NAMES_SHORT, FEATURE_NAMES_SHORT, setup_matplotlib

# 三类颜色：红 / 绿 / 蓝
CLASS_COLORS = ['#E74C3C', '#2ECC71', '#3498DB']
CLASS_CMAP = ListedColormap(CLASS_COLORS)


def run_eda(df, X, y, feature_names, target_names):
    """执行全部 EDA 分析，生成图表和统计文件。"""
    print("[EDA] 开始探索性数据分析...")

    _plot_feature_distribution(df, feature_names, target_names)
    _plot_boxplots(df, feature_names, target_names)
    _plot_scatter_matrix(X, y, feature_names, target_names)
    _plot_correlation_heatmap(X, feature_names)
    _save_statistics(df, feature_names, target_names)

    print("[EDA] 完成，共生成 4 张图表 + 1 个统计摘要表。")


def _plot_feature_distribution(df, feature_names, target_names):
    """图1：特征分布直方图（4子图，按类别着色）。"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for idx, feat in enumerate(feature_names):
        ax = axes[idx]
        for cls_idx, cls in enumerate(target_names):
            data = df[df['类别'] == cls][feat]
            ax.hist(data, bins=12, alpha=0.6, color=CLASS_COLORS[cls_idx],
                    label=cls, edgecolor='white', linewidth=0.5)
        ax.set_title(f'{feat} 分布', fontsize=13, fontweight='bold')
        ax.set_xlabel(feat, fontsize=11)
        ax.set_ylabel('频数', fontsize=11)
        ax.legend(fontsize=9)

    plt.suptitle('图1  各特征按类别分布直方图', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '01_feature_distribution.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def _plot_boxplots(df, feature_names, target_names):
    """图2：箱线图（4子图，展示离群值）。"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for idx, feat in enumerate(feature_names):
        ax = axes[idx]
        data_by_class = [df[df['类别'] == cls][feat].values for cls in target_names]
        bp = ax.boxplot(data_by_class, labels=target_names, patch_artist=True,
                        widths=0.6, medianprops=dict(color='black', linewidth=1.5))
        for patch, color in zip(bp['boxes'], CLASS_COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title(f'{feat} 箱线图', fontsize=13, fontweight='bold')
        ax.set_xlabel('类别', fontsize=11)
        ax.set_ylabel(feat, fontsize=11)

    plt.suptitle('图2  各特征按类别箱线图', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '02_boxplots.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def _plot_scatter_matrix(X, y, feature_names, target_names):
    """图3：散点矩阵图（4特征两两散点，对角线为分布）。"""
    n = len(feature_names)
    fig, axes = plt.subplots(n, n, figsize=(14, 12))

    for i in range(n):
        for j in range(n):
            ax = axes[i][j]
            if i == j:
                # 对角线：画分布直方图
                for cls_idx, cls in enumerate(target_names):
                    mask = y == cls_idx
                    ax.hist(X[mask, i], bins=10, alpha=0.6,
                            color=CLASS_COLORS[cls_idx], edgecolor='white')
            else:
                # 散点
                for cls_idx, cls in enumerate(target_names):
                    mask = y == cls_idx
                    ax.scatter(X[mask, j], X[mask, i], c=CLASS_COLORS[cls_idx],
                               label=cls, s=20, alpha=0.7, edgecolors='white', linewidth=0.5)

            if i == n - 1:
                ax.set_xlabel(feature_names[j], fontsize=10)
            if j == 0:
                ax.set_ylabel(feature_names[i], fontsize=10)

            # 仅右下角显示图例
            if i == 0 and j == n - 1:
                ax.legend(fontsize=8, loc='upper right')

    plt.suptitle('图3  散点矩阵图（对角线为分布，非对角线为两两散点）',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '03_scatter_matrix.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def _plot_correlation_heatmap(X, feature_names):
    """图4：特征相关性热力图。"""
    corr = np.corrcoef(X.T)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

    # 标注数值
    for i in range(len(feature_names)):
        for j in range(len(feature_names)):
            value = corr[i, j]
            color = 'white' if abs(value) > 0.7 else 'black'
            ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                    fontsize=13, color=color, fontweight='bold')

    ax.set_xticks(range(len(feature_names)))
    ax.set_yticks(range(len(feature_names)))
    ax.set_xticklabels(feature_names, fontsize=11, rotation=30, ha='right')
    ax.set_yticklabels(feature_names, fontsize=11)
    ax.set_title('图4  特征相关性热力图', fontsize=14, fontweight='bold')
    fig.colorbar(im, ax=ax, label='相关系数')

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, '04_correlation_heatmap.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")


def _save_statistics(df, feature_names, target_names):
    """统计摘要表导出 CSV。"""
    # 整体描述
    desc = df[feature_names].describe()
    desc_str = desc.copy()
    desc_str.index = ['计数', '均值', '标准差', '最小值', '25%', '中位数', '75%', '最大值']

    # 按类别均值
    group_mean = df.groupby('类别')[feature_names].mean()

    # 合并
    summary = pd.concat([desc_str, group_mean], axis=0)
    path = os.path.join(RESULTS_DIR, 'statistics_summary.csv')
    summary.to_csv(path, encoding='utf-8-sig')
    print(f"  -> {path}")
