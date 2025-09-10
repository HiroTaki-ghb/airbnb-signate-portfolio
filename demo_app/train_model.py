import os
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir("."))


# train_model.py
import pandas as pd
import pickle
import lightgbm as lgb
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from preprocess import AirbnbPreprocessor

# --- 学習データの読み込み ---
df = pd.read_csv("train.csv", index_col=0)

# --- スコアリング用辞書を作成 ---
amenity_scores_df = pd.read_csv("amenity_score.csv")
word_scores_df = pd.read_csv("wordlist.csv")

amenity_scores_dict = pd.Series(
    amenity_scores_df.score.values, index=amenity_scores_df.amenity
).to_dict()

word_scores_dict = pd.Series(
    word_scores_df.score.values, index=word_scores_df.word
).to_dict()

# --- 特徴量と目的変数 ---
X = df.drop(columns=["y"])
y = df["y"]

# --- パイプライン定義 ---
pipe = Pipeline([
    ("preprocess", AirbnbPreprocessor(amenity_scores_dict, word_scores_dict)),
    ("model", lgb.LGBMRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=-1,
        random_state=42
    ))
])

# --- 学習 ---
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, random_state=42
)
pipe.fit(X_train, y_train)

# --- 検証スコア ---
score = pipe.score(X_valid, y_valid)
print(f"Validation R^2: {score:.4f}")

# --- pickle保存 ---
with open("model.pkl", "wb") as f:
    pickle.dump(pipe, f)

print("✅ model.pkl saved! (amenity/wordlist 辞書も埋め込み済み)")
