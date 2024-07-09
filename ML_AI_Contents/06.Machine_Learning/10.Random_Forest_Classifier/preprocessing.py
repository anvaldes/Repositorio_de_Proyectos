import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from category_encoders import JamesSteinEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler



def create_preprocessor(features_dict):

    #------------------------------------------------------------------------------------------

    cat_str = features_dict['cat_str']
    cat_oh = features_dict['cat_oh']
    num_mean = features_dict['num_mean']
    num_mean_nan = features_dict['num_mean_nan']
    num_zero_nan = features_dict['num_zero_nan']

    #------------------------------------------------------------------------------------------

    # 1. Categorical String

    cat_str_steps = [
        ('imputer', SimpleImputer(strategy = 'constant', fill_value = 'UNKNOWN')),
        ('encoding', JamesSteinEncoder())
        ]

    cat_str_transformer = Pipeline(steps = cat_str_steps)

    #------------------------------------------------------------------------------------------

    # 2. Categorical Onehot

    cat_oh_steps = [
        ('imputer', SimpleImputer(strategy = 'constant', fill_value = 'UNKNOWN')),
        ('encoding', OneHotEncoder(handle_unknown = 'ignore'))
        ]

    cat_oh_transformer = Pipeline(steps = cat_oh_steps)

    #------------------------------------------------------------------------------------------

    # 3. Numerical Mean

    num_mean_steps = [
        ('imputer', SimpleImputer(strategy = 'mean')),
        ('scale', StandardScaler())
        ]

    num_mean_transformer = Pipeline(steps = num_mean_steps)

    #------------------------------------------------------------------------------------------

    # 4. Numerical Mean NaN

    num_mean_ind_steps = [
        ('imputer', SimpleImputer(strategy = 'mean', add_indicator = True)),
        ('scale', StandardScaler())
        ]

    num_mean_ind_transformer = Pipeline(steps = num_mean_ind_steps)

    #------------------------------------------------------------------------------------------

    # 5. Numerical Zero NaN

    num_zero_ind_steps = [
        ('imputer', SimpleImputer(strategy = 'constant', fill_value = 0, add_indicator = True)),
        ('scale', StandardScaler())
        ]

    num_zero_ind_transformer = Pipeline(steps = num_zero_ind_steps)

    #------------------------------------------------------------------------------------------

    transformers_dict = {
        'cat_str': cat_str_transformer,
        'cat_oh': cat_oh_transformer,
        'num_mean': num_mean_transformer,
        'num_mean_nan': num_mean_ind_transformer,
        'num_zero_nan': num_zero_ind_transformer
        }

    #------------------------------------------------------------------------------------------

    return transformers_dict



def get_fit_transfomers(features_dict, X_train, y_train):

    #------------------------------------------------------------------------------------------

    X_train = X_train.reset_index()
    X_train = X_train.drop(columns = ['index'])

    y_train = y_train.reset_index()
    y_train = y_train.drop(columns = ['index'])

    #------------------------------------------------------------------------------------------

    transformers_dict = create_preprocessor(features_dict)

    types_keys = list(features_dict.keys())

    #------------------------------------------------------------------------------------------

    transformers_fit = {}

    for tk in types_keys:

        if tk == 'cat_str':

            transformers_fit[tk] = transformers_dict[tk].fit(X_train[features_dict[tk]], y_train)

        else:

            transformers_fit[tk] = transformers_dict[tk].fit(X_train[features_dict[tk]])

    #------------------------------------------------------------------------------------------

    return transformers_fit



def transform_datasets(fit_transformers, features_dict, X):

    #------------------------------------------------------------------------------------------

    cat_str = features_dict['cat_str']
    cat_oh = features_dict['cat_oh']
    num_mean = features_dict['num_mean']
    num_mean_nan = features_dict['num_mean_nan']
    num_zero_nan = features_dict['num_zero_nan']

    #------------------------------------------------------------------------------------------

    cat_oh_cols = list(fit_transformers['cat_oh'][1].get_feature_names_out())

    #------------------------------------------------------------------------------------------

    new_cat_oh_cols = []

    for c_oh in cat_oh_cols:

        for i in range(len(cat_oh)):
            
            if c_oh[1] == str(i):

                new_c_oh = cat_oh[i] + c_oh[2:]
                new_cat_oh_cols.append(new_c_oh)

    #------------------------------------------------------------------------------------------

    new_cols = cat_str + new_cat_oh_cols + num_mean + num_mean_nan + [f'indic_{n_m}' for n_m in num_mean_nan] + num_zero_nan + [f'indic_{n_z}' for n_z in num_zero_nan]

    #------------------------------------------------------------------------------------------

    cat_str_transformer = fit_transformers['cat_str']
    cat_oh_transformer = fit_transformers['cat_oh']
    num_mean_transformer = fit_transformers['num_mean']
    num_mean_ind_transformer = fit_transformers['num_mean_nan']
    num_zero_ind_transformer = fit_transformers['num_zero_nan']

    #------------------------------------------------------------------------------------------

    X_new = pd.concat(
        [
            cat_str_transformer.transform(X[cat_str]),
            pd.DataFrame.sparse.from_spmatrix(cat_oh_transformer.transform(X[cat_oh])),
            pd.DataFrame(num_mean_transformer.transform(X[num_mean])),
            pd.DataFrame(num_mean_ind_transformer.transform(X[num_mean_nan])),
            pd.DataFrame(num_zero_ind_transformer.transform(X[num_zero_nan]))
            ],
            axis = 1
            )

    #------------------------------------------------------------------------------------------

    X_new.columns = new_cols

    #------------------------------------------------------------------------------------------
    
    return X_new
