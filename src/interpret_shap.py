"""
SHAP 可解释性分析（题目核心）：
- SVM 用 KernelExplainer（background 取 50 条训练样本控制计算量）
- 决策树用 TreeExplainer（秒级计算）
- 生成 summary_plot、dependence_plot、force_plot
- 降级方案：若 shap 不可用，回退到 permutation_importance
"""
import os
import numpy as np
import matplotlib.pyplot as plt

from config import FIGURES_DIR, RESULTS_DIR, FEATURE_NAMES_SHORT, TARGET_NAMES_SHORT, setup_matplotlib


def run_shap_analysis(models, uses_std, X_train_std, X_train_raw,
                      X_test_std, X_test_raw, y_train, feature_names):
    """执行 SHAP 分析（SVM + 决策树）。"""
    print("[可解释性-SHAP] 开始 SHAP 分析...")

    try:
        import shap
        print("  shap 库已加载，版本:", shap.__version__)
    except ImportError:
        print("  [警告] shap 库未安装，降级为 permutation_importance")
        _fallback_permutation_importance(models, uses_std, X_test_std, X_test_raw,
                                         y_train, feature_names)
        return

    # --- SVM SHAP 分析 ---
    print("  [SVM] 使用 KernelExplainer 计算 SHAP 值...")
    # 取训练集子集作为 background 控制计算量
    bg_idx = np.random.RandomState(42).choice(
        len(X_train_std), size=min(50, len(X_train_std)), replace=False
    )
    background = X_train_std[bg_idx]
    # 测试集取前 30 条解释
    X_explain_std = X_test_std[:30]

    explainer_svm = shap.KernelExplainer(models['svm'].predict_proba, background)
    shap_values_svm = explainer_svm.shap_values(X_explain_std, silent=True)

    # 图12: SVM SHAP summary plot
    _save_shap_summary(shap_values_svm, X_explain_std, feature_names,
                       '12_shap_summary_svm', 'SVM (KernelExplainer)')

    # 图13: SVM SHAP dependence plot
    _save_shap_dependence(shap_values_svm, X_explain_std, feature_names,
                          '13_shap_dependence_svm', 'SVM')

    # --- 决策树 SHAP 分析 ---
    print("  [决策树] 使用 TreeExplainer 计算 SHAP 值...")
    # TreeExplainer 用原始数据
    X_explain_raw = X_test_raw[:30]
    explainer_tree = shap.TreeExplainer(models['tree'])
    shap_values_tree = explainer_tree.shap_values(X_explain_raw)

    # 图14: Tree SHAP summary plot
    _save_shap_summary(shap_values_tree, X_explain_raw, feature_names,
                       '14_shap_summary_tree', '决策树 (TreeExplainer)')

    # 图15: Tree SHAP dependence plot
    _save_shap_dependence(shap_values_tree, X_explain_raw, feature_names,
                          '15_shap_dependence_tree', '决策树')

    # 图16: Force plot（单样本局部解释，HTML）
    _save_force_plot(explainer_tree, shap_values_tree, X_explain_raw,
                     feature_names, models['tree'])

    print("[可解释性-SHAP] 完成。")


