import os
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

# ==========================================
# NEXUS - REPORT GENERATION ENGINE
# ==========================================

class NexusReportEngine:

    def __init__(self, output_directory="nexus_reports"):

        self.output_directory = output_directory

        os.makedirs(
            self.output_directory,
            exist_ok=True
        )

        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "NexusTitle",
            parent=self.styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#123B70"),
            spaceAfter=15
        )

        self.heading_style = ParagraphStyle(
            "NexusHeading",
            parent=self.styles["Heading2"],
            textColor=colors.HexColor("#087EA4"),
            spaceBefore=12,
            spaceAfter=8
        )

        self.body_style = self.styles["BodyText"]

    def _create_table(self, dataframe, max_rows=30):

        if dataframe is None or dataframe.empty:
            return Paragraph(
                "No information available.",
                self.body_style
            )

        display_data = dataframe.head(max_rows).copy()

        data = [
            [str(column) for column in display_data.columns]
        ]

        for row in display_data.itertuples(
            index=False,
            name=None
        ):
            data.append([
                str(value) for value in row
            ])

        table = Table(
            data,
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#123B70")),

            ("TEXTCOLOR", (0, 0), (-1, 0),
             colors.white),

            ("GRID", (0, 0), (-1, -1), 0.5,
             colors.HexColor("#D1D5DB")),

            ("FONTSIZE", (0, 0), (-1, -1), 8),

            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#EFF6FF")]),

            ("TOPPADDING", (0, 0), (-1, -1), 6),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ]))

        return table

    def generate_report(
        self,
        dataframe,
        profile,
        insights,
        filename=None
    ):

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Dataset must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot generate a report from an empty dataset."
            )

        if not isinstance(profile, dict):
            raise TypeError(
                "Profile must be a dictionary."
            )

        if not isinstance(insights, dict):
            raise TypeError(
                "Insights must be a dictionary."
            )

        if filename is None:
            filename = (
                "nexus_report_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".pdf"
            )

        if not isinstance(filename, str):
            raise TypeError(
                "Filename must be a string."
            )

        if not filename.lower().endswith(".pdf"):
            raise ValueError(
                "Report filename must end with .pdf."
            )

        if os.path.basename(filename) != filename:
            raise ValueError(
                "Filename must not contain directory paths."
            )

        if filename in ("", ".", ".."):
            raise ValueError(
                "Invalid report filename."
            )

        output_path = os.path.join(
            self.output_directory,
            filename
        )

        story = []

        # REPORT TITLE
        story.append(
            Paragraph(
                "NEXUS DATA INTELLIGENCE REPORT",
                self.title_style
            )
        )

        story.append(
            Paragraph(
                "Your Data. Your Insights. Your Decisions.",
                self.body_style
            )
        )

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Generated: " + datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                self.body_style
            )
        )

        story.append(Spacer(1, 20))

        # DATASET OVERVIEW
        story.append(
            Paragraph("1. Dataset Overview", self.heading_style)
        )

        overview = pd.DataFrame([
            ["Total Rows", len(dataframe)],
            ["Total Columns", len(dataframe.columns)],
            ["Duplicate Rows", int(dataframe.duplicated().sum())],
            ["Missing Values", int(dataframe.isna().sum().sum())],
            ["Memory Usage (KB)", round(
                dataframe.memory_usage(
                    index=True,
                    deep=True
                ).sum() / 1024, 2
            )]
        ], columns=["Metric", "Value"])

        story.append(self._create_table(overview))
        story.append(Spacer(1, 15))

        # DATA PROFILE
        story.append(
            Paragraph("2. Column Information", self.heading_style)
        )

        story.append(
            self._create_table(
                profile.get("columns", pd.DataFrame())
            )
        )

        story.append(Spacer(1, 15))

        # MISSING VALUES
        story.append(
            Paragraph("3. Missing Value Analysis", self.heading_style)
        )

        story.append(
            self._create_table(
                profile.get("missing_values", pd.DataFrame())
                .reset_index()
            )
        )

        story.append(Spacer(1, 15))

        # NUMERICAL STATISTICS
        story.append(
            Paragraph("4. Numerical Statistics", self.heading_style)
        )

        story.append(
            self._create_table(
                profile.get(
                    "numerical_statistics",
                    pd.DataFrame()
                ).reset_index()
            )
        )

        story.append(Spacer(1, 15))

        # CATEGORICAL STATISTICS
        story.append(
            Paragraph("5. Categorical Statistics", self.heading_style)
        )

        story.append(
            self._create_table(
                profile.get(
                    "categorical_statistics",
                    pd.DataFrame()
                )
            )
        )

        story.append(Spacer(1, 15))

        # ANALYTICS
        story.append(
            Paragraph("6. Analytics Findings", self.heading_style)
        )

        story.append(
            Paragraph("Distribution Analysis", self.styles["Heading3"])
        )

        story.append(
            self._create_table(
                insights.get(
                    "distributions",
                    pd.DataFrame()
                )
            )
        )

        story.append(Spacer(1, 12))

        story.append(
            Paragraph("Outlier Analysis", self.styles["Heading3"])
        )

        story.append(
            self._create_table(
                insights.get(
                    "outliers",
                    pd.DataFrame()
                )
            )
        )

        story.append(Spacer(1, 12))

        story.append(
            Paragraph("Correlation Analysis", self.styles["Heading3"])
        )

        story.append(
            self._create_table(
                insights.get(
                    "correlation",
                    pd.DataFrame()
                ).reset_index()
            )
        )

        # BUILD PDF
        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=45,
            bottomMargin=45
        )

        document.build(story)

        if not os.path.isfile(output_path):
            raise RuntimeError(
                "PDF generation failed."
            )

        if os.path.getsize(output_path) == 0:
            raise RuntimeError(
                "Generated PDF is empty."
            )

        return {
            "status": "success",
            "filename": filename,
            "file_path": output_path,
            "file_size_bytes": os.path.getsize(output_path)
        }


print("NEXUS REPORT GENERATION ENGINE CREATED")
