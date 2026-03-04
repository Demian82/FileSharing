from fastapi import FastAPI, File, UploadFile, Form
import os

app = FastAPI()

# 파일이 저장될 디렉토리 설정
UPLOAD_DIR = "shared_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_to_linux_format(content: bytes, filename: str) -> bytes:
    """
    텍스트 기반 파일일 경우 Windows의 CRLF(\r\n)를 Linux의 LF(\n)로 변환합니다.
    """
    text_extensions = {'.py', '.txt', '.md', '.json', '.js', '.c', '.cpp'}
    _, ext = os.path.splitext(filename)

    if ext.lower() in text_extensions:
        print(f"📝 {filename}: 텍스트 파일 호환성 리팩토링 중...")
        # CRLF -> LF 변환
        return content.replace(b'\r\n', b'\n')
    return content

@app.post("/upload")
async def receive_file(
    file: UploadFile = File(...),
    sender_os: str = Form(...)  # 보낸 기기의 OS 정보 (windows/linux)
):
    content = await file.read()
    
    # 윈도우에서 보낸 파일이라면 리팩토링 로직 실행
    if sender_os.lower() == 'windows':
        content = convert_to_linux_format(content, file.filename)
    
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(save_path, "wb") as f:
        f.write(content)
        
    print(f"✅ 파일 수신 완료: {save_path} (From: {sender_os})")
    return {"status": "success", "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    # 외부 기기에서 접속 가능하도록 0.0.0.0으로 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)