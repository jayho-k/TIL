import unittest
import io
import json
from unittest.mock import patch
from self_ask import Completion, Evidence, SearchResult, run_self_ask, FEW_SHOT


class RegressionTests(unittest.TestCase):
    def run_case(self, outputs):
        values = iter(outputs)
        self.queries = []
        def search(query):
            self.queries.append(query)
            return SearchResult('supported', '외부 근거 답.', (Evidence('doc-1', '원문 근거'),))
        return run_self_ask('사용자 질문', lambda p, stop: Completion(next(values)), search)

    def test_final_marker_inside_question_is_not_final_answer(self):
        result = self.run_case([
            ' Yes.\nFollow up: 문서의 So the final answer is: 표식 의미는?',
            '\nSo the final answer is: 실제 검색 답.',
        ])
        self.assertEqual(result['answer'], '실제 검색 답.')
        self.assertEqual(len(self.queries), 1)

    def test_generated_intermediate_answer_is_replaced_with_search(self):
        result = self.run_case([
            ' Yes.\nFollow up: 질문?\nIntermediate Answer: 모델이 지어낸 답.',
            '\nSo the final answer is: 외부 근거 답.',
        ])
        self.assertEqual(result['answer'], '외부 근거 답.')
        self.assertEqual(self.queries, ['질문?'])

    def test_duplicate_query_does_not_search_again(self):
        self.queries = []
        def search(query):
            self.queries.append(query)
            return SearchResult('supported', '근거', (Evidence('doc-1', '원문'),))
        result = run_self_ask('질문', lambda p, stop: Completion('\nFollow up: 같은 질문?'), search)
        self.assertEqual(len(self.queries), 1)
        self.assertEqual(result['status'], 'duplicate_query')

    def test_no_evidence_does_not_become_an_answer(self):
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: 질문?'),
                               lambda q: SearchResult('no_evidence'))
        self.assertEqual(result['status'], 'no_evidence')

    def test_direct_answer_requires_evidence_by_default(self):
        result = run_self_ask('질문', lambda p, stop: Completion('No.\nSo the final answer is: 답.'),
                               lambda q: self.fail('must not search'))
        self.assertEqual(result['status'], 'unverified_answer')

    def test_direct_answer_can_be_enabled(self):
        result = run_self_ask('질문', lambda p, stop: Completion('No.\nSo the final answer is: 답.'),
                               lambda q: self.fail('must not search'), require_evidence=False)
        self.assertEqual(result['answer'], '답.')

    def test_truncated_generation_is_not_accepted_as_final(self):
        result = run_self_ask('질문', lambda p, stop: Completion('So the final answer is: 잘린', 'length'),
                               lambda q: self.fail('must not search'), max_retries=0)
        self.assertEqual(result['status'], 'generation_truncated')

    def test_mixed_search_and_final_output_is_rejected(self):
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: 질문?\nSo the final answer is: 추측.'),
                               lambda q: self.fail('must not search'), max_retries=0)
        self.assertEqual(result['status'], 'invalid_output')

    def test_prompt_budget_prevents_call(self):
        result = run_self_ask('긴 질문', lambda p, stop: self.fail('must not call'),
                               lambda q: self.fail('must not search'), max_prompt_chars=5)
        self.assertEqual(result['status'], 'prompt_limit')

    def test_search_timeout_is_retried_once(self):
        outputs = iter(['Follow up: 질문?', 'So the final answer is: 답.'])
        attempts = []
        def search(q):
            attempts.append(q)
            if len(attempts) == 1:
                raise TimeoutError('temporary')
            return SearchResult('supported', '답.', (Evidence('doc-1', '답 원문'),))
        result = run_self_ask('질문', lambda p, stop: Completion(next(outputs)), search)
        self.assertEqual(result['answer'], '답.')
        self.assertEqual(len(attempts), 2)

    def test_supported_answer_without_quote_is_not_grounded(self):
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: 질문?'),
                               lambda q: SearchResult('supported', '답.', (Evidence('doc-1', ''),)))
        self.assertEqual(result['status'], 'invalid_search_result')

    def test_evidence_and_search_answer_are_preserved(self):
        result = self.run_case(['Follow up: 질문?', 'So the final answer is: 답.'])
        self.assertEqual(result['searches'][0]['evidence'][0]['source_id'], 'doc-1')
        self.assertEqual(result['searches'][0]['answer'], '외부 근거 답.')

    def test_canonical_transcript_preserves_yes_answer(self):
        result = self.run_case([' Yes.\nFollow up: 질문?', 'So the final answer is: 답.'])
        self.assertIn('Are follow up questions needed here: Yes.\nFollow up:', result['transcript'][len(FEW_SHOT):])

    def test_conflicting_evidence_is_retained_without_answering(self):
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: 질문?'),
                               lambda q: SearchResult('conflicting_evidence', '',
                                                       (Evidence('doc-1', '매일'), Evidence('doc-2', '매주'))))
        self.assertEqual(result['status'], 'conflicting_evidence')
        self.assertIsNone(result['answer'])
        self.assertEqual(len(result['searches'][0]['evidence']), 2)

    def test_normalized_duplicate_query_is_stopped(self):
        result = self.run_case(['Follow up: DB   VERSION?', 'follow up: db version?'])
        self.assertEqual(result['status'], 'duplicate_query')
        self.assertEqual(len(self.queries), 1)

    def test_search_limit_prevents_extra_search(self):
        values = iter(['Follow up: 질문1?', 'Follow up: 질문2?'])
        queries = []
        def search(q):
            queries.append(q)
            return SearchResult('supported', '답', (Evidence('doc', '원문'),))
        result = run_self_ask('질문', lambda p, stop: Completion(next(values)), search, max_searches=1)
        self.assertEqual(result['status'], 'search_limit')
        self.assertEqual(len(queries), 1)

    def test_invalid_output_retry_is_bounded(self):
        calls = []
        def complete(p, stop):
            calls.append(p)
            return Completion('잘못된 형식')
        result = run_self_ask('질문', complete, lambda q: self.fail('must not search'))
        self.assertEqual(result['status'], 'invalid_output')
        self.assertEqual(len(calls), 2)

    def test_model_call_limit_covers_retries(self):
        result = run_self_ask('질문', lambda p, stop: Completion('잘못된 형식'),
                               lambda q: self.fail('must not search'), max_model_calls=1)
        self.assertEqual(result['status'], 'model_call_limit')

    def test_no_evidence_is_not_retried(self):
        queries = []
        def search(q):
            queries.append(q)
            return SearchResult('no_evidence')
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: 질문?'), search)
        self.assertEqual(result['status'], 'no_evidence')
        self.assertEqual(len(queries), 1)

    def test_model_generated_guess_is_not_in_transcript(self):
        result = self.run_case(['Follow up: 질문?\nIntermediate Answer: 모델 추측', 'So the final answer is: 답.'])
        self.assertNotIn('모델 추측', result['transcript'])
        self.assertIn('Intermediate answer: 외부 근거 답.', result['transcript'])

    def test_overlong_search_answer_is_not_silently_truncated(self):
        result = run_self_ask('질문', lambda p, stop: Completion('Follow up: Q?'),
                               lambda q: SearchResult('supported', 'X' * 6, (Evidence('doc', '원문'),)),
                               max_answer_chars=5)
        self.assertEqual(result['status'], 'answer_limit')

    def test_timeout_after_deadline_reports_time_limit(self):
        elapsed = [0]
        def complete(p, stop):
            elapsed[0] = 5
            raise TimeoutError('late timeout')
        result = run_self_ask('질문', complete, lambda q: self.fail('must not search'),
                               clock=lambda: elapsed[0], max_seconds=1, max_retries=0)
        self.assertEqual(result['status'], 'time_limit')


class AdapterTests(unittest.TestCase):
    def test_ollama_preserves_length_stop_reason(self):
        from self_ask_ollama import make_ollama_complete
        response = io.BytesIO(json.dumps({'done': True, 'response': 'partial', 'done_reason': 'length'}).encode())
        with patch('self_ask_ollama.urlopen', return_value=response):
            reply = make_ollama_complete('existing-model')('prompt', stop=['marker'])
        self.assertEqual(reply.finish_reason, 'length')

    def test_ollama_missing_stop_reason_is_not_assumed_complete(self):
        from self_ask_ollama import make_ollama_complete
        response = io.BytesIO(json.dumps({'done': True, 'response': 'text'}).encode())
        with patch('self_ask_ollama.urlopen', return_value=response):
            reply = make_ollama_complete('existing-model')('prompt', stop=['marker'])
        self.assertNotEqual(reply.finish_reason, 'stop')


if __name__ == '__main__':
    unittest.main()
