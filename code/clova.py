import sys
import os
import json
import requests
import urllib.request
import hashlib
import hmac
import base64
import time
# Clova Speech Recognition
def csr_stt(voice_path):
    lang = "Kor"  # 언어 코드 ( Kor, Jpn, Eng, Chn )
    url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang
    data = open(voice_path, "rb")
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(url, data=data, headers=headers)
    rescode = response.status_code
    if(rescode == 200):
        print(response.text)
    else:
        print("Error : " + response.text)
    return json.loads(response.text)["text"]
# Clova Premium Voice
def cvoice_tts(text, response_voice_file_name):
    encText = urllib.parse.quote(text)
    data = "speaker=nara&volume=0&speed=0&pitch=0&format=mp3&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode == 200):
        print("TTS mp3 저장")
        response_body = response.read()
        with open(response_voice_file_name, "wb") as f:
            f.write(response_body)
    else:
        print("Error Code:" + rescode)
# Chatbot
def chatbot_api(source_voice_text):
    timestamp = get_timestamp()
    request_body = {
        'version': 'v2',
        'userId': 'U47b00b58c90f8e47428af8b7bddcda3d1111111',
        'timestamp': timestamp,
        'bubbles': [
            {
                'type': 'text',
                'data': {
                    'description': source_voice_text
                }
            }
        ],
        'event': 'send'
    }
    # Request body
    encode_request_body = json.dumps(request_body).encode('UTF-8')
    # make signature
    signature = make_signature(secret_key, encode_request_body)
    # headers
    custom_headers = {
        'Content-Type': 'application/json;UTF-8',
        'X-NCP-CHATBOT_SIGNATURE': signature
    }
    print("## Timestamp : ", timestamp)
    print("## Signature : ", signature)
    print("## headers ", custom_headers)
    print("## Request Body : ", encode_request_body)
    # POST Request
    response = requests.post(headers=custom_headers, url=ep_path, data=encode_request_body)
    print(response.status_code)
    if(response.status_code == 200):
        print(response.text)
    return json.loads(response.text)["bubbles"][0]["data"]["description"]
def get_timestamp():
    timestamp = int(time.time() * 1000)
    return timestamp
def make_signature(secret_key, request_body):
    secret_key_bytes = bytes(secret_key, 'UTF-8')
    signing_key = base64.b64encode(hmac.new(secret_key_bytes, request_body, digestmod=hashlib.sha256).digest())
    return signing_key
################
#필요한 정보입력#
################
# Clova API 의 ID 입력 - CSR,CFV 호출에 사용
client_id = "<앱 등록 시 발급받은 Client ID>"
# Clova API 의 Secret 입력 - CSR,CPV 호출에 사용
client_secret = "<앱 등록 시 발급 받은 Client Secret>"
# chatbot 과 연동된 api gateway url 입력
ep_path = "<Chatbot APIGW Invoke URL 입력>"
# chatbot 의 custom secret key 입력
secret_key = "<Chatbot 의 Secretkey 입력>"
# CSR 로 전송할 로컬에 저장되어있는 음성파일 경로 입력
customer_voice_path = "<음성파일 경로>"
# CPV 로 응답받은 음성이 저장될 mp3 파일 경로
clova_voice_file_name = "<음성 파일 경로>"
###########
#실행 로직#
###########
# 고객의 음성을 텍스트로 변환
customer_voice_text = csr_stt(customer_voice_path)
# 고객의 텍스트를 챗봇에 전달
clova_text = chatbot_api(customer_voice_text)
# 챗봇 응답을 음성으로 변환하여 mp3 파일로 저장
cvoice_tts(clova_text, clova_voice_file_name)
