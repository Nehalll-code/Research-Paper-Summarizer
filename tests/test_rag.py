from src.rag import PaperIndex, answer_question

PAPERS = [
    {'filename': 'a.pdf', 'year': 2020, 'source': 'upload',
     'text': 'Transformers use self-attention to model long range dependencies in text. ' * 20},
    {'filename': 'b.pdf', 'year': 2015, 'source': 'arxiv',
     'text': 'Convolutional networks classify images using learned spatial filters. ' * 20},
]


def test_search_ranks_and_filters():
    idx = PaperIndex()
    assert idx.build(PAPERS) > 0
    hits = idx.search('self-attention', k=3)
    assert hits[0]['paper'] == 'a.pdf'
    assert all(h['paper'] == 'b.pdf' for h in idx.search('x', k=3, paper='b.pdf'))
    assert all(h['paper'] == 'a.pdf' for h in idx.search('x', k=3, min_year=2018))


def test_extractive_fallback(monkeypatch):
    monkeypatch.delenv('GROQ_API_KEY', raising=False)
    idx = PaperIndex(); idx.build(PAPERS)
    ans, backend = answer_question('what is attention?', idx.search('attention'))
    assert backend == 'extractive' and '[1]' in ans
