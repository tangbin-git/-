"""
全局配置中心：路径常量、随机种子、模型超参数、中文字体设置。
所有模块均依赖此文件。
"""
import os
import matplotlib
import matplotlib.pyplot as plt

# ========== 路径常量 ==========
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'figures')
RULES_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'rules')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'results')
REPORT_DIR = os.path.join(PROJECT_ROOT, 'report')
SLIDES_DIR = os.path.join(PROJECT_ROOT, 'slides')

# ========== 实验参数 ==========
RANDOM_STATE = 42
TEST_SIZE = 0.3

# ========== 模型超参数 ==========
MODEL_PARAMS = {
    'knn': {
        'n_neighbors': 5,
        'weights': 'uniform',
    },
    'svm': {
        'C': 1.0,
        'gamma': 'scale',
        'kernel': 'rbf',
        'probability': True,   # 必须开启才能画 ROC
        'decision_function_shape': 'ovr',
    },
    'tree': {
        'max_depth': 3,
        'random_state': RANDOM_STATE,
        'criterion': 'gini',
    },
    'lr': {
        'max_iter': 200,
        'multi_class': 'multinomial',
        'solver': 'lbfgs',
        'random_state': RANDOM_STATE,
    },
}

# ========== 模型中文名称 ==========
MODEL_NAMES_CN = {
    'knn': 'K近邻 (KNN)',
    'svm': '支持向量机 (RBF-SVM)',
    'tree': '决策树 (CART)',
    'lr': '逻辑回归 (Softmax)',
}

# ========== 特征中英文映射 ==========
FEATURE_NAMES_CN = {
    'sepal length (cm)': '花萼长度',
    'sepal width (cm)': '花萼宽度',
    'petal length (cm)': '花瓣长度',
    'petal width (cm)': '花瓣宽度',
}

FEATURE_NAMES_SHORT = ['花萼长度', '花萼宽度', '花瓣长度', '花瓣宽度']

# ========== 类别中英文映射 ==========
TARGET_NAMES_CN = {
    'setosa': '山鸢尾',
    'versicolor': '变色鸢尾',
    'virginica': '维吉尼亚鸢尾',
}

TARGET_NAMES_SHORT = ['山鸢尾', '变色鸢尾', '维吉尼亚鸢尾']


# ========== 中文字体设置 ==========
def setup_matplotlib():
    """统一设置 matplotlib 中文字体，避免乱码。"""
    matplotlib.rcParams['font.sans-serif'] = ['STheiti', 'Arial Unicode MS', 'SimHei', 'sans-serif']
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['figure.dpi'] = 150
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['savefig.bbox'] = 'tight'


def ensure_dirs():
    """创建所有输出目录。"""
    for d in [DATA_DIR, FIGURES_DIR, RULES_DIR, RESULTS_DIR, REPORT_DIR, SLIDES_DIR]:
        os.makedirs(d, exist_ok=True)
