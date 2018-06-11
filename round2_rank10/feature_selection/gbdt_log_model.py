from odps import ODPS
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from odps.df import DataFrame
from sklearn.model_selection import KFold
import time
import numpy as np


def eval_metric(pred, labels):
	return np.mean(np.power(np.log(pred + 1) - np.log(labels + 1), 2))

def gbdt_model(df, label, use_feature, true_test, submission_data, gbdt_model):
    print("基于GBDT： 开始训练 label 为{}...".format(label))
    value4preds = np.log(df[label])
    train_data = df.loc[:, use_feature]
    print(train_data.shape)
    scores = np.zeros(len(value4preds))
    submission_scores = np.zeros((len(submission_data), 5))
    kf = KFold(n_splits=5, shuffle=True, random_state=1024)
    five_fold_index = list(kf.split(train_data, value4preds))
    
    train_index_1, test_index_1 = five_fold_index[0]
    print('第1次训练...')
    x_train_1, x_test_1 = train_data.iloc[train_index_1], train_data.iloc[test_index_1]
    y_train_1, y_test_1 = value4preds.iloc[train_index_1], value4preds.iloc[test_index_1]
    gbdt_model.fit(x_train_1, y_train_1)
    scores[test_index_1] = np.exp(gbdt_model.predict(x_test_1))
    submission_scores[:, 0] = gbdt_model.predict(true_test)
    print('the score is: ', eval_metric(scores[test_index_1], np.exp(y_test_1)))
    print('第1次训练结束')
    print('*******************************************************************')
    train_index_2, test_index_2 = five_fold_index[1]
    print('第2次训练...')
    x_train_2, x_test_2 = train_data.iloc[train_index_2], train_data.iloc[test_index_2]
    y_train_2, y_test_2 = value4preds.iloc[train_index_2], value4preds.iloc[test_index_2]
    gbdt_model.fit(x_train_2, y_train_2)
    scores[test_index_2] = np.exp(gbdt_model.predict(x_test_2))
    submission_scores[:, 1] = gbdt_model.predict(true_test)
    print('the score is: ', eval_metric(scores[test_index_2], np.exp(y_test_2)))
    print('第2次训练结束')
    print('*******************************************************************')
    train_index_3, test_index_3 = five_fold_index[2]
    print('第3次训练...')
    x_train_3, x_test_3 = train_data.iloc[train_index_3], train_data.iloc[test_index_3]
    y_train_3, y_test_3 = value4preds.iloc[train_index_3], value4preds.iloc[test_index_3]
    gbdt_model.fit(x_train_3, y_train_3)
    scores[test_index_3] = np.exp(gbdt_model.predict(x_test_3))
    submission_scores[:, 2] = gbdt_model.predict(true_test)
    print('the score is: ', eval_metric(scores[test_index_3], np.exp(y_test_3)))
    print('第3次训练结束')
    print('*******************************************************************')
    train_index_4, test_index_4 = five_fold_index[3]
    print('第4次训练...')
    x_train_4, x_test_4 = train_data.iloc[train_index_4], train_data.iloc[test_index_4]
    y_train_4, y_test_4 = value4preds.iloc[train_index_4], value4preds.iloc[test_index_4]
    gbdt_model.fit(x_train_4, y_train_4)
    scores[test_index_4] = np.exp(gbdt_model.predict(x_test_4))
    submission_scores[:, 3] = gbdt_model.predict(true_test)
    print('the score is: ', eval_metric(scores[test_index_4], np.exp(y_test_4)))
    print('第4次训练结束')
    print('*******************************************************************')
    train_index_5, test_index_5 = five_fold_index[4]
    print('第5次训练...')
    x_train_5, x_test_5 = train_data.iloc[train_index_5], train_data.iloc[test_index_5]
    y_train_5, y_test_5 = value4preds.iloc[train_index_5], value4preds.iloc[test_index_5]
    gbdt_model.fit(x_train_5, y_train_5)
    scores[test_index_5] = np.exp(gbdt_model.predict(x_test_5))
    submission_scores[:, 4] = gbdt_model.predict(true_test)
    print('the score is: ', eval_metric(scores[test_index_5], np.exp(y_test_5)))
    print('第5次训练结束')
    print('*******************************************************************')
    submission_data[label] = np.exp(np.mean(submission_scores, axis=1)).round(3)
    return eval_metric(scores, np.exp(value4preds))


# snp one-hot:14  'sys': 0.013770852754101864  juz_train_6_6_add_wzm_for145_final2 sys_juz_train_6_6_snp_onehot_22
# snp one-hot:10  'dia': 0.01811632794174798   juz_train_6_6_add_wzm_for145_final2 dia_juz_train_6_6_snp_onehot_22
# snp one-hot:14  'tl':  0.088753086260020458  juz_train_6_6_add_wzm_onlytl_final  tl_juz_train_6_6_snp_onehot_22
# snp one-hot:10  'hdl': 0.011026393729362835  juz_train_6_6_add_wzm_for145_final  ldl_juz_train_6_6_snp_onehot_22
# snp one-hot:1   'ldl': 0.033357708093281487  juz_train_6_6_add_wzm_for145_final  hdl_juz_train_6_6_snp_onehot_22
if __name__ == "__main__":
    use_label = 'dia'
    train = odps.get_table('{}_juz_train_6_6_snp_onehot_22'.format(use_label)).to_df().to_pandas()
    test = odps.get_table('{}_juz_test_6_6_snp_onehot_22'.format(use_label)).to_df().to_pandas()

    print(train.shape)
    print(test.shape)
    predict_features = ['sys', 'dia', 'tl', 'hdl', 'ldl']
    use_features = [t for t in train.columns if t != 'vid' and t not in predict_features]
    test_data = test.loc[:, use_features]
    
    submission = test.loc[:, ['vid', use_label]]
    base_line_score = np.zeros(5)
    start = time.time()
    model =  GradientBoostingRegressor(learning_rate=0.01, n_estimators=800, max_depth=5, subsample=0.7,
                                               random_state=1, verbose=0, min_samples_leaf=50)
    for i, j in enumerate(predict_features):
        if j in [use_label]:
            base_line_score[i] = gbdt_model(train, j, use_features, test_data, submission, model)
    print(dict(zip(predict_features, base_line_score)))
    print('CV训练用时{}秒'.format(time.time() - start))
    print('scores:', np.mean(base_line_score))