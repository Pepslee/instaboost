import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.linear_model import Perceptron
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron
from catboost import CatBoostClassifier, Pool, cv
from sklearn .preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from joblib import dump, load
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler



def IoU(y, x, thresh=0):
    x = x > thresh
    y = y > 0
    intersection = np.sum(np.bitwise_and(x, y))
    # if intersection == 0:
    #     return 0
    union = np.sum(np.bitwise_or(x, y))
    # if union == 0:
    #     return 0
    return intersection/(union + 0.0001)


page = 'p.i.n.k.m.a.n'
forward_path = os.path.join('p.i.n.k.m.a.n', page + '_follows')
backward_path = os.path.join('p.i.n.k.m.a.n', page + '_followers')


params = {'iterations': None,
          'custom_loss': ['F1'],
          # 'loss_function': 'F1',
          'random_seed': 42,
          'logging_level': 'Silent',
          'class_weights': [0.7, 9],
          'learning_rate': None}
model = CatBoostClassifier(**params)


# tree = Perceptron(n_iter=10, eta0=0.9, random_state=0, class_weight={0: 0.08, 1: .91})

model = DecisionTreeClassifier(criterion='entropy', max_depth=20, random_state=0, class_weight={0: 0.6, 1: 9})
# tree = SVC(class_weight={0: 0.1, 1: 0.9})
# ada = AdaBoostClassifier(base_estimator=tree, n_estimators=500, learning_rate=0.01, random_state=0)

# forward_path = 'p.i.n.k.m.a.n/forward_dp'
# backward_path = '/home/panchenko/PycharmProjects/classificators/train_data/backward_dp'

select = SelectKBest(chi2, k=50)

# X_new = select.fit_transform(train_data_features, train["sentiment"])

forward_df = pd.read_csv(forward_path)
forward_df['comeback'] = 0
forward_names = set(forward_df['name'])
backward_names = set(pd.read_csv(backward_path, header=None).values.flatten().tolist())

true_backward = list(forward_names.intersection(backward_names))
forward_df['comeback'] = 0
forward_df.loc[forward_df['name'].isin(true_backward), 'comeback'] = 1
# forward_df['posts'] = forward_df['posts']/(forward_df['posts'].mean())
forward_df['fb_factor'] = forward_df['follow']/(forward_df['followers'] + 1)

# forward_df['id'] = np.log10(forward_df['id']+1)
# forward_df['followers'] = np.log10(forward_df['followers']+1)
# forward_df['follow'] = np.log10(forward_df['follow']+1)
#
# forward_df['posts'] = np.log10(forward_df['posts']+1)
stratify = forward_df[['comeback']].values.ravel()
# feature_names = ['id', 'followers', 'follow', 'fb_factor', 'posts']
feature_names = ['id', 'followers', 'follow', 'fb_factor', 'posts']
X = forward_df[feature_names]
# X = forward_df[['id', 'followers', 'follow', 'posts']]
sc = StandardScaler()
# sc = MinMaxScaler()
# sc.fit(X.values)
# X_train, X_test, Y_train, Y_test = train_test_split(X.values, stratify, test_size=0.1, random_state=0, stratify=stratify)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=10)
spl = skf.get_n_splits(X.values, stratify)
sc = MinMaxScaler()

input = X.values
input = sc.fit_transform(input)

classifiers = [
    RandomForestClassifier(class_weight={0: 1, 1: 9}, max_depth=40, n_estimators=5, random_state=1),
    LogisticRegression(max_iter=30, multi_class='multinomial', solver='lbfgs', class_weight={0: 0.8, 1: 9}, random_state=50, l1_ratio=0.5),
    DecisionTreeClassifier(criterion='entropy', max_depth=100, random_state=0, class_weight={0: 1, 1: 9})
    ]


for i, model in enumerate(classifiers):


    mean_precision = []
    for train_index, test_index in skf.split(X.values, stratify):
        X_train, X_test =input[train_index], input[test_index]
        Y_train, Y_test = stratify[train_index], stratify[test_index]

        class_weight = [Y_train.sum()/(Y_train.sum() + (1-Y_train).sum()), (1-Y_train).sum()/(Y_train.sum() + (1-Y_train).sum())]

        # X_train = train[['id', 'followers', 'follow', 'fb_factor', 'posts', 'time']]
        # Y_train = train[['comeback']]
        # X_test = test[['id', 'followers', 'follow', 'fb_factor', 'posts', 'time']]
        # Y_test = test[['comeback']]

        # model = DecisionTreeClassifier(criterion='gini', max_depth=100, random_state=10, class_weight={0: 0.9, 1: 90})
        # model = SVC(class_weight={0: 1, 1: 9}, gamma='auto')
        model = model.fit(X_train, Y_train)

        # model = CatBoostClassifier(**params)
        # model.fit(X_train, Y_train, eval_set=(X_test, Y_test), logging_level='Silent')

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # print((tree_train, tree_test))

        acc_train = np.logical_and(Y_train, y_train_pred).sum()/Y_train.sum()
        acc_test = np.logical_and(Y_test, y_test_pred).sum()/Y_test.sum()

        iou_train = IoU(Y_train, y_train_pred)
        iou_test = IoU(Y_test, y_test_pred)

        precision = metrics.precision_score(Y_test, y_test_pred)

        # print('Fold:  ')
        # print('Acc  ', (acc_train, acc_test))
        # print('IOU  ', (iou_train, iou_test))
        mean_precision.append(precision)
        # print('precision  ', precision)



        res = pd.DataFrame()
        res['origin'] = Y_test
        res['pred'] = y_test_pred
        pass
    # if np.asarray(mean_precision).mean() > 0.1 and 0 not in mean_precision:
    print('  ')
    print('Classificator № ' + str(i))
    print(mean_precision)
    dump(model, os.path.join('p.i.n.k.m.a.n', 'filename_' + str(i) + '.joblib'))

# tree = ada.fit(X_train, Y_train)
#
# y_train_pred = ada.predict(X_train)
# y_test_pred = ada.predict(X_test)
# # tree_train = accuracy_score(Y_train, y_train_pred)
# # tree_test = accuracy_score(Y_test, y_test_pred)
#
# print((tree_train, tree_test))
#
# tree_train = np.logical_and(Y_train, y_train_pred).sum()/Y_train.sum()
# tree_test = np.logical_and(Y_test, y_test_pred).sum()/Y_test.sum()
#
# # print((tree_train, tree_test))
#
# print(metrics.classification_report(Y_test, y_test_pred))
# pass
