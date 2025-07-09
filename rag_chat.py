import oci
import os
import json

# OCI 設定
config = oci.config.from_file()
endpoint = "https://agent-runtime.generativeai.us-chicago-1.oci.oraclecloud.com"
#enter your agent endpoint OCID
agent_endpoint_id = ""

session_cache_file = "session_cache.json"

def load_cached_session():
    if os.path.exists(session_cache_file):
        with open(session_cache_file, "r") as f:
            data = json.load(f)
            return data.get("session_id")
    return None

def save_cached_session(session_id):
    with open(session_cache_file, "w") as f:
        json.dump({"session_id": session_id}, f)

def validate_session(client, session_id):
    try:
        client.get_session(
            agent_endpoint_id=agent_endpoint_id,
            session_id=session_id
        )
        return True
    except oci.exceptions.ServiceError as e:
        if e.status == 404:
            print("⚠️ 快取的 Session 已失效，將重新建立。")
            return False
        raise  # 其他錯誤照原樣丟出

def get_or_create_session(client):
    cached_id = load_cached_session()
    if cached_id and validate_session(client, cached_id):
        print("🧠 使用有效的快取 Session ID:", cached_id)
        return cached_id

    print("📡 建立新 Session...")
    resp = client.create_session(
        create_session_details=oci.generative_ai_agent_runtime.models.CreateSessionDetails(
            display_name="cached-session",
            description="Reusable RAG session"
        ),
        agent_endpoint_id=agent_endpoint_id
    )
    session_id = resp.data.id
    save_cached_session(session_id)
    print("✅ 新建立 Session ID:", session_id)
    return session_id

def Chat(content):
    client = oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient(
        config=config,
        service_endpoint=endpoint
    )

    session_id = get_or_create_session(client)

    reply = client.chat(
        agent_endpoint_id=agent_endpoint_id,
        chat_details=oci.generative_ai_agent_runtime.models.ChatDetails(
            session_id=session_id,
            user_message=content
        )
    )
    return reply.data.message.content.text

def main(content, pos_x = 0.0, pos_z = 0.0, direction = 0.0, max_token_hint=100):
    # prompt = f"Please answer the following question in no more than {max_token_hint} words: {content}"
    prompt = f"I’m standing at ({pos_x}, {pos_z}) which means (X, Z) and facing toward {direction} degrees, where 0° points north (Z+) and 90° points east (X+). You can use the relative direction to answer questions, but do not use the coordinates and the compass. Based on these, please answer the following question naturally in under {max_token_hint} words: {content}"
    
    result = Chat(prompt)
    print("\nQ:\n", prompt)
    print("\n🧠 AI 回答：\n", result)
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(result)
    return result

# main("I am currently located at (-2, 3.5). Where am I right now? What is nearby?")
