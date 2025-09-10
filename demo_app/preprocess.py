# preprocess.py
import pandas as pd
import numpy as np
import re
from sklearn.base import BaseEstimator, TransformerMixin


class AirbnbPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, amenity_scores_dict, word_scores_dict):
        self.amenity_scores_dict = amenity_scores_dict
        self.word_scores_dict = word_scores_dict
        self.encoding_maps = {}
        self.categorical_cols = None

    def data_pre(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # --- 欠損値処理 (bathrooms, bedrooms, beds) ---
        for column in ["bathrooms", "bedrooms", "beds"]:
            if df[column].isnull().sum() > 0:
                medians = df.groupby("accommodates")[column].median()
                df[column] = df.apply(
                    lambda row: medians[row["accommodates"]] if pd.isnull(row[column]) else row[column],
                    axis=1
                )

        # --- 欠損値処理 (review_scores_rating, host_identity_verified) ---
        df["review_scores_rating"] = df["review_scores_rating"].fillna(df["review_scores_rating"].median())
        df["host_identity_verified"] = df["host_identity_verified"].fillna("f")
        df["host_has_profile_pic"] = df["host_has_profile_pic"].fillna("f")

        # host_response_rate列を数値変換＋欠損値処理
        if "host_response_rate" not in df.columns:
            df["host_response_rate"] = np.nan

        df["host_response_rate"] = (
            df["host_response_rate"]
            .replace("None", np.nan)        # 文字列 "None" を np.nan に置換
            .replace("nan", np.nan)         # 文字列 "nan" も np.nan に置換
            .astype(str)
            .str.rstrip("%")
        )

        df["host_response_rate"] = pd.to_numeric(df["host_response_rate"], errors="coerce")
        df["host_response_rate"] = df["host_response_rate"].fillna(df["host_response_rate"].median())

        # --- サムネイル有無をフラグ化 ---
        df["thumbnail_url"] = df["thumbnail_url"].notna().astype(int)

        # --- 日付処理 ---
        df["host_since"] = pd.to_datetime(df["host_since"])
        df["host_since"] = df["host_since"].fillna(df["host_since"].median())
        df["first_review"] = pd.to_datetime(df["first_review"]).fillna(df["host_since"])
        df["last_review"] = pd.to_datetime(df["last_review"]).fillna(df["host_since"])

        df["host_days_since"] = (pd.Timestamp("2017-10-05") - df["host_since"]).dt.days
        df["first_review"] = df["first_review"].astype("int64") // 10**9
        df["last_review"] = df["last_review"].astype("int64") // 10**9

        # --- アメニティスコア ---
        df["cleaned_amenities"] = df["amenities"].str.replace('"', "", regex=False)

        def calculate_amenity_score(cleaned_amenities):
            total_score = 0
            keys = re.findall(r"\{(.*)\}", str(cleaned_amenities))
            if keys:
                for key in keys[0].split(","):
                    key = key.strip()
                    total_score += self.amenity_scores_dict.get(key, 0)
            return total_score

        df["amenity_scores"] = df["cleaned_amenities"].apply(calculate_amenity_score)

        # --- name/description スコア ---
        def calculate_score(text):
            if not isinstance(text, str):
                return 0
            return sum(self.word_scores_dict.get(word.strip().lower(), 0) for word in text.split())

        df["name_scores"] = df["name"].apply(calculate_score)
        df["description_scores"] = df["description"].apply(calculate_score)

        # --- 不要列削除 ---
        drop_list = [
            "amenities", "city", "description", "neighbourhood",
            "name", "cleaned_amenities", "host_since", "zipcode"
        ]
        df = df.drop([c for c in drop_list if c in df.columns], axis=1)

        # --- object → category ---
        object_cols = df.select_dtypes(include="object").columns
        df[object_cols] = df[object_cols].astype("category")

        return df

    def fit(self, X, y=None):
        df = self.data_pre(X.copy())

        # カテゴリ列を取得
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns

        # ターゲットエンコーディングの平均値を計算
        global_mean = y.mean()
        encoding_maps = {}
        tmp = df.copy()
        tmp["_target"] = y

        for col in self.categorical_cols:
            mean_map = tmp.groupby(col)["_target"].mean().to_dict()
            mean_map["Other"] = global_mean
            encoding_maps[col] = mean_map

        self.encoding_maps = encoding_maps
        return self

    def transform(self, X):
        df = self.data_pre(X.copy())

    def transform(self, X):
        df = self.data_pre(X.copy())

        # 保存済みのエンコーディングを適用
        for col in self.categorical_cols:
            mean_map = self.encoding_maps[col]
            df[col] = np.where(df[col].isin(mean_map), df[col], "Other")
            df[f"{col}_encoded"] = df[col].map(mean_map).astype(float)

        # 元のカテゴリ列は削除
        df.drop(columns=self.categorical_cols, inplace=True, errors="ignore")

        # object型のカラムをcategory型に変換
        # ただし本来は数値の列を除外
        object_cols = df.select_dtypes(include="object").columns
        exclude_cols = ["latitude", "longitude", "number_of_reviews"]
        cat_cols = [col for col in object_cols if col not in exclude_cols]

        if len(cat_cols) > 0:
            df[cat_cols] = df[cat_cols].astype("category")

        return df
