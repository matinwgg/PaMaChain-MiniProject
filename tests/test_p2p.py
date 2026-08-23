import pytest

from pamachain.p2p import PeerMessage, block_fingerprint, build_chain_response, build_get_chain


def test_message_round_trip():
    message = build_chain_response("abc", [{"height": 1, "hash": "x"}])
    assert PeerMessage.decode(message.encode()) == message


def test_message_rejects_oversized_payload():
    with pytest.raises(ValueError, match="size limit"):
        PeerMessage("x", "id", {"data": "a" * 2_000_000}).encode()


def test_message_rejects_wrong_protocol():
    with pytest.raises(ValueError, match="unsupported"):
        PeerMessage.decode(b'{"v":999,"kind":"chain","id":"x","payload":{}}')


def test_fingerprint_is_order_independent():
    assert block_fingerprint({"a": 1, "b": 2}) == block_fingerprint({"b": 2, "a": 1})


def test_get_chain_request():
    message = build_get_chain("request-1")
    assert message.kind == "get_chain"
    assert message.payload == {}
