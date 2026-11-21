# ==========================================
# NEXUS - DATA INSPECTOR ENGINE
# VERSION 1.0
# ==========================================

import pandas as pd
import numpy as np


class NexusDataInspector:

    def __init__(self, dataframe):

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Input must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot inspect an empty dataset."
            )

        self.dataframe = dataframe.copy()

    # 1. Dataset dimensions
    def get_dimensions(self):

        rows, columns = self.dataframe.shape

        return {
            "rows": rows,
            "columns": columns
        }

    # 2. Column information
    def get_column_information(self):

        information = []

        for column in self.dataframe.columns:

            information.append({
                "column": str(column),
                "data_type": str(
                    self.dataframe[column].dtype
                ),
                "non_null": int(
                    self.dataframe[column].count()
                ),
                "missing": int(
                    self.dataframe[column].isna().sum()
                ),
                "unique_values": int(
                    self.dataframe[column].nunique()
                )
            })

        return pd.DataFrame(information)

    # 3. Missing value analysis
    def get_missing_values(self):

        missing = self.dataframe.isna().sum()

        percentage = (
            missing / len(self.dataframe)
        ) * 100

        return pd.DataFrame({
            "missing_count": missing,
            "missing_percentage": percentage.round(2)
        })

    # 4. Duplicate analysis
    def get_duplicate_information(self):

        duplicates = int(
            self.dataframe.duplicated().sum()
        )

        return {
            "duplicate_rows": duplicates,
            "duplicate_percentage": round(
                duplicates / len(self.dataframe) * 100,
                2
            )
        }

    # 5. Numerical statistics
    def get_numerical_statistics(self):

        numerical_data = self.dataframe.select_dtypes(
            include=np.number
        )

        if numerical_data.empty:
            return pd.DataFrame()

        return numerical_data.describe().T

    # 6. Categorical statistics
    def get_categorical_statistics(self):

        categorical_data = self.dataframe.select_dtypes(
            include=["object", "category", "bool", "string"]
        )

        results = []

        for column in categorical_data.columns:

            results.append({
                "column": column,
                "unique_values": int(
                    categorical_data[column].nunique()
                ),
                "most_frequent": (
                    categorical_data[column].mode().iloc[0]
                    if not categorical_data[column].mode().empty
                    else None
                ),
                "frequency": int(
                    categorical_data[column].value_counts().iloc[0]
                ) if not categorical_data[column].value_counts().empty else 0
            })

        return pd.DataFrame(results)

    # 7. Memory consumption
    def get_memory_usage(self):

        memory = self.dataframe.memory_usage(
            index=True,
            deep=True
        ).sum()

        return {
            "memory_bytes": int(memory),
            "memory_kb": round(memory / 1024, 2),
            "memory_mb": round(memory / (1024 ** 2), 4)
        }

    # 8. Complete dataset profile
    def generate_profile(self):

        return {
            "dimensions": self.get_dimensions(),
            "columns": self.get_column_information(),
            "missing_values": self.get_missing_values(),
            "duplicates": self.get_duplicate_information(),
            "numerical_statistics": self.get_numerical_statistics(),
            "categorical_statistics": self.get_categorical_statistics(),
            "memory_usage": self.get_memory_usage()
        }


print("NEXUS DATA INSPECTOR ENGINE CREATED")
