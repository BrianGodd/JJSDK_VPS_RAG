import logging
# logging.basicConfig(level=logging.DEBUG)

import oci
import time
import json
# from oci.ai_speech import AIServiceSpeechClient
# from oci.ai_speech.models import (
#     CreateTranscriptionJobDetails,
#     ObjectListFileInputLocation,
#     ObjectLocation,
#     TranscriptionModelDetails
# )

# === 參數設定 ===
AUDIO_FILE = "sample_mixed.wav"
BUCKET_NAME = "Speech"
OBJECT_NAME = "uploaded-sample.wav"
NAMESPACE = "" #enter your upload bucket namespace
input_prefix = "uploads"
output_prefix = "speech-output"
final_prefix = "transcripts"

# Speech configuration
model_type = "ORACLE"  # or "WHISPER_MEDIUM" or "ORACLE"
language_code = "en"  # "en-US" for ORACLE "en" for whisper

# === 初始化客戶端 ===
config = oci.config.from_file()
config["region"] = "us-chicago-1"
object_storage = oci.object_storage.ObjectStorageClient(config)
object_storage_client = oci.object_storage.ObjectStorageClient(config)
ai_speech_client = oci.ai_speech.AIServiceSpeechClient(config)
COMPARTMENT_ID = "" #enter your COMPARTMENT_ID

def upload_audio_file(file_name):
    """Uploads an audio file to Object Storage."""
    with open(file_name, "rb") as f:
        audio_upload_name = input_prefix + "/" + OBJECT_NAME
        object_storage_client.put_object(
            namespace_name=NAMESPACE,
            bucket_name=BUCKET_NAME,
            object_name=audio_upload_name,
            put_object_body=f,  # Use read() to get the file content
        )
    print("Successfully uploaded input file to Object Storage")
    return audio_upload_name

from pydub import AudioSegment
import os
def boost_upload_audio_file(file_name):
    """
    壓縮音檔為 FLAC 後上傳至 OCI Object Storage。
    :param file_name: 原始 .wav 檔案路徑
    :return: 上傳後的 Object 名稱
    """
    # 確保轉成 FLAC 存在
    file_root = os.path.splitext(os.path.basename(file_name))[0]
    compressed_file = f"{file_root}.flac"
    audio = AudioSegment.from_wav(file_name)
    audio.export(compressed_file, format="flac")

    # 準備上傳
    object_name = f"{input_prefix}/{compressed_file}"
    with open(compressed_file, "rb") as f:
        object_storage_client.put_object(
            namespace_name=NAMESPACE,
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            put_object_body=f
        )

    print(f"✅ 已上傳 FLAC 檔案：{object_name}")
    os.remove(compressed_file)  # 上傳完刪除暫存檔

    return object_name

def create_speech_job(audio_upload_name): 
    """Creates a speech transcription job."""
    print("Starting transcription process")  
    create_transcription_job_response = ai_speech_client.create_transcription_job(
        create_transcription_job_details=oci.ai_speech.models.CreateTranscriptionJobDetails(
            compartment_id=COMPARTMENT_ID,
            input_location=oci.ai_speech.models.ObjectListInlineInputLocation(
                location_type="OBJECT_LIST_INLINE_INPUT_LOCATION",
                object_locations=[
                    oci.ai_speech.models.ObjectLocation(
                        namespace_name=NAMESPACE,
                        bucket_name=BUCKET_NAME,
                        object_names=[audio_upload_name],
                    )
                ],
            ),
            output_location=oci.ai_speech.models.OutputLocation(
                namespace_name=NAMESPACE,
                bucket_name=BUCKET_NAME,
                prefix=output_prefix,
            ),
            #display_name=filename,
            model_details=oci.ai_speech.models.TranscriptionModelDetails(
                domain="GENERIC",
                model_type=model_type,
                # language_code=language_code,
                transcription_settings=oci.ai_speech.models.TranscriptionSettings(
                    diarization=oci.ai_speech.models.Diarization(
                        is_diarization_enabled=True
                    )
                ),
            ),
        )
    )

    job_id = create_transcription_job_response.data.id
    out_loc = create_transcription_job_response.data.output_location.prefix
    print(f"{job_id}, {out_loc}")
    return job_id, out_loc

