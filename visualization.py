import pandas as pd
import plotly.express as px


class NexusVisualizationEngine:

    def __init__(self, dataframe):

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Input must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot visualize an empty dataset."
            )

        self.dataframe = dataframe.copy(deep=True)

    def _validate_columns(self, columns):

        for column in columns:

            if column not in self.dataframe.columns:
                raise KeyError(
                    f"Column not found: {column}"
                )

    def bar_chart(self, x, y, color=None):

        self._validate_columns([x, y])

        if color is not None:
            self._validate_columns([color])

        return px.bar(
            self.dataframe,
            x=x,
            y=y,
            color=color,
            title=f"{y} by {x}",
            template="plotly_dark"
        )

    def line_chart(self, x, y, color=None):

        self._validate_columns([x, y])

        if color is not None:
            self._validate_columns([color])

        return px.line(
            self.dataframe,
            x=x,
            y=y,
            color=color,
            title=f"{y} Trend",
            template="plotly_dark"
        )

    def histogram(self, column, bins=20):

        self._validate_columns([column])

        if bins < 1:
            raise ValueError(
                "Number of bins must be positive."
            )

        return px.histogram(
            self.dataframe,
            x=column,
            nbins=bins,
            title=f"Distribution of {column}",
            template="plotly_dark"
        )

    def scatter_plot(self, x, y, color=None):

        self._validate_columns([x, y])

        if color is not None:
            self._validate_columns([color])

        return px.scatter(
            self.dataframe,
            x=x,
            y=y,
            color=color,
            title=f"{y} vs {x}",
            template="plotly_dark"
        )

    def box_plot(self, x, y):

        self._validate_columns([x, y])

        return px.box(
            self.dataframe,
            x=x,
            y=y,
            title=f"{y} by {x}",
            template="plotly_dark"
        )

    def correlation_heatmap(self):

        numeric_data = self.dataframe.select_dtypes(
            include="number"
        )

        if numeric_data.shape[1] < 2:
            raise ValueError(
                "At least two numerical columns are required."
            )

        correlation = numeric_data.corr()

        return px.imshow(
            correlation,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Correlation Heatmap",
            template="plotly_dark"
        )

    def pie_chart(self, column):

        self._validate_columns([column])

        counts = self.dataframe[column].value_counts(
            dropna=False
        ).reset_index()

        counts.columns = [column, "count"]

        return px.pie(
            counts,
            names=column,
            values="count",
            title=f"Distribution of {column}",
            template="plotly_dark"
        )


print("NEXUS VISUALIZATION ENGINE CREATED")
