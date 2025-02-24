import pdfplumber

def extract_text_from_pdf(pdf_path: str):
    """
    PDFからテキストを抽出する関数

    Args:
        pdf_path(str): PDFのパス

    Returns:
        text: 抽出されたテキスト
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:  # Noneチェック
                    text += page_text + "\n"
                else:
                    print(f"警告: 空白または抽出失敗のページがあります (PDF: {pdf_path}, ページ: {page_number})")
            return text
    except Exception as e:
        raise RuntimeError(f"PDFのテキストの抽出に失敗しました: {pdf_path}, エラー詳細: {e}")
    