def wait_for_job_completion(job_id, out_loc):
    """
    Waits for the Oracle STT transcription job to complete.
    Polls every 3 seconds and prints elapsed time.
    """
    start_time = time.time()
    poll_interval = 2  # 每次輪詢間隔秒數

    while True:
        try:
            get_transcription_job_response = ai_speech_client.get_transcription_job(
                transcription_job_id=job_id
            )
            status = get_transcription_job_response.data.lifecycle_state

            elapsed = time.time() - start_time
            minutes, seconds = divmod(int(elapsed), 60)
            print(f"⏱️ 等待中... {status} | Elapsed: {minutes:02d}:{seconds:02d}")

            if status == "SUCCEEDED":
                print(f"✅ Transcription completed in {minutes:02d}:{seconds:02d}")
                break
            elif status in ["FAILED", "CANCELED"]:
                raise RuntimeError(f"❌ Job {status}. Please check OCI console.")

            time.sleep(poll_interval)

        except oci.exceptions.ServiceError as e:
            print(f"⚠️ OCI API Error: {e}")
            break

    # 組合輸出 JSON 的 object 名稱
    ori_name = get_transcription_job_response.data.input_location.object_locations[0].object_names[0]
    res_file = f"{out_loc}{NAMESPACE}_{BUCKET_NAME}_{ori_name}.json"
    print(f"📄 Output JSON file: {res_file}")
    return res_file


def download_speech_json(res_file):
    """Downloads the transcript from Object Storage."""
    print("Fetching speech json output")
    get_object_response = object_storage_client.get_object(
        namespace_name=NAMESPACE,
        bucket_name=BUCKET_NAME,
        http_response_content_type="text/plain",
        object_name=res_file,
    )
    json_data = json.loads(get_object_response.data.content)
    print("Get JSON from Object Storage, OK")
  
    return json_data

def create_transcript(json_data):
    """Creates a formatted transcript from JSON data."""
    print("Formatting transcript from raw json")
    transcript = ""
    # Check if 'transcriptions' exists in json_data
    if isinstance(json_data.get("transcriptions"), list) and len(json_data["transcriptions"]) > 0:
        for entry in json_data["transcriptions"][0]["tokens"]:
            text = entry["token"]
            # if current_speaker != speaker_index:
            #     speaker_name = speaker1_name if speaker_index == 0 else speaker2_name
            #     transcript += f"\n\n{speaker_name}: {text} "
            #     current_speaker = speaker_index
            # else:
            transcript += f"{text} "
    return transcript

def cleanup_all_job_output(prefix="speech-output/job-"):
    print("🧹 開始清除所有 job 輸出資料夾中的檔案...")

    list_response = object_storage_client.list_objects(
        namespace_name=NAMESPACE,
        bucket_name=BUCKET_NAME,
        prefix=prefix,
        fields=["name"]
    )

    for obj in list_response.data.objects:
        obj_name = obj.name
        if obj_name.endswith("/"):
            continue  # 跳過資料夾虛擬標記

        print(f"🗑️ 刪除檔案: {obj_name}")
        object_storage_client.delete_object(
            namespace_name=NAMESPACE,
            bucket_name=BUCKET_NAME,
            object_name=obj_name
        )

    print("✅ 已清除所有 job-* 資料夾內的檔案。")

import whisper

def detect_language_from_wav(file_path: str, model_size: str = "tiny") -> str:
    """
    使用 OpenAI Whisper 本地模型快速判斷 WAV 音檔的語言。
    
    :param file_path: 音檔路徑（.wav）
    :param model_size: Whisper 模型大小，可選 tiny、base、small（越小越快）
    :return: 語言代碼，例如 'en', 'zh', 'ja'
    """
    model = whisper.load_model(model_size)
    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)  # 長度固定化

    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)

    # 找出最高機率的語言代碼
    detected_lang = max(probs, key=probs.get)
    # print("🌐 語言機率分布：")
    # for lang, p in sorted(probs.items(), key=lambda x: -x[1]):
    #     print(f"  {lang}: {p:.2%}")
        
    return detected_lang

def main(file_name):
    # cleanup_all_job_output()
    audio_upload_name = boost_upload_audio_file(file_name)
    # lang_code = detect_language_from_wav(AUDIO_FILE)
    # print("🎯 偵測到的語言：", lang_code)
    # language_code = lang_code

    job_id, out_loc = create_speech_job(audio_upload_name)
    res_file = wait_for_job_completion(job_id, out_loc)
    json_data = download_speech_json(res_file)
    transcript = create_transcript(json_data)
    print(transcript)
    return transcript