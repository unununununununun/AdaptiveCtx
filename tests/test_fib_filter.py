from experimental.fib_filter import preprocess

def test_filter_noise():
    raw = """Hello team, let's discuss the parser.
8f3c9a7e1b2d3c4e5f6a7b8c9d0e
This line is normal again.
aaaaaaaaabbbbbbbbccccccccccddddddddd
"""
    cleaned = preprocess(raw)
    assert "8f3c9a7e" not in cleaned
    assert "aaaaa" not in cleaned
    assert "This line is normal again." in cleaned