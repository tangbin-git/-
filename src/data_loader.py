"""
数据加载模块：从 sklearn 加载 Iris 数据集，组装为 DataFrame，导出 CSV。
"""
import os
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

from config import DATA_DIR, FEATURE_NAMES_SHORT, TARGET_NAMES_SHORT, ensure_dirs


def load_iris_data():
    """
    加载 Iris 数据集。

    Returns:
        X (np.ndarray): 150×4 特征矩阵
        y (np.ndarray): 150 标签
        feature_names (list): 特征中文名
        target_names (list): 类别中文名
        df (pd.DataFrame): 含中文列名的完整 DataFrame
    """
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = FEATURE_NAMES_SHORT
    target_names = TARGET_NAMES_SHORT

    df = pd.DataFrame(X, columns=feature_names)
    df['类别'] = [target_names[i] for i in y]

    # 导出 CSV 供离线使用
    ensure_dirs()
    csv_path = os.path.join(DATA_DIR, 'iris.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"  数据集已导出: {csv_path}  ({len(df)} 条样本)")

    return X, y, feature_names, target_names, df
