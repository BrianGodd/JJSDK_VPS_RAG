# JJSDK_VPS_RAG_Extension

A Unity package integrating **JORJIN JJSDK**, **Immersal VPS**, and **OCI Speech/ Generative AI RAG** to enable spatial positioning, orientation tracking, and AI-powered question answering for mobile devices and AR glasses.

## Repository Structure
```
JJSDK_VPS_RAG_Extension/
│
├── python(Backend)         # Python backend for STT, TTS, and RAG services
├── JJ_VPS_RAG.unitypackage # Unity package with sample scenes and scripts
├── README.md               # Project documentation (this file)
├── WavUtility.cs           # Utility for saving/loading WAV in Unity
└── ...
```

## Dependencies
### Unity-side
- Unity **2022.3 LTS** (minSdkVersion API 27+)
- AR Foundation 5.1+
- [GLTFUtility](https://github.com/Siccity/GLTFUtility)
- [Newtonsoft.Json for Unity](https://github.com/applejag/Newtonsoft.Json-for-Unity)
- [Immersal SDK](https://github.com/immersal/imdk-unity)
- [UnityWav](https://github.com/deadlyfingers/UnityWav)

### Backend-side
- Python 3.9+
- Requirements in `python(Backend)/requirements.txt`

## Setup

### 1. Immersal SDK
1. Scan your environment using **Immersal Mapper** (manual mode recommended).
2. Download `.glb` map from Immersal Portal and note the **Map ID**.
3. In Unity, import the map into the `XR Map` object in your scene.

### 2. OCI RAG
1. Upload your generated PDF documents to an OCI Bucket.
2. Create a RAG Agent in **Generative AI Agents** and record its OCID.
3. Verify the agent’s endpoint is `Active`.

### 3. Backend (Python)
```bash
git clone https://github.com/BrianGodd/JJSDK_VPS_RAG_Extension
cd JJSDK_VPS_RAG_Extension/python(Backend)
pip install --upgrade pip
pip install -r requirements.txt
```
- Set your OCI credentials in `STT.py`, `TTS.py`, and `rag_chat.py`.
- Start the backend:
```bash
python app.py
```
- (Optional) Use ngrok for external access:
```bash
ngrok http 5005
```

### 4. Unity Frontend
1. Import `JJ_VPS_RAG.unitypackage` into Unity.
2. Open a sample scene:
   - **Mobile** version
   - **AR Glasses** version
3. Configure `RAGController` for OCI/OpenAI STT/TTS.

## Main Scripts
- **CameraRenderer.cs** – JJSDK frame handling
- **ImmersalAPI.cs** – VPS localization
- **IMUManager.cs** – Orientation calibration & coordinate conversion
- **MicController.cs** – Audio recording & saving
- **RAGController.cs** – Backend communication and AI response handling

## Demo
[![Demo Video](https://img.youtube.com/vi/JlpbgchgMnw/0.jpg)](https://www.youtube.com/watch?v=JlpbgchgMnw)

## Contact
Brian Huang – brianbaby0409@gmail.com
