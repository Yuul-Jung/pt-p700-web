# PT-P700 Web Label Studio

Brother PT-P700용 웹 라벨 편집기 실험판입니다. GitHub Pages 프런트엔드와 Ubuntu USB 직접 연결용 로컬 Python 브리지를 분리했습니다. 실물 PT-P700 인쇄, 여백, 이미지 회전 및 테이프 폭별 정합성은 아직 검증되지 않았습니다.

## 파일

- `index.html`: 웹 편집, 미리보기, PNG 다운로드 및 로컬 인쇄 요청
- `bridge.py`: Ubuntu 컴퓨터의 `127.0.0.1:8765`에서만 동작하는 인쇄 서버
- `requirements.txt`: Python 이미지 처리 라이브러리

## Ubuntu 실행

```bash
# 프린터 USB 연결 확인
lsusb | grep -i brother

# 패키지 설치
sudo apt update
sudo apt install ptouch-print python3-venv

# PT-P700 직접 인쇄가 되는지 먼저 확인
ptouch-print --info
ptouch-print --text 'PT-P700 TEST'

# 저장소 복제 및 Python 환경 준비
git clone https://github.com/Yuul-Jung/pt-p700-web.git
cd pt-p700-web
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 브리지 시작 (종료: Ctrl+C)
.venv/bin/python bridge.py
```

GitHub Pages: https://yuul-jung.github.io/pt-p700-web/

GitHub에서 Settings → Pages → Build and deployment → Deploy from a branch → main, /(root)를 선택합니다.

## 주의

GitHub Pages는 정적 파일만 서비스합니다. `bridge.py`는 반드시 프린터가 연결된 Ubuntu PC에서 별도로 실행해야 합니다. 브리지 포트를 외부에 공개하지 마세요. 브리지는 허용된 브라우저 Origin만 받습니다. 일부 브라우저에서는 HTTPS 페이지에서 로컬 HTTP 서버 연결에 대한 권한 승인이 요구되거나 차단될 수 있습니다. 실제 인쇄가 실패하면 `ptouch-print`와 USB 권한을 먼저 확인하세요. 실물 검증 완료 전에는 정상 인쇄를 보장하지 않습니다.

본 코드는 LabelSis 소스를 복제하지 않았으며 `ptouch-print`는 별도 설치합니다.
