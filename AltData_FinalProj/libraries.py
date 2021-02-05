import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
from adtk.detector import QuantileAD
from adtk.detector import GeneralizedESDTestAD
from adtk.detector import AutoregressionAD


class Imputer:
    original_df = pd.DataFrame()

    def __init__(self, _original: pd.DataFrame):
        self.original_df = _original.copy(deep=True)

    def set_original_df(self, _df):
        """
        Set a dataframe to be imputed.
        """
        self.original_df = _df

    def SimpleImputer(self):
        # univariate, which imputes values in the i-th feature dimension using only non-missing values in that feature dimension

        df1 = self.original_df.copy(deep=True)
        imp1 = SimpleImputer(missing_values=np.nan, strategy='mean')
        result_1 = imp1.fit_transform(df1.T)
        result_1 = pd.DataFrame(result_1.T, columns=df1.columns, index=df1.index)
        return result_1

    def IterativeImputer(self):
        df2 = self.original_df.copy(deep=True)
        imp2 = IterativeImputer(max_iter=10, random_state=0)
        result_2 = imp2.fit_transform(df2)
        result_2 = pd.DataFrame(result_2, columns=df2.columns, index=df2.index)
        return result_2

    def KnnImputer(self):
        df3 = self.original_df.copy(deep=True)
        imp3 = KNNImputer(n_neighbors=2, weights="uniform")
        result_3 = imp3.fit_transform(df3)
        result_3 = pd.DataFrame(result_3, columns=df3.columns, index=df3.index)
        return result_3


def deleter(data_imputed, delete_perct, missing_n, block_n) -> pd.DataFrame:
    """
    Randomly delete data for cross validation. The deletion is NOT in-\place.

    :param data_imputed: the original dataframe where the imputation has finished
    :param delete_perct: the percentage of deleted data. Eg, when delete_p = 0.1, we delete 10% of all data
    :return: a new dataframe where deleted data is substituted by np.nan
    """
    data_deleting = data_imputed.copy(deep=True)
    non_missing_n = int(data_deleting.shape[0] * data_deleting.shape[1])
    # chunk size is 2, thus at each time we delete a pair
    deleting_pairs = int(non_missing_n * delete_perct / round(missing_n / block_n))

    for j in range(deleting_pairs):

        store_idx = np.random.randint(0, high=len(data_imputed))
        month_idx = np.random.randint(0, high=24)
        if month_idx == 23:
            # If the last month is selected, there is no month backward
            # so for the last month, we select the forward month only
            month_idx_2 = 22
        elif month_idx == 0:
            # If the first month is selected, there is no month forward,
            # so for the first month, we select the backward month only
            month_idx_2 = 1
        else:
            # for the months in the middle, we randomly choose its backward month or forward month to delete together.
            month_idx_2 = month_idx + np.random.choice([-1, 1])

        # Locate the data we want to delete
        store_ts = data_deleting.iloc[store_idx]
        month_del = [data_deleting.columns.values[month_idx]]
        month_del.append(data_deleting.columns.values[month_idx_2])
        # Replace the deleted data with np.nan
        store_ts[month_del] = [np.NaN, np.NaN]
        data_deleting.iloc[store_idx] = store_ts
    return data_deleting


def outlier_detector(ori_data: pd.DataFrame):
    """
    Detect outliers using three packages mentioned above.

    :param ori_data: data
    :return: new dataframe with outliers
    """

    detector1 = QuantileAD(low=0.02, high=0.98)
    res1 = detector1.fit_detect(ori_data.T).T
    res1 = res1.replace(to_replace=1, value='True')
    res1 = res1.replace(to_replace=0, value='False')
    res1.head()

    detector2 = GeneralizedESDTestAD(alpha=0.05)
    res2 = detector2.fit_detect(ori_data.T).T
    res2 = res2.replace(to_replace=1, value='True')
    res2 = res2.replace(to_replace=0, value='False')

    detector3 = AutoregressionAD(c=1.0)
    pivot_m = ori_data.T.resample('m').first()
    res3 = detector3.fit_detect(pivot_m).T
    res3 = res3.replace(to_replace=1, value='True')
    res3 = res3.replace(to_replace=0, value='False')
    res3.columns = res1.columns

    def numeralized(val):
        num = 0 if val == 'False' else 1
        return num

    res1_prep = res1.applymap(numeralized)
    res2_prep = res2.applymap(numeralized)
    res3_prep = res3.applymap(numeralized)
    res_agg = res1_prep.add(res2_prep).add(res3_prep)
    res_agg.head()

    cleaned_df = ori_data.where(res_agg < 2, np.NaN)
    return cleaned_df


def MAPE(y_df: pd.DataFrame, y_hat_df: pd.DataFrame) -> float:
    """
    :param y_df: actual test data
    :param y_hat_df: predicted values
    :return: the MAPE of actual data and predicted data
    """
    pct_df =  np.abs(y_df - y_hat_df)/ np.abs(y_df)
    MAPE = pct_df.stack().mean()
    return MAPE


def cal_chunk_size(data_cleaned:pd.DataFrame):
    df5 = data_cleaned.copy(deep=True)
    temp = df5.fillna('missing')
    all_cnt = []

    # In the for loop below, we calculate the chunk size
    for store, ts in zip(temp.index.values, temp.values):
        missing_count = ts.tolist().count('missing')
        cnts = []
        start = 0
        while start in range(len(ts)):
            if ts[start] == 'missing':
                count = 1
                # If a missing value is detected, we keep checking if the next value is still missing.
                # count is the number of missing values in the missing block.
                while start + 1 < 24 and ts[start + 1] == 'missing':
                    count += 1
                    start += 1
                cnts.append(count)
                start += 1
            else:
                start += 1
        all_cnt.append(cnts)

    block_n = 0
    for ele in all_cnt:
        block_n += len(ele)
    print(f"Total numbers of missing chunks is {block_n}.")

    missing_n = temp.values.flatten().tolist().count('missing')
    print(f"Total numbers of missing values is {missing_n}.")
    print(f'Average length of missing chunks is {round(missing_n / block_n)}.')

    non_missing_n = data_cleaned.count(1).sum()
    deleting_level = 0.1
    print()
    print(f'To delete extra 10% data, which is {int(non_missing_n * deleting_level)} data points, \n therefore we need to randomly delete {int(non_missing_n * deleting_level / round(missing_n / block_n))} blocks.')
    return missing_n,block_n

def cross_validator_Q7(imputer:Imputer,impute_method,original_data,cv_times,
                    miss_n,b_n):
    """
    :param imputer: an instance of Imputer
    :param impute_method: input a function, imputor. This function will be tested.
    :param original_data: data
    :param cv_times: repeat many times and calcualte average MAPE
    :return: average MAPE for the imputor
    """
    error = np.zeros(cv_times)
    for i in range(cv_times):
        # randomly delete data
        deleted_df = deleter(original_data,0.1,miss_n,b_n)
        imputer.set_original_df(deleted_df.copy(deep=True))
        imputed_data = impute_method() # impute data
        error[i] = MAPE(original_data,imputed_data)
    return error