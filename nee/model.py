# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang
"""

"""

import numpy as np

class myKRR():
    def __init__(self, best_models):
        self.models = best_models

    def fit(self, V_train, D_train):
        for i in np.arange(108):
            model = self.models[i]
            model.fit(V_train, D_train.iloc[:, i])

    def predict(self, V_pred):
        D_pred = []
        for i in np.arange(108):
            model = self.models[i]
            D_pred.append(model.predict(V_pred))

        D_pred = np.transpose(D_pred)
        return D_pred


class mySVR():
    def __init__(self, best_models):
        self.models = best_models

    def predict(self, V_pred):
        D_pred_X = []
        D_pred_Y = []
        D_pred_Z = []
        for i in np.arange(36):
            model = self.models[i]
            D_pred_X.append(model.predict(V_pred)[:, 0])
            D_pred_Y.append(model.predict(V_pred)[:, 1])
            D_pred_Z.append(model.predict(V_pred)[:, 2])
        D_pred = np.vstack((D_pred_X, D_pred_Y, D_pred_Z))
        D_pred = np.transpose(D_pred)
        return D_pred