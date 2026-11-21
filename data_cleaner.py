# ==========================================
# NEXUS - DATA CLEANER ENGINE
# VERSION 1.0
# ==========================================

import pandas as pd
import numpy as np


class NexusDataCleaner:

    def __init__(self, dataframe):

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Input must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot clean an empty dataset."
            )

        # Preserve original and working copies
        self.original_data = dataframe.copy(deep=True)
        self.dataframe = dataframe.copy(deep=True)

        # Record cleaning operations
        self.cleaning_history = []

    def _validate_columns(self, columns):

        if columns is None:
            return list(self.dataframe.columns)

        if isinstance(columns, str):
            columns = [columns]

        missing = [
            col for col in columns
            if col not in self.dataframe.columns
        ]

        if missing:
            raise KeyError(
                f"Columns not found: {missing}"
            )

        return list(columns)

    # 1. Remove duplicate records
    def remove_duplicates(self, subset=None, keep="first"):

        if keep not in ["first", "last", False]:
            raise ValueError("Invalid duplicate retention option.")

        before = len(self.dataframe)

        self.dataframe = self.dataframe.drop_duplicates(
            subset=subset,
            keep=keep
        ).reset_index(drop=True)

        removed = before - len(self.dataframe)

        self.cleaning_history.append({
            "operation": "remove_duplicates",
            "rows_removed": int(removed)
        })

        return self.dataframe

    # 2. Handle missing values
    def handle_missing_values(
        self,
        strategy="drop",
        columns=None,
        fill_value=None
    ):

        valid_strategies = [
            "drop", "mean", "median", "mode", "constant"
        ]

        if strategy not in valid_strategies:
            raise ValueError("Unsupported missing value strategy.")

        selected = self._validate_columns(columns)

        before = int(
            self.dataframe[selected].isna().sum().sum()
        )

        if strategy == "drop":

            self.dataframe = self.dataframe.dropna(
                subset=selected
            )

        elif strategy in ["mean", "median"]:

            for column in selected:

                if not pd.api.types.is_numeric_dtype(
                    self.dataframe[column]
                ):
                    raise TypeError(
                        f"{column} must be numeric for {strategy}."
                    )

                if self.dataframe[column].notna().any():

                    value = getattr(
                        self.dataframe[column], strategy
                    )()

                    self.dataframe[column] = (
                        self.dataframe[column].fillna(value)
                    )

        elif strategy == "mode":

            for column in selected:

                modes = self.dataframe[column].mode(
                    dropna=True
                )

                if not modes.empty:
                    self.dataframe[column] = (
                        self.dataframe[column].fillna(
                            modes.iloc[0]
                        )
                    )

        elif strategy == "constant":

            if fill_value is None:
                raise ValueError(
                    "A fill_value is required for constant strategy."
                )

            for column in selected:

                self.dataframe[column] = (
                    self.dataframe[column].fillna(fill_value)
                )

        after = int(
            self.dataframe[selected].isna().sum().sum()
        )

        self.cleaning_history.append({
            "operation": "handle_missing_values",
            "strategy": strategy,
            "columns": selected,
            "missing_values_before": before,
            "missing_values_after": after
        })

        return self.dataframe

    # 3. Convert column data types
    def convert_data_types(self, conversions, errors="raise"):

        if errors not in ["raise", "coerce"]:
            raise ValueError(
                "Errors must be 'raise' or 'coerce'."
            )

        allowed_types = [
            "int", "float", "string",
            "category", "datetime"
        ]

        for column, target_type in conversions.items():

            self._validate_columns([column])

            if target_type not in allowed_types:
                raise ValueError(
                    f"Unsupported data type: {target_type}"
                )

            if target_type == "int":

                numeric = pd.to_numeric(
                    self.dataframe[column],
                    errors=errors
                )

                if (
                    errors == "raise"
                    and numeric.notna().any()
                    and not numeric.dropna().mod(1).eq(0).all()
                ):
                    raise ValueError(
                        f"{column} contains non-integer values."
                    )

                self.dataframe[column] = numeric.astype("Int64")

            elif target_type == "float":

                self.dataframe[column] = pd.to_numeric(
                    self.dataframe[column],
                    errors=errors
                ).astype("float64")

            elif target_type == "string":

                self.dataframe[column] = (
                    self.dataframe[column].astype("string")
                )

            elif target_type == "category":

                self.dataframe[column] = (
                    self.dataframe[column].astype("category")
                )

            elif target_type == "datetime":

                self.dataframe[column] = pd.to_datetime(
                    self.dataframe[column],
                    errors=errors
                )

            self.cleaning_history.append({
                "operation": "convert_data_type",
                "column": column,
                "target_type": target_type,
                "errors": errors
            })

        return self.dataframe

    # 4. Remove unnecessary whitespace
    def trim_whitespace(self, columns=None):

        selected = self._validate_columns(columns)

        cleaned = []

        for column in selected:

            if (
                pd.api.types.is_object_dtype(
                    self.dataframe[column]
                )
                or isinstance(
                    self.dataframe[column].dtype,
                    pd.StringDtype
                )
            ):

                self.dataframe[column] = (
                    self.dataframe[column].str.strip()
                )

                cleaned.append(column)

        self.cleaning_history.append({
            "operation": "trim_whitespace",
            "columns": cleaned
        })

        return self.dataframe

    # 5. Generate cleaning report
    def get_cleaning_report(self):

        return {
            "original_rows": int(len(self.original_data)),
            "current_rows": int(len(self.dataframe)),
            "rows_removed": int(
                len(self.original_data) - len(self.dataframe)
            ),
            "original_missing_values": int(
                self.original_data.isna().sum().sum()
            ),
            "current_missing_values": int(
                self.dataframe.isna().sum().sum()
            ),
            "operations_performed": len(
                self.cleaning_history
            ),
            "cleaning_history": self.cleaning_history.copy()
        }

    # 6. Export cleaned dataset
    def get_cleaned_data(self):

        return self.dataframe.copy(deep=True)


print("NEXUS DATA CLEANER ENGINE CREATED")