def _save_shap_summary(shap_values, X_explain, feature_names, filename, model_label):
    """保存 SHAP summary plot。"""
    import shap

    fig, ax = plt.subplots(figsize=(10, 6))
    # shap_values 可能是 list（多类）或 ndarray
    # 对多分类取各类 SHAP 值的平均绝对值
    if isinstance(shap_values, list):
        # list of arrays, each (n_samples, n_features) for one class
        sv_combined = np.mean([np.abs(sv) for sv in shap_values], axis=0)
    else:
        # ndarray: (n_samples, n_features, n_classes) or (n_samples, n_features)
        if shap_values.ndim == 3:
            sv_combined = np.mean(np.abs(shap_values), axis=2)
        else:
            sv_combined = np.abs(shap_values)

    shap.summary_plot(sv_combined, X_explain, feature_names=feature_names,
                      show=False, plot_type='bar')
    plt.title(f'图  {model_label} SHAP 特征重要性 Summary',
              fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, f'{filename}.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  -> {path}")


def _save_shap_dependence(shap_values, X_explain, feature_names, filename, model_label):
    """保存 SHAP dependence plot（前2重要特征）。"""
    import shap

    # 确定 SHAP 值格式
    if isinstance(shap_values, list):
        sv = shap_values[0]  # 取第一类
    else:
        if shap_values.ndim == 3:
            sv = shap_values[:, :, 0]
        else:
            sv = shap_values

    # 找前2重要特征
    mean_abs = np.mean(np.abs(sv), axis=0)
    top2 = np.argsort(mean_abs)[::-1][:2]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for idx, feat_idx in enumerate(top2):
        ax = axes[idx]
        ax.scatter(X_explain[:, feat_idx], sv[:, feat_idx],
                   c=X_explain[:, feat_idx], cmap='coolwarm', s=40,
                   edgecolors='black', linewidth=0.5, alpha=0.8)
        ax.set_xlabel(feature_names[feat_idx], fontsize=11)
        ax.set_ylabel('SHAP 值', fontsize=11)
        ax.set_title(f'{feature_names[feat_idx]} 依赖图 ({model_label})',
                     fontsize=12, fontweight='bold')
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
        ax.grid(True, alpha=0.3)

    plt.suptitle(f'图  {model_label} SHAP 依赖图（Top-2 特征）',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, f'{filename}.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  -> {path}")


def _save_force_plot(explainer, shap_values, X_explain, feature_names, model):
    """保存 SHAP force plot 为 HTML（单样本局部解释）。"""
    import shap

    # 取第一个测试样本
    if isinstance(shap_values, list):
        sv_sample = shap_values[0][0:1]
    else:
        if shap_values.ndim == 3:
            sv_sample = shap_values[0:1, :, 0]
        else:
            sv_sample = shap_values[0:1]

    force_plot = shap.force_plot(
        explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray))
        else explainer.expected_value,
        sv_sample,
        X_explain[0:1],
        feature_names=feature_names,
    )

    html_path = os.path.join(FIGURES_DIR, '16_shap_force_plot.html')
    shap.save_html(html_path, force_plot)
    print(f"  -> {html_path}")

    # 同时保存一张 force plot 截图（matplotlib 版本）
    try:
        fig, ax = plt.subplots(figsize=(12, 3))
        shap.waterfall_plot(shap.Explanation(
            values=sv_sample[0],
            base_values=explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray))
            else explainer.expected_value,
            data=X_explain[0],
            feature_names=feature_names,
        ), show=False)
        plt.title('图16  SHAP 单样本局部解释 (Waterfall)', fontsize=13, fontweight='bold')
        plt.tight_layout()
        png_path = os.path.join(FIGURES_DIR, '16_shap_force_plot.png')
        plt.savefig(png_path, bbox_inches='tight')
        plt.close()
        print(f"  -> {png_path}")
    except Exception as e:
        print(f"  [提示] waterfall 图生成失败: {e}，HTML 版本已保存。")


def _fallback_permutation_importance(models, uses_std, X_test_std, X_test_raw,
                                     y_test, feature_names):
    """降级方案：permutation importance。"""
    from sklearn.inspection import permutation_importance

    print("  [降级] 使用 permutation_importance 替代 SHAP")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for idx, (name, model) in enumerate(models.items()):
        X = X_test_std if uses_std[name] else X_test_raw
        result = permutation_importance(model, X, y_test, n_repeats=10,
                                        random_state=42, scoring='f1_macro')
        importances_mean = result.importances_mean
        sorted_idx = np.argsort(importances_mean)[::-1]

        ax = axes[idx]
        ax.barh(range(len(feature_names)),
                importances_mean[sorted_idx],
                color=['#E74C3C', '#2ECC71', '#3498DB', '#F39C12'],
                alpha=0.8)
        ax.set_yticks(range(len(feature_names)))
        ax.set_yticklabels([feature_names[i] for i in sorted_idx], fontsize=10)
        ax.set_xlabel('置换重要性', fontsize=10)
        ax.set_title(f'{name} 置换重要性', fontsize=12, fontweight='bold')
        ax.invert_yaxis()

    plt.suptitle('图  置换重要性（SHAP 降级方案）', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'permutation_importance_fallback.png')
    plt.savefig(path)
    plt.close()
    print(f"  -> {path}")
