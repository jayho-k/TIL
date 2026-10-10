"""기존 Ollama 모델을 문자열 completion에 연결하는 예제."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from self_ask import Completion, TransientError


def make_ollama_complete(model, url='http://localhost:11434/api/generate', timeout=20):
    """모델 설치·다운로드는 하지 않는다. raw completion 적합성은 별도 확인."""
    if not model or timeout <= 0:
        raise ValueError('모델명과 양수 timeout이 필요합니다.')

    def complete(prompt, stop):
        body = {'model': model, 'prompt': prompt, 'raw': True, 'stream': False,
                'options': {'temperature': 0, 'num_predict': 256, 'stop': stop}}
        request = Request(url, data=json.dumps(body).encode('utf-8'),
                          headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=timeout) as response:
                data = json.load(response)
        except HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                raise TransientError('Ollama 일시적 HTTP 오류') from exc
            # 영구 HTTP 오류는 재시도하지 않고 유효하지 않은 응답으로 종료.
            return Completion('', 'http_error')
        except URLError as exc:
            raise ConnectionError('Ollama 연결 실패') from exc
        except (ValueError, UnicodeDecodeError):
            return Completion('', 'invalid_response')
        if not isinstance(data, dict) or data.get('done') is not True:
            return Completion('', 'invalid_response')
        # 종료 사유 누락을 정상 완료라고 추정하지 않는다.
        return Completion(data.get('response'), data.get('done_reason', 'unknown'))

    return complete
