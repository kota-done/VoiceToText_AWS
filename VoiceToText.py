import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import tempfile
import wave
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import configparser
import os


#設定ファイル
config = configparser.ConfigParser()
config.read('/Applications/python-docker/Chatbot_forOST/cognition.ini',encoding='utf-8')


#音声ファイル保管先
config_audio_path = config['Voiceful']['VoiceData_filepath']
config_txt_path = config["Voiceful"]['Txt_filepath']

os.makedirs(config_audio_path, exist_ok=True)

# 現在時刻を取得してファイル名を生成
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
wav_file_name = f"recorded_audio_{current_time}.wav"
txt_file_name = f"transcription_{current_time}.txt"

wav_file_path = os.path.join(config_audio_path, wav_file_name)
txt_file_path = os.path.join(config_txt_path, txt_file_name)

# 録音フラグと音声フレーム
is_recording = False
audio_frames = []

#boto3でのS3アップロード用　2025/1/3
S3_BUCKET_NAME =os.getenv('S3_BUCKET_NAME')
s3Key = config['S3_upload']['s3Key']

# 音声認識を実行してコマンドを取得
def recognize_command(audio_segment):
    recognizer = sr.Recognizer()
    try:
        # 一時的に保存して音声認識を実行
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_segment.export(temp_file.name, format="wav")
            with sr.AudioFile(temp_file.name) as source:
                audio_data = recognizer.record(source)
                command = recognizer.recognize_google(audio_data, language="ja-JP")
                return command
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"音声認識エラー: {e}")
        return None

# 録音データを保存
def save_audio(frames, rate=16000):
    with wave.open(wav_file_path, "wb") as wf:
        wf.setnchannels(1)          # モノラル
        wf.setsampwidth(2)          # 16ビット
        wf.setframerate(rate)       # サンプリングレート
        wf.writeframes(b"".join(frames))
    st.success(f"録音データを保存しました: {wav_file_path}")

# 文字起こしを実行し、結果をテキストファイルに保存
def transcribe_audio_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ja-JP")
            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text)
            st.success(f"文字起こし結果を保存しました: {txt_file_path}")

            #テキストファイルをS3へアップロード（動作確認未） 2025/1/2
            # if text:
            # upload_to_s3(text, S3_BUCKET_NAME, s3Key)

    except sr.UnknownValueError:
        st.warning("音声を認識できませんでした。")
    except sr.RequestError as e:
        st.error(f"文字起こしサービスへの接続に失敗しました: {e}")

# テキストファイルの内容を表示
def display_transcription():
    if os.path.exists(txt_file_path):
        with open(txt_file_path, "r", encoding="utf-8") as txt_file:
            text = txt_file.read()
        st.text_area("文字起こし結果", text, height=200)
    else:
        st.info("文字起こし結果がまだありません。")

##1マイクボタンを教えたあと起動しないので、修正
#12/29 12 時ごろ
# # Streamlitアプリのメイン
# st.title("音声制御による録音と文字起こし")

# # マイク起動ボタン
# if st.button("マイクを起動"):
#     webrtc_ctx = webrtc_streamer(
#         key="speech-control",
#         mode=WebRtcMode.SENDRECV,
#         audio_receiver_size=256,
#         media_stream_constraints={"audio": True},
#         rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#     )

#     # 録音制御ボタン
#     if webrtc_ctx.audio_receiver:
#         st.info("音声コマンド『録音開始』『録音停止』で制御してください。")
#         if st.button("録音制御を開始"):
#             while True:
#                 audio_frame = webrtc_ctx.audio_receiver.get_frames(timeout=1)
#                 if not audio_frame:
#                     break

#                 # 音声コマンドの認識
#                 audio_segment = AudioSegment.from_file(audio_frame[0].data, format="webm")
#                 command = recognize_command(audio_segment)

#                 if command == "録音開始" and not is_recording:
#                     st.info("録音を開始します。")
#                     is_recording = True
#                     audio_frames = []

#                 elif command == "録音停止" and is_recording:
#                     st.info("録音を停止します。")
#                     is_recording = False
#                     save_audio(audio_frames)  # 音声データを保存
#                     transcribe_audio_to_text()  # 文字起こしを実行
#                     break

#                 elif is_recording:
#                     audio_frames.append(audio_frame[0].data)

# # ボタンで文字起こし結果を表示Chatbot_forOST/import streamlit as st.py
# if st.button("文字起こし結果を表示"):
##1     display_transcription()

# Streamlitアプリのメイン
st.title("音声制御による録音と文字起こし")

# マイク起動フラグを管理
if "webrtc_started" not in st.session_state:
    st.session_state["webrtc_started"] = False

# マイク起動処理
if not st.session_state["webrtc_started"]:
    if st.button("マイクを起動"):
        st.session_state["webrtc_started"] = True

if st.session_state["webrtc_started"]:
    st.info("マイクが起動しました。")
    try:
        webrtc_ctx = webrtc_streamer(
            key="speech-control",
            mode=WebRtcMode.SENDRECV,
            audio_receiver_size=256,
            media_stream_constraints={"audio": True},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        )

        # 録音制御ボタン
        if webrtc_ctx.audio_receiver:
            st.info("音声コマンド『録音開始』『録音停止』で制御してください。")
            if st.button("録音制御を開始"):
                while True:
                    audio_frame = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                    if not audio_frame:
                        break

                    # 音声コマンドの認識
                    audio_segment = AudioSegment.from_file(audio_frame[0].data, format="webm")
                    command = recognize_command(audio_segment)

                    if command == "録音開始" and not is_recording:
                        st.info("録音を開始します。")
                        is_recording = True
                        audio_frames = []

                    elif command == "録音停止" and is_recording:
                        st.info("録音を停止します。")
                        is_recording = False
                        save_audio(audio_frames)  # 音声データを保存
                        transcribe_audio_to_text()  # 文字起こしを実行
                        break

                    elif is_recording:
     
                        audio_frames.append(audio_frame[0].data)
    except Exception as e:
        st.error(f"WebRCTエラー:{e}")

# ボタンで文字起こし結果を表示
if st.button("文字起こし結果を表示"):
    display_transcription()