# importing required libraries
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from joblib import dump


def MeanAbsoluteError(Y_test, y_test):
    n = len(Y_test)
    num = 0
    for i in range(n):
        num += abs(y_test[i] - Y_test[i])

    return num / n


class CustomEncoder(BaseEstimator):
    def __init__(self):
        pass

    def fit(self, documents, y=None):
        return self

    def transform(self, x_dataset):
        # nb_of_runs
        x_dataset["Unpopular"] = x_dataset["nb_of_runs"].apply(
            lambda x: 1 if x <= 3 else 0
        )
        x_dataset["Somehow_Popular"] = x_dataset["nb_of_runs"].apply(
            lambda x: 1 if x > 3 and x <= 7 else 0
        )
        x_dataset["Popular"] = x_dataset["nb_of_runs"].apply(
            lambda x: 1 if x > 7 and x <= 19 else 0
        )
        x_dataset["Very_Popular"] = x_dataset["nb_of_runs"].apply(
            lambda x: 1 if x > 19 else 0
        )

        # age
        x_dataset["Young"] = x_dataset["age"].apply(lambda x: 1 if x <= 21 else 0)
        x_dataset["Somehow_Old"] = x_dataset["age"].apply(
            lambda x: 1 if x > 21 and x <= 28 else 0
        )
        x_dataset["Old"] = x_dataset["age"].apply(
            lambda x: 1 if x > 28 and x <= 31 else 0
        )
        x_dataset["Very_Old"] = x_dataset["age"].apply(lambda x: 1 if x > 31 else 0)

        # coding time to a categorical variable
        x_dataset["Short"] = x_dataset["time"].apply(lambda x: 1 if x <= 664.833 else 0)
        x_dataset["Somehow_Long"] = x_dataset["time"].apply(
            lambda x: 1 if x > 664.833 and x <= 1226 else 0
        )
        x_dataset["Long"] = x_dataset["time"].apply(
            lambda x: 1 if x > 1226 and x <= 2315 else 0
        )
        x_dataset["Very_Long"] = x_dataset["time"].apply(lambda x: 1 if x > 2315 else 0)

        return x_dataset


pre_process = ColumnTransformer(
    remainder="passthrough",
    transformers=[("drop_columns", "drop", ["age", "nb_of_runs"])],
)


data = pd.read_csv("data/f_dataset.csv")
try:
    data.drop("Unnamed: 0", axis=1, inplace=True)
except Exception:
    pass

features = ["time", "age", "nb_of_runs"]
label = "TAS_time"

X = data[features]
y = data[label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
X_train.reset_index(inplace=True, drop=True)
X_test.reset_index(inplace=True, drop=True)
y_train.reset_index(inplace=True, drop=True)
y_test.reset_index(inplace=True, drop=True)


model_pipeline = Pipeline(
    steps=[
        ("coding_known_variables", CustomEncoder()),
        ("pre_processing", pre_process),
        (
            "XGBoost_regressor",
            GradientBoostingRegressor(
                random_state=0,
                learning_rate=0.051,
                max_depth=4,
                criterion="friedman_mse",
                loss="absolute_error",
                n_estimators=100,
            ),
        ),
    ]
)

print("Fitting the pipeline with the training data")
model_pipeline.fit(X_train, y_train)

print(X_train)

# predict target values on the training data
print("\n\nPredict target on the train data\n\n")
print(model_pipeline.predict(X_train))

print("\n\nPredict target on the test data\n\n")
print(model_pipeline.predict(X_test))

print("\n\nScore on test set (MAE) : \n\n")
print(MeanAbsoluteError(y_test, model_pipeline.predict(X_test)))


dump(model_pipeline, filename="src/time_prediction.joblib")
