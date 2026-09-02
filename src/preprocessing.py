"""
数据预处理：分层抽样划分 + 标准化。
KNN/SVM/LR 需标准化数据；决策树用原始数据（保持规则阈值可读性）。
"""
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from config import RANDOM_STATE, TEST_SIZE


def split_and_scale(X, y):
    """
    分层划分数据集并标准化。

    Returns:
        X_train_std, X_test_std: 标准化后的训练/测试集（KNN/SVM/LR 用）
        X_train_raw, X_test_raw: 原始尺度训练/测试集（决策树/可解释性 用）
        y_train, y_test: 标签
        scaler: 拟合好的 StandardScaler（供后续使用）
    """
    # 分层抽样划分
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"  训练集: {len(X_train_raw)} 条  |  测试集: {len(X_test_raw)} 条")
    print(f"  训练集类别分布: {dict(zip(*[list(x) for x in __import__('numpy').unique(y_train, return_counts=True)]))}")
    print(f"  测试集类别分布: {dict(zip(*[list(x) for x in __import__('numpy').unique(y_test, return_counts=True)]))}")

    # 标准化（仅 fit 训练集）
    scaler = StandardScaler()
    X_train_std = scaler.fit_transform(X_train_raw)
    X_test_std = scaler.transform(X_test_raw)

    return X_train_std, X_test_std, X_train_raw, X_test_raw, y_train, y_test, scaler
