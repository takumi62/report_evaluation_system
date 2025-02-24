import os
from config import Config
import yaml
from pdf_processing import extract_text_from_pdf
from evaluation import evaluate_with_langchain, generate_evaluation_prompt, parse_gpt_response, grade_score
import json

from langchain_openai import ChatOpenAI

# 並列処理用の関数の実装
# ThreadPoolExecutor(max_workers=5) で同時処理数を制限

from concurrent.futures import ThreadPoolExecutor

def process_single_pdf(pdf_path, criteria, report_context, langchain_client):
    """
    単一のPDFを処理する関数（並列化の単位）。

    Args:
        pdf_path (str): PDFファイルのパス。
        criteria (list): 評価基準。
        context (str): レポートの課題やテーマ。
        langchain_client (ChatOpenAI): GPTクライアント。

    Returns:
        dict: PDFの処理結果。
    """
    try:
        # PDFからテキストを抽出
        pdf_text = extract_text_from_pdf(pdf_path)

        # GPTで採点
        response = evaluate_with_langchain(pdf_text, criteria, report_context)
        parsed_response = parse_gpt_response(response, criteria)

        # グレード計算
        grade = grade_score(parsed_response["total_score"])

        # 結果を返す
        return {
            "filename": os.path.basename(pdf_path),
            "total_score": parsed_response["total_score"],
            "grade": grade,
            "details": parsed_response["details"]
        }

    except Exception as e:
        # エラーが発生した場合は記録
        return {"filename": os.path.basename(pdf_path), "error": str(e)}


def process_pdf_folder(folder_path: str, output_path: str, criteria_path: str, report_context: str, langchain_client, parallel: bool = False):
    """
    フォルダ内のPDFを処理して採点する（直列または並列）。

    Args:
        folder_path (str): PDFフォルダのパス。
        output_path (str): 評価結果を保存するパス。
        criteria_path (str): 評価基準YAMLファイルのパス。
        report_context (str): レポートの課題やテーマ。
        parallel (bool): 並列処理を有効にするかどうか。

    Returns:
        None
    """
    from evaluation import load_evaluation_criteria
    import pandas as pd
    from concurrent.futures import ThreadPoolExecutor

    # 評価基準をロード
    criteria = load_evaluation_criteria(criteria_path)

    # フォルダ内のPDFファイルをリスト化
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]

    if parallel:
        # 並列処理
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda pdf: process_single_pdf(pdf, criteria, report_context, langchain_client), pdf_files))
    else:
        # 直列処理
        results = []
        for pdf in pdf_files:
            results.append(process_single_pdf(pdf, criteria, report_context, langchain_client))

    # 結果をCSVに保存
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")


# main.pyの実行
if __name__ == "__main__":
    # フォルダパスを指定
    pdf_folder_path = Config.pdf_folder # レポートが保存されているフォルダ
    output_csv_path = Config.output_path  # 評価結果を保存するCSVのパス
    criteria_yaml_path = Config.evaluation_criteria_path  # 評価基準YAMLのパス
    report_context = """
    日本における再生医療等製品の開発状況についてレポートにまとめてください。
    """

    # GPTクライアントを初期化
    langchain_client = ChatOpenAI(model=Config.model, openai_api_key=Config.openai_api_key)

    # 採点処理関数の呼び出し
    # parallel=Trueで並列処理
    try:
        process_pdf_folder(
            folder_path=pdf_folder_path,
            output_path=output_csv_path,
            criteria_path=criteria_yaml_path,
            report_context=report_context,
            langchain_client=langchain_client,
            parallel=False
        )
    except Exception as e:
        print(f"Fatal error during processing: {e}")