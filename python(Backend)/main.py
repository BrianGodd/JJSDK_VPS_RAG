import time
from STT import main as STT_main
from STT import cleanup_all_job_output as STT_clean
from rag_chat import main as RAG_main
from TTS import main as TTS_main

def main(kind = 0, pos_x = 0.0, pos_z = 0.0, direction = 0.0): #0: all, 1:no stt, 2:no tts, 3:no stt&tts
    AUDIO_FILE = "uploads/input.wav"

    total_start_time = time.time()

    if kind != 1 and kind != 3:
        stt_start = time.time()
        result = STT_main(AUDIO_FILE)
        stt_end = time.time()
        print(f"STT 耗時：{stt_end - stt_start:.2f} 秒")
    else:
        with open("input.txt", "r", encoding="utf-8") as f:
            result = f.read()

    rag_start = time.time()
    chat_result = RAG_main(result, pos_x, pos_z, direction, 30)
    rag_end = time.time()
    print(f"RAG 回答耗時：{rag_end - rag_start:.2f} 秒")

    if kind != 2 and kind != 3:
        tts_start = time.time()
        TTS_main(chat_result)
        tts_end = time.time()
        print(f"TTS 耗時：{tts_end - tts_start:.2f} 秒")

    total_end_time = time.time()
    print(f"全部流程總耗時：{total_end_time - total_start_time:.2f} 秒")

    STT_clean()

if __name__ == "__main__":
    main()