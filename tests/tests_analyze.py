from analysis import analyze


class TestCleaning(object):
    def test_remove_stopwords(self):
        key = [
            (['the', 'dog'], ['dog'])
        ]

        for test in key:
            answer = analyze.remove_stopwords(test[0])
            assert answer == test[1]

    def test_tokenize(self):
        key = [
            ('deez nuts', ['deez', 'nuts']),
            ('multiple. sentences', ['multiple', '.', 'sentences'])
        ]

        for test in key:
            answer = analyze.tokenize_full(test[0])
            assert answer == test[1]

    def test_stem_text(self):
        key = [
            (['the', 'dog'], ['the', 'dog'])
        ]

        for test in key:
            answer = analyze.stem_text(test[0])
            assert answer == test[1]

    def test_clean_text(self):
        key = [
            (['the', 'dog'], ['dog'])
        ]

        for test in key:
            answer = analyze.clean_text(test[0])
            assert answer == test[1]
