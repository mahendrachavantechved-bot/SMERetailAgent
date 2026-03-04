import requests

SARVAM_API_KEY = "sk_rc853rl4_5uIuUN2Brd sme_retail_loan  kpKFqZia1T10vV"

def stt_from_file(file_path):
    url = "https://api.sarvam.ai/v1/speech-to-text"
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
    files = {"file": open(file_path, "rb")}
    try:
        r = requests.post(url, headers=headers, files=files)
        return r.json().get("text", "No transcription")
    except:
        return "STT Error"
