import pandas as pd
import numpy as np


class NexusAnalyticsEngine:

    def __init__(self, dataframe):

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Input must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot analyze an empty dataset."
            )

        self.dataframe = dataframe.copy(deep=True)

        self.numeric_columns = (
            self.dataframe
            .select_dtypes(include=np.number)
            .columns.tolist()
        )

        self.categorical_columns = (
            self.dataframe
            .select_dtypes(
                include=["object", "category", "bool", "string"]
            )
            .columns.tolist()
        )

    def descriptive_statistics(self):

        return self.dataframe.describe(
            include="all"
        ).T

    def correlation_analysis(self):

        numeric_data = self.dataframe[
            self.numeric_columns
        ]

        if len(self.numeric_columns) < 2:
            return pd.DataFrame()

        return numeric_data.corr()

    def detect_outliers(self):

        results = []

        for column in self.numeric_columns:

            series = self.dataframe[column].dropna()

            if series.empty:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outliers = series[
                (series < lower_bound) |
                (series > upper_bound)
            ]

            results.append({
                "column": column,
                "outlier_count": int(len(outliers)),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_percentage": round(
                    len(outliers) / len(series) * 100, 2
                )
            })

        return pd.DataFrame(results)

    def distribution_analysis(self):

        results = []

        for column in self.numeric_columns:

            series = self.dataframe[column].dropna()

            if series.empty:
                continue

            results.append({
                "column": column,
                "mean": float(series.mean()),
                "median": float(series.median()),
                "standard_deviation": float(
                    series.std()
                ) if len(series) > 1 else 0.0,
                "minimum": float(series.min()),
                "maximum": float(series.max()),
                "skewness": float(series.skew())
                if len(series) > 2 else 0.0
            })

        return pd.DataFrame(results)

    def categorical_analysis(self):

        results = []

        for column in self.categorical_columns:

            series = self.dataframe[column].dropna()

            if series.empty:
                continue

            frequencies = series.value_counts()

            results.append({
                "column": column,
                "unique_categories": int(
                    series.nunique()
                ),
                "most_common_category": str(
                    frequencies.index[0]
                ),
                "most_common_frequency": int(
                    frequencies.iloc[0]
                )
            })

        return pd.DataFrame(results)

    def group_analysis(self, group_column, target_column):

        if group_column not in self.dataframe.columns:
            raise KeyError(
                f"Group column not found: {group_column}"
            )

        if target_column not in self.dataframe.columns:
            raise KeyError(
                f"Target column not found: {target_column}"
            )

        if not pd.api.types.is_numeric_dtype(
            self.dataframe[target_column]
        ):
            raise TypeError(
                "Target column must be numeric."
            )

        return (
            self.dataframe
            .groupby(group_column, dropna=False)[target_column]
            .agg(["count", "mean", "sum", "min", "max"])
            .reset_index()
        )

    def generate_insights(self):

        return {
            "descriptive_statistics":
                self.descriptive_statistics(),

            "correlation":
                self.correlation_analysis(),

            "outliers":
                self.detect_outliers(),

            "distributions":
                self.distribution_analysis(),

            "categorical_analysis":
                self.categorical_analysis()
        }


print("NEXUS ANALYTICS ENGINE CREATED")
