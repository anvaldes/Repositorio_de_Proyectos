import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler



def create_preprocessor(var_dict):

    #------------------------------------------------------------------------------------------

    cat_oh = var_dict['cat_oh']
    num_mean = var_dict['num_mean']

    #------------------------------------------------------------------------------------------

    # 1. Categorical Onehot

    cat_oh_steps = [
            ('imputer', SimpleImputer(strategy = 'constant', fill_value = 'Developing')),
            ('encoding', OneHotEncoder(handle_unknown = 'ignore'))
            ]

    cat_oh_transformer = Pipeline(steps = cat_oh_steps)

    #------------------------------------------------------------------------------------------

    # 2. Numerical Mean

    num_mean_steps = [
        ('imputer', SimpleImputer(strategy = 'mean')),
        ('scale', StandardScaler())
        ]

    num_mean_transformer = Pipeline(steps = num_mean_steps)

    #------------------------------------------------------------------------------------------

    transformers_dict = {
        'cat_oh': cat_oh_transformer,
        'num_mean': num_mean_transformer
        }
    
    return transformers_dict



def get_fit_transformers(var_dict, X_train):

    #------------------------------------------------------------------------------------------

    X_train = X_train.reset_index()
    X_train = X_train.drop(columns = ['index'])

    #------------------------------------------------------------------------------------------

    transformers_dict = create_preprocessor(var_dict)

    #------------------------------------------------------------------------------------------

    types_keys = list(var_dict.keys())

    #------------------------------------------------------------------------------------------

    transformers_fit = {}

    for tk in types_keys:

        transformers_fit[tk] = transformers_dict[tk].fit(X_train[var_dict[tk]])

    #------------------------------------------------------------------------------------------

    return transformers_dict



def transform_datasets(transformers_fit, var_dict, X):

    #------------------------------------------------------------------------------------------

    num_mean = var_dict['num_mean']
    cat_oh = var_dict['cat_oh']

    #------------------------------------------------------------------------------------------

    cat_oh_cols = list(transformers_fit['cat_oh'][1].get_feature_names_out())

    #------------------------------------------------------------------------------------------

    new_cat_oh_cols = []

    for c_oh in cat_oh_cols:

        for i in range(len(cat_oh)):
                
            if c_oh[1] == str(i):

                new_c_oh = cat_oh[i] + c_oh[2:]
                new_cat_oh_cols.append(new_c_oh)
    
    #------------------------------------------------------------------------------------------

    new_cols = new_cat_oh_cols + num_mean

    #------------------------------------------------------------------------------------------

    cat_oh_transformer = transformers_fit['cat_oh']
    num_mean_transformer = transformers_fit['num_mean']

    #------------------------------------------------------------------------------------------

    X_new = pd.concat(
        [
            pd.DataFrame.sparse.from_spmatrix(cat_oh_transformer.transform(X[cat_oh])),
            pd.DataFrame(num_mean_transformer.transform(X[num_mean]))
            ],
            axis = 1
            )
    
    #------------------------------------------------------------------------------------------

    X_new.columns = new_cols

    #------------------------------------------------------------------------------------------

    X_new = X_new.drop(columns = ['Status_Developing'])

    #------------------------------------------------------------------------------------------

    return X_new