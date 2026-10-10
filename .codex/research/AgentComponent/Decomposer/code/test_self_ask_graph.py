import unittest
from self_ask import Completion, Evidence, SearchResult


class GraphTests(unittest.TestCase):
    def build(self, outputs):
        from self_ask_langgraph import build_self_ask_graph
        answers = iter(outputs)
        self.inputs = []
        def complete(prompt, stop):
            self.inputs.append(prompt)
            return Completion(next(answers))
        def search(query):
            return SearchResult('supported', 'DB B', (Evidence('doc-1', 'service uses DB B'),))
        return build_self_ask_graph(complete, search)

    def test_graph_has_separate_execution_nodes(self):
        graph = self.build([])
        self.assertTrue({'initialize', 'decide', 'retrieve', 'finalize'}.issubset(graph.get_graph().nodes))

    def test_stream_exposes_search_then_next_decision(self):
        graph = self.build(['Follow up: service database?', 'So the final answer is: DB B'])
        updates = list(graph.stream({'question': 'Which database?'}, stream_mode='updates'))
        names = [next(iter(update)) for update in updates]
        self.assertEqual(names, ['initialize', 'decide', 'retrieve', 'decide', 'finalize'])
        self.assertIn('Intermediate answer: DB B', self.inputs[1])

    def test_reusing_graph_does_not_reuse_previous_request_evidence(self):
        graph = self.build(['Follow up: service database?', 'So the final answer is: DB B',
                            'So the final answer is: guessed'])
        first = graph.invoke({'question': 'first'})
        second = graph.invoke({'question': 'second'})
        self.assertEqual(first['status'], 'completed')
        self.assertEqual(second['status'], 'unverified_answer')
        self.assertEqual(second['searches'], [])

    def test_more_than_25_graph_steps_uses_configured_budget(self):
        from self_ask_langgraph import build_self_ask_graph
        outputs = iter([f'Follow up: question-{i}?' for i in range(15)] + ['So the final answer is: done'])
        graph = build_self_ask_graph(
            lambda p, stop: Completion(next(outputs)),
            lambda q: SearchResult('supported', 'evidence', (Evidence('doc', 'quote'),)),
            max_searches=15, max_model_calls=16,
        )
        result = graph.invoke({'question': 'many hops'})
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(len(result['searches']), 15)


if __name__ == '__main__':
    unittest.main()
