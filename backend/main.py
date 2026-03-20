import socket
import platform
import os
import asyncio
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from contextlib import asynccontextmanager

# -- [Discovery Logic] --
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

zeroconf = Zeroconf(ip_version=IPVersion.V4Only)

def start_discovery():
    my_ip = get_local_ip()
    my_os = platform.system().lower()
    hostname = socket.gethostname()

    properties =  {b'os': my_ip.encode() , b'hostname': hostname.encode()}

    info = ServiceInfo(
        "_filetransfer._tcp.local.",
        f"{hostname}.{my_os}._filetransfer._tcp.local.",
        addresses=[socket.inet_aton(my_ip)],
        port=8000,
        properties=properties,
    )
    zeroconf.register_service(info)
    print(f"Active discovering network {my_ip}")
    return info

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup] execute when starting server
    info = start_discovery()
    app.state.discovery_info = info

    yield # Server waits here until operating requests

    # [Shutdown] execute when shutting down server
    print("Shutting down server...")
    zeroconf.unregister_service(app.state.discovery_info)
    zeroconf.close()

# apply lifespan when creating app instance with FastAPI
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    )

UPLOAD_DIR = "shared_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -- [File Upload and Refactoring Logic] --
@app.post("/upload")
async def receive_file(file: UploadFile = File(...), sender_os: str = Form(...)):
    content = await file.read()
    
    # Refactoring for Windows-originated files: Convert CRLF to LF for text-based files
    if sender_os.lower() == 'windows':
        text_extensions = {'.py', '.txt', '.md', '.json'}
        if any(file.filename.endswith(ext) for ext in text_extensions):
            content = content.replace(b'\r\n', b'\n')
            print(f"{file.filename} Refactoring complete (CRLF -> LF)")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, 'wb') as f:
        f.write(content)

    return {"message": "Success", "file": file.filename}

@app.get("/files")
async def list_files():
    try:
        files = os.listdir(UPLOAD_DIR)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename:path}")
async def download_file(filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "shared_files", filename)

    print(f"================ DOWNLOAD DEBUG ================")
    print(f"1. Requested File name: {filename}")
    print(f"2. Abspath that server find: {file_path}")
    print(f"3. File exits: {os.path.exists(os.path.exists(file_path))}")
    print(f"=================================================")

    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/files/{filename:path}")
async def delete_file(filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "shared_files", filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {"message": f"Succesfully deleted {filename}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to dele file: {str(e)}")
    
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)