"""API 없이 반복 흐름 확인: python example_self_ask.py"""
from self_ask import Completion, Evidence, SearchResult
from self_ask_langgraph import build_self_ask_graph


def make_demo_callbacks():
    outputs = iter([
        ' Yes.\nFollow up: 서비스 A가 사용하는 데이터베이스는 무엇인가?',
        '\nFollow up: 데이터베이스 B의 백업 주기는 무엇인가?',
        '\nSo the final answer is: 매일 새벽 2시에 백업합니다.',
    ])
    def demo_complete(prompt, stop):
        print('\n모델 입력의 이번 질문 부분:')
        print(prompt.split('\n\nQuestion:', 1)[-1])
        return Completion(next(outputs))

    def demo_search(query):
        # 검색기 대역이며 실제 검색 정확도를 평가하는 함수가 아니다.
        if query == '서비스 A가 사용하는 데이터베이스는 무엇인가?':
            return SearchResult('supported', '데이터베이스 B',
                                (Evidence('doc-1', '서비스 A는 데이터베이스 B를 사용한다.'),))
        if query == '데이터베이스 B의 백업 주기는 무엇인가?':
            return SearchResult('supported', '매일 새벽 2시',
                                (Evidence('doc-2', '데이터베이스 B는 매일 새벽 2시에 백업한다.'),))
        return SearchResult('no_evidence')

    return demo_complete, demo_search


def main():
    demo_complete, demo_search = make_demo_callbacks()
    graph = build_self_ask_graph(demo_complete, demo_search)
    result = {}
    # updates 스트림으로 노드별 변경을 확인한다. 콜백은 여전히 대역이다.
    for update in graph.stream({'question': '서비스 A가 사용하는 DB의 백업 주기는?'}, stream_mode='updates'):
        for node, changes in update.items():
            print('실행 노드:', node)
            result.update(changes)
    print('\n종료 상태:', result['status'])
    print('최종 답:', result['answer'])
    print('근거 ID:', [e['source_id'] for s in result['searches'] for e in s['evidence']])


if __name__ == '__main__':
    main()
