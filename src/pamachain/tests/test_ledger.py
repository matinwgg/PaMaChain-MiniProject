from pamachain.ledger.mock_chain import append_block, chain

def test_append_chain():
    entry = append_block({"label":"test","secret":"abc"})
    c = chain()
    assert c[-1]["hash"] == entry["hash"]
    assert c[-1]["label"] == "test"
    assert c[-1]["secret"] == "abc"