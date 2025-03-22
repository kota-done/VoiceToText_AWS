import os

import streamlit as st
from PIL import Image
from UPload_S3.Upload_S3 import upload_to_s3

S3_BUCKET_NAME =os.getenv('S3_BUCKET_NAME')

testFoldaIMG_PATH = ''

#S3でのファイル名
s3fileName = ''

def uploadIMG():
    st.markdown('#画像を保存')
    file = st.file_uploader('画像をアップロードしてください。',type=['jpg','jpeg','HEIC','png'])
    if file:
        st.markdown(f'{file.name}をアップロードしました')
        IMG_PATH = os.path.join(testFoldaIMG_PATH,file.name)

    try:
        #S3へアップロード
        upload_to_s3(file,S3_BUCKET_NAME,s3fileName)
        print(f"Complete Upload")
    except Exception as e :
        print(f"アップロード中にエラー発生:{e}")
        

        