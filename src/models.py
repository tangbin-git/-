"""
模型定义与训练：KNN、SVM(RBF)、决策树、逻辑回归。
KNN/SVM/LR 用标准化数据；决策树用原始数据（保持规则可读性）。
"""
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from config import MODEL_PARAMS, MODEL_NAMES_CN


def train_all_models(X_train_std, X_train_raw, y_train):
    """
    训练四个模型。

    Args:
        X_train_std: 标准化训练集（KNN/SVM/LR）
        X_train_raw: 原始尺度训练集（决策树）
        y_train: 训练标签

    Returns:
        models dict: {'knn': model, 'svm': model, 'tree': model, 'lr': model}
        uses_std dict: 记录每个模型用的是否是标准化数据，供评估时选择对应测试集
    """
    print("[模型训练] 开始训练四个模型...")

    models = {}
    uses_std = {}

    # KNN — 标准化数据
    models['knn'] = KNeighborsClassifier(**MODEL_PARAMS['knn'])
    models['knn'].fit(X_train_std, y_train)
    uses_std['knn'] = True
    print(f"  KNN 训练完成 (k={MODEL_PARAMS['knn']['n_neighbors']})")

    # SVM-RBF — 标准化数据
    models['svm'] = SVC(**MODEL_PARAMS['svm'])
    models['svm'].fit(X_train_std, y_train)
    uses_std['svm'] = True
    print(f"  SVM-RBF 训练完成 (C={MODEL_PARAMS['svm']['C']}, gamma={MODEL_PARAMS['svm']['gamma']})")

    # 决策树 — 原始数据（规则阈值保持 cm 单位）
    models['tree'] = DecisionTreeClassifier(**MODEL_PARAMS['tree'])
    models['tree'].fit(X_train_raw, y_train)
    uses_std['tree'] = False
    print(f"  决策树训练完成 (max_depth={MODEL_PARAMS['tree']['max_depth']})")

    # 逻辑回归 — 标准化数据
    models['lr'] = LogisticRegression(**MODEL_PARAMS['lr'])
    models['lr'].fit(X_train_std, y_train)
    uses_std['lr'] = True
    print(f"  逻辑回归训练完成 (solver={MODEL_PARAMS['lr']['solver']})")

    return models, uses_std
