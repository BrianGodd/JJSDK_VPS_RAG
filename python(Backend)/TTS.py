import logging
# logging.basicConfig(level=logging.DEBUG)

import oci

# 載入 OCI 設定（~/.oci/config）
config = oci.config.from_file()
config["region"] = "us-chicago-1"
ai_speech_client = oci.ai_speech.AIServiceSpeechClient(config)
COMPARTMENT_ID = "" #enter your COMPARTMENT_ID

# response = ai_speech_client.list_voices(compartment_id=COMPARTMENT_ID)

# print(response.data)

def Text2Speech(content):
    # 語音合成請求內容
    synthesize_details = oci.ai_speech.models.SynthesizeSpeechDetails(
        text=content,
        compartment_id=COMPARTMENT_ID,
        configuration=oci.ai_speech.models.TtsOracleConfiguration(
            model_family="ORACLE",
            model_details=oci.ai_speech.models.TtsOracleTts2NaturalModelDetails(
                model_name="TTS_2_NATURAL",
                voice_id="Brian"
            ),
            speech_settings=oci.ai_speech.models.TtsOracleSpeechSettings(
                text_type="TEXT",
                sample_rate_in_hz=24000,
                output_format="MP3",  # PCM 或 MP3
            )
        )
    )

    # 發送請求
    response = ai_speech_client.synthesize_speech(synthesize_speech_details=synthesize_details)

    # 儲存音檔
    with open("output.mp3", "wb") as f:
        f.write(response.data.content)

    print("✅ 語音檔已儲存：output.mp3")

def main(content):
    Text2Speech(content)