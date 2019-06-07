import numpy as np
import pandas as pd
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn. tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.linear_model import Perceptron
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron
from catboost import CatBoostClassifier, Pool, cv
from sklearn .preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate





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


params = {'iterations': None,
          'custom_loss': ['F1'],
          # 'loss_function': 'F1',
          'random_seed': 42,
          'logging_level': 'Silent',
          'class_weights': [1, 9],
          'learning_rate': None}
model = CatBoostClassifier(**params)


# tree = Perceptron(n_iter=10, eta0=0.9, random_state=0, class_weight={0: 0.08, 1: .91})

model = DecisionTreeClassifier(criterion='entropy', max_depth=20, random_state=0, class_weight={0: 0.6, 1: 9})
# tree = SVC(class_weight={0: 0.1, 1: 0.9})
# ada = AdaBoostClassifier(base_estimator=tree, n_estimators=500, learning_rate=0.01, random_state=0)

forward_path = '/home/panchenko/PycharmProjects/classificators/train_data/forward_dp'
backward_path = '/home/panchenko/PycharmProjects/classificators/train_data/backward_dp'

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
forward_df['fb_factor'] = forward_df['follow']/forward_df['followers']+1

forward_df['id'] = np.log10(forward_df['id']+1)
forward_df['followers'] = np.log10(forward_df['followers']+1)
forward_df['follow'] = np.log10(forward_df['follow']+1)
forward_df['posts'] = np.log10(forward_df['posts']+1)
stratify = forward_df[['comeback']].values.ravel()
# feature_names = ['id', 'followers', 'follow', 'fb_factor', 'posts']
feature_names = ['id', 'followers', 'follow', 'fb_factor', 'posts']
X = forward_df[feature_names]
# X = forward_df[['id', 'followers', 'follow', 'posts']]
sc = StandardScaler()
sc = MinMaxScaler()
# sc.fit(X.values)
X_train, X_test, Y_train, Y_test = train_test_split(X.values, stratify, test_size=0.1, random_state=42, stratify=stratify)

skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=10)
spl = skf.get_n_splits(X.values, stratify)
for train_index, test_index in skf.split(X.values, stratify):
    X_train, X_test = X.values[train_index], X.values[test_index]
    Y_train, Y_test = stratify[train_index], stratify[test_index]



    # X_train = train[['id', 'followers', 'follow', 'fb_factor', 'posts', 'time']]
    # Y_train = train[['comeback']]
    # X_test = test[['id', 'followers', 'follow', 'fb_factor', 'posts', 'time']]
    # Y_test = test[['comeback']]

    model = DecisionTreeClassifier(criterion='entropy', max_depth=20, random_state=0, class_weight={0: 0.9, 1: 9})
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
    print('precision  ', precision)


    res = pd.DataFrame()
    res['origin'] = Y_test
    res['pred'] = y_test_pred
    pass
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
