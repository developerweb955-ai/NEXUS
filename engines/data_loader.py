# ==========================================
# NEXUS - DATA LOADER ENGINE
# VERSION 1.0
# ==========================================

import pandas as pd
import os


class NexusDataLoader:

    SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls"]

    def __init__(self):
        self.dataset = None
        self.filename = None
        self.file_extension = None

    def load(self, file_path):

        # Validate file existence
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        # Extract file extension
        extension = os.path.splitext(file_path)[1].lower()

        # Validate file format
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {extension}"
            )

        # Validate file size
        if os.path.getsize(file_path) == 0:
            raise ValueError("File is empty.")

        try:

            if extension == ".csv":
                dataframe = pd.read_csv(file_path)

            elif extension in [".xlsx", ".xls"]:
                dataframe = pd.read_excel(file_path)

            if dataframe.empty:
                raise ValueError(
                    "Dataset contains no records."
                )

            self.dataset = dataframe
            self.filename = os.path.basename(file_path)
            self.file_extension = extension

            return dataframe

        except (ValueError, UnicodeDecodeError):
            raise

        except Exception as error:
            raise RuntimeError(
                f"Dataset loading failed: {error}"
            ) from error


print("NEXUS DATA LOADER ENGINE CREATED")
