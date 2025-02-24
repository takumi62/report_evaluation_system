# Report Evaluation System
### 概要
本システムは、PDF形式のレポートをAI（GPT-4）を活用して自動評価するシステムです。指定された評価基準に基づき、レポートをスコアリングし、最終的なグレード（A～F）を算出します。結果はCSVファイルとして出力され、詳細な評価内容も含まれます。

### 特徴
PDFの自動テキスト抽出：レポートをPDFから直接読み込み、テキストを解析します。
AI評価：GPT-4を利用して、複数の評価基準に基づいてスコアリングを実施します。
詳細な結果出力：評価スコア、グレード、詳細な判定結果をCSV形式で保存します。
柔軟な環境設定：.envファイルを用いた環境変数管理で簡単に設定を変更可能。

### システム構成

```
report_evaluation_system/
├── app/
│   ├── config.py                # 環境変数と設定を管理
│   ├── evaluation.py            # GPTによる評価ロジック
│   ├── main.py                  # メインスクリプト
│   ├── pdf_processing.py        # PDFテキスト抽出ロジック
├── data/
│   ├── evaluation_criteria.yaml # 評価基準を定義したYAMLファイル
│   ├── sample_report.pdf        # テスト用のPDFファイル
├── output/                      # 評価結果の出力ディレクトリ
├── .env                         # 環境変数ファイル
├── requirements.txt             # 必要なPythonパッケージ
├── Dockerfile                   # Dockerビルド設定
└── README.md                    # 本ファイル
```

### セットアップ手順
1. 必要条件
Python 3.11以上
Docker（任意で使用）
2. 環境変数の設定
.envファイルを作成し、以下の内容を記載してください：

```
OPENAI_API_KEY=your_openai_api_key
MODEL=gpt-4o
PDF_FOLDER=data/
EVALUATION_CRITERIA_PATH=data/evaluation_criteria.yaml
OUTPUT_PATH=output/evaluation_results.csv
```

3. 必要パッケージのインストール
ローカル環境で実行する場合：

```
pip install -r requirements.txt
```

Dockerを使用する場合：

```
docker build -t report-evaluation-system .
```

### 使用方法
1. ローカル環境で実行
以下のコマンドを使用してスクリプトを実行します：

```
python app/main.py
```

2. Dockerを使用して実行
以下のコマンドを使用してDockerコンテナを実行します：

```
docker run --rm -it --env-file .env -v $(pwd)/output:/workdir/output report-evaluation-system
```

### 結果
評価結果はoutput/evaluation_results.csvに保存されます。

### 評価基準の編集
評価基準はdata/evaluation_criteria.yamlで管理されています。評価項目や加点・減点の内容を編集することで、カスタマイズが可能です。

### YAML形式の例

```
criteria:
  - name: "文量が2ページ以上3ページ以内に収まっていない"
    points: -3
  - name: "フォントが10-11Point"
    points: -1
  - name: "余白が標準かやや狭い"
    points: -1
  - name: "本文が適切に書かれており、分量が3枚目に到達している"
    points: 5
```

### 出力結果
結果はCSV形式で保存されます。以下は出力結果の例です：

```
filename,total_score,grade,details
filename.pdf,total_score,grade,"[{'criterion': '文量が2ページ以上3ページ以内に収まっていない', 'points': 0, 'result': '非該当'}, ...]"
```

filename: 対象PDFファイルの名前
total_score: 最終スコア
grade: A～Fの評価
details: 各評価基準の詳細結果（JSON形式）

### 注意事項
必ずOPENAI_API_KEYを環境変数に設定してください。
入力PDFファイルはdata/ディレクトリに配置してください。
評価基準の設定やスコア計算ロジックを変更する場合は、evaluation.pyを編集してください。
NLPが評価しやすい言葉を用いて評価項目を作成してください。