import os

import streamlit as st
from PIL import Image
from UPload_S3 import Upload_S3
import configparser

#設定ファイル
config = configparser.ConfigParser()
config.read('/Applications/python-docker/VoiceToText_AWS/cognition.ini',encoding='utf-8')


S3_BUCKET_NAME =os.getenv('S3_BUCKET_NAME')

testFoldaOnsei_PATH = config['S3_upload']['s3Voicefile']




st.markdown('#音声ファイルを保存')
file = st.file_uploader('音声ファイルをアップロードしてください。',type=['mp3','wav'])
st.button("UPload",on_click=lambda:UploadToS3(file))

def UploadToS3(file): 
    if file:
        st.markdown(f'{file.name}をアップロードしました')
        #S3ファイルパス＋ファイル名で保存。
        Onsei_PATH = os.path.join(testFoldaOnsei_PATH,file.name)

    try:
        #S3へアップロード
        #2025/03/29 音声ファイルでS3にアップロード確認済み。
        Upload_S3.upload_to_s3(file,S3_BUCKET_NAME,Onsei_PATH)
        st.success("✅ S3へのアップロードが完了しました。")
    except Exception as e :
        print(f"アップロード中にエラー発生:{e}")
        