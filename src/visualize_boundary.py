"""
决策边界可视化：选取两组2D特征对，绘制四模型决策边界。
注意：边界图仅用2个特征独立训练，用于可视化对比，非全特征模型。
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.inspection import DecisionBoundaryDisplay

from config import FIGURES_DIR, MODEL_NAMES_CN, MODEL_PARAMS, TARGET_NAMES_SHORT, setup_matplotlib
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

# 背景色 cmap
BG_CMAP = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
# 散点颜色
PT_COLORS = ['#E74C3C', '#2ECC71', '#3498DB']


def plot_decision_boundaries(X, y, feature_names):
    """
    绘制两组特征对的四模型决策边界。

    Args:
        X: 全特征数据 (150×4)
        y: 标签
        feature_names: 特征中文名列表
    """
    # 特征对选取
    pairs = [
        (2, 3, '花瓣长度', '花瓣宽度', '高区分度'),
        (0, 1, '花萼长度', '花萼宽度', '低区分度'),
    ]

    for pair_idx, (fi, fj, fname_i, fname_j, label) in enumerate(pairs):
        _plot_single_pair(X, y, feature_names, fi, fj, fname_i, fname_j, label, pair_idx)


def _plot_single_pair(X, y, feature_names, fi, fj, fname_i, fname_j, label, pair_idx):
    """绘制单个特征对的四模型决策边界。"""
    X_2d = X[:, [fi, fj]]

    # 为2特征数据训练四个独立模型
    models_2d = {
        'knn': KNeighborsClassifier(**MODEL_PARAMS['knn']),
        'svm': SVC(**MODEL_PARAMS['svm']),
        'tree': DecisionTreeClassifier(**MODEL_PARAMS['tree']),
        'lr': LogisticRegression(**MODEL_PARAMS['lr']),
    }
    for m in models_2d.values():
        m.fit(X_2d, y)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for idx, (name, model) in enumerate(models_2d.items()):
        ax = axes[idx]
        DecisionBoundaryDisplay.from_estimator(
            model, X_2d, cmap=BG_CMAP, ax=ax, alpha=0.4,
            response_method='predict',
            xlabel=fname_i, ylabel=fname_j,
        )
        # 叠加散点
        for cls_idx in range(3):
            mask = y == cls_idx
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                       c=PT_COLORS[cls_idx], edgecolors='black', s=30,
                       linewidth=0.5, label=TARGET_NAMES_SHORT[cls_idx], alpha=0.8)

        ax.set_title(f'{MODEL_NAMES_CN[name]}', fontsize=13, fontweight='bold')
        ax.set_xlabel(fname_i, fontsize=11)
        ax.set_ylabel(fname_j, fontsize=11)
        if idx == 0:
            ax.legend(fontsize=9, loc='upper left')

    pair_labels = ['花瓣长度 × 花瓣宽度（高区分度）', '花萼长度 × 花萼宽度（低区分度）']
    fig_num = 8 if pair_idx == 0 else 9
    plt.suptitle(f'图{fig_num}  {pair_labels[pair_idx]}决策边界对比',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, f'{fig_num:02d}_decision_boundary_{label}.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")
