#AWSへの認証情報
import boto3
import os
from dotenv import load_dotenv
from io import BytesIO
# .envファイルの内容を読み込見込む
load_dotenv()

# #1 AWS認証情報 IAM Identity Centerのユーザーのため、セッショントークンが必要。エラーが頻発するため、envファイルでの参照中断
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_REGION = os.getenv('AWS_DEFAULT_REGION')
# S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# # S3クライアントの初期化
# s3 = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION,
# #1)

#設定ファイル 2025/1/3
import configparser
config = configparser.ConfigParser()
config.read('/Applications/python-docker/Chatbot_forOST/cognition.ini',encoding='utf-8')


#boto3初期化 AWS CLIの認証情報を利用。2025/1/3
s3 = boto3.client('s3')


def upload_to_s3(content: str, bucket_name: str, file_name: str):
    """
    メモリ上の文字列をテキストファイルとしてS3にアップロードする関数
    """
    # 文字列をバイトストリームに変換
    text_data = BytesIO(content.encode("utf-8"))
    
    # S3にアップロード
    s3.upload_fileobj(
        Fileobj=text_data,  # メモリ上のデータ
        Bucket=bucket_name,  # アップロード先のS3バケット名
        Key=file_name,  # S3上でのファイル名
    )
    print(f"S3にアップロード成功: {file_name}")

# 文字起こし結果（`text`変数）を生成し、アップロード
if __name__ == "__main__":
    # 文字起こし結果を仮定（通常は文字起こし処理の出力として取得）
    text = "これはサンプルの文字起こし結果です。"

    # ファイル名を指定
    file_name = "transcription_sample.txt"

    # S3にアップロード
    upload_to_s3(text, S3_BUCKET_NAME, file_name)