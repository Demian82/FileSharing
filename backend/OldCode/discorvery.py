#! python3.12

import socket
import time
import platform
from zeroconf import IPVersion, ServiceInfo, Zeroconf, ServiceBrowser

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

class MyListener:
    def remove_service(self, zeroconf, type, name):
        print(f"📡 기기 연결 해제: {name}")

    def update_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            # 주소 정보를 문자열로 변환
            address = socket.inet_ntoa(info.addresses[0])
            # OS 정보를 안전하게 추출
            raw_os = info.properties.get(b'os', b'unknown')
            target_os = raw_os.decode('utf-8') if isinstance(raw_os, bytes) else str(raw_os)
            
            print(f"\n✨ 새로운 기기 발견! ✨")
            print(f" - 이름: {name}")
            print(f" - 주소: {address}:{info.port}")
            print(f" - 운영체제: {target_os}")
            print(f"--------------------------")

if __name__ == '__main__':
    my_ip = get_local_ip()
    my_os = platform.system().lower()
    hostname = socket.gethostname()

    # 딕셔너리의 키와 값을 모두 bytes 형태로 변환해야 안전합니다.
    properties = {
        b'os': my_os.encode('utf-8'),
        b'user': hostname.encode('utf-8')
    }

    # ServiceInfo 인자 확인: (type, name, address, port, properties)
    # 최신 버전에서는 addresses(리스트)를 권장합니다.
    info = ServiceInfo(
        "_fileshare._tcp.local.",
        f"{hostname}.{my_os}._fileshare._tcp.local.",
        addresses=[socket.inet_aton(my_ip)],
        port=8000,
        properties=properties,
    )

    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    
    print(f"🚀 탐지 시작... (IP: {my_ip}, OS: {my_os})")
    
    try:
        zeroconf.register_service(info)
        listener = MyListener()
        browser = ServiceBrowser(zeroconf, "_fileshare._tcp.local.", listener)
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 중단 중...")
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()