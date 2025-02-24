import os
import json
import yaml
from config import Config
from pdf_processing import extract_text_from_pdf
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def evaluate_with_langchain(text: str, criteria: list, report_context: str) -> str:
    """
    LangChainを使用して効率的に評価を行う。

    Args:
        text (str): レポートの内容（PDFから抽出したもの）。
        criteria (list): 評価基準リスト。
        report_context (str): レポートの課題やテーマ。

    Returns:
        str: GPTの応答（採点結果）。
    """
    try:
        # システムプロンプトの定義
        system_prompt = """
        あなたは熟練したレポート評価者です。以下のレポートに対して10個程度の評価基準が与えられています。
        各基準を満たす場合は1、満たさない場合は0を返してください。最後に合計点をTotalで示してください。
        回答はフォーマット例に従ってシンプルに出力してください。
        """

        # GPTクライアントの初期化
        langchain_client = ChatOpenAI(model=Config.model, openai_api_key=Config.openai_api_key)

        # プロンプト生成
        prompt = generate_evaluation_prompt(text, criteria, report_context)

        # GPTで採点
        response = langchain_client.invoke(input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])

        return response.content.strip()
    except Exception as e:
            raise RuntimeError(f"LangChainでの評価処理中にエラーが発生しました: {e}")



def load_evaluation_criteria(criteria_path: str):
    """
    YAML形式の評価基準をロードする。
    criteria: 
      - name: "序論が明確である"
      - name: "目的が明確である"
      - ...
    といった形で10個程度記載すると想定
    """
    try:
        with open(criteria_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data["criteria"]
    except Exception as e:
        raise RuntimeError(f"評価基準の読み込みに失敗しました: {e}")

def generate_evaluation_prompt(text: str, criteria: list, report_context: str):
    """
    減点項目と加点項目を明示した評価プロンプトを生成。

    Args:
        text (str): PDFから抽出したレポート内容。
        criteria (list): 評価基準リスト。
        report_context (str): レポートの課題やテーマ。

    Returns:
        str: GPTへのプロンプト。
    """
    prompt = f"以下はレポートの課題やテーマに関する説明です:\n\n{report_context}\n\n"
    prompt += f"以下はPDFから抽出されたレポートの内容です:\n\n{text}\n\n"
    prompt += "以下の評価基準に基づき、このレポートを評価してください。\n"
    prompt += "各項目について、該当する場合は「1」、該当しない場合は「0」を返してください。\n"
    prompt += "減点項目は該当する場合に指定された点数を減点し、加点項目は該当する場合に指定された点数を加点してください。\n\n"

    for i, criterion in enumerate(criteria, 1):
        direction = "減点" if criterion["points"] < 0 else "加点"
        prompt += f"{i}. {criterion['name']} ({direction}: {abs(criterion['points'])}点)\n"

    prompt += "\n出力フォーマット例:\n"
    prompt += "1: 1\n2: 0\n3: 1\n...\nTotal: X\n"
    prompt += "各項目の結果とTotal（最終スコア）を明示してください。\n"
    return prompt

def parse_gpt_response(response: str, criteria: list):
    """
    GPTの応答からスコアを計算。

    Args:
        response (str): GPTの応答。
        criteria (list): 評価基準リスト。

    Returns:
        dict: 計算結果。
    """
    import re
    try:

        total_score = 100  # 初期スコアは100点
        details = []

        # 各評価項目のスコアを解析
        score_pattern = re.compile(r'^(\d+):\s*(\d)')  # 例: "1: 1"
        for i, line in enumerate(response.strip().split("\n")):
            if match := score_pattern.match(line):
                index = int(match.group(1)) - 1
                result = int(match.group(2))  # 1: 該当, 0: 非該当
                points = criteria[index]['points']

                # 減点/加点の処理
                if result == 1:  # 該当する場合
                    total_score += points

                # 詳細を記録
                details.append({
                    "criterion": criteria[index]["name"],
                    "points": points if result == 1 else 0,
                    "result": "該当" if result == 1 else "非該当"
                })

        return {"total_score": total_score, "details": details}
    except Exception as e:
        raise ValueError(f"GPTの応答を解析中にエラーが発生しました: {e}")

def grade_score(total_score: int, thresholds=None) -> str:
    """
    総スコアを基にA～Fのグレードを計算。

    Args:
        total_score (int): 最終スコア。
        thresholds (dict): グレードの閾値。

    Returns:
        str: グレード（A～F）。
    """
    if thresholds is None:
        thresholds = {"A": 90, "B": 75, "C": 60, "D": 40}

    for grade, threshold in thresholds.items():
        if total_score >= threshold:
            return grade
    return "F"
