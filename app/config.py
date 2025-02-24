import os
from dotenv import load_dotenv

load_dotenv()  # .env ファイルから環境変数を読み込む

class Config:
    model = os.getenv('MODEL', 'gpt-4o')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the env variables")
    
    pdf_folder = os.getenv('PDF_FOLDER')
    output_path = os.getenv('OUTPUT_PATH')
    evaluation_criteria_path = os.getenv('EVALUATION_CRITERIA_PATH')