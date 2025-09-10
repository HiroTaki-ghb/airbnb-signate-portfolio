# Airbnb 宿泊価格予測（データコンペ成果物）

本リポジトリは、データ分析学習の一環として **Airbnb 宿泊価格予測コンペティション** に挑戦した成果をまとめたものです。  
（※元はSIGNATE主催のコンペティションですが、2025年9月現在、コンペ自体はすでに公開終了しているため、元データは格納しておりません）

---

## 🎯 プロジェクト概要
- **テーマ**: Airbnb 宿泊価格の予測  
- **順位**: 8位 / 931人  
- **評価指標**: RMSE ≈ 140.8  
- **目的**: 入力された条件をもとに、目安となる宿泊価格を算出すること  

---

## ⚡ 工夫点・苦労点
- 特徴量エンジニアリングに時間をかけ、テキスト項目をCountVectorizerで処理後、価格と紐づけてスコア化
- プログラミング未経験の状態から初めて挑戦した課題だったため、試行錯誤に苦労した

---

## 🚀 デモアプリ
学習したモデルを利用し、ごく簡易的な Web アプリを作成しました。  
以下のリンクから試すことができます。

👉 [Streamlit デモはこちら](https://a8qnerqrkmozae2bv4smwm.streamlit.app/)  

コードは `demo.app/` フォルダをご参照ください。

---

## 🛠 使用技術
- Python (pandas, scikit-learn, LightGBM, Optuna)
- Jupyter Notebook

---

## 📂 リポジトリ構成
├── demo.app/ # デモ用Webアプリのコード
├── airbnb-signate-competition.ipynb # 学習用Jupyter Notebook
├── README.md # 本ファイル
└── .gitignore