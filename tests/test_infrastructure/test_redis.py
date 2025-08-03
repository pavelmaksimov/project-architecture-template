from project.infrastructure.adapters.cache import context_redis_transaction, local_redis_transaction


def test_local_transaction(redis):
    with local_redis_transaction() as tr:
        tr.set("foo", "bar")
        tr.set("bar", "baz")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

    assert redis.get("foo") == b"bar"
    assert redis.get("bar") == b"baz"


def test_context_transaction(redis):
    with context_redis_transaction() as tr:
        tr.set("foo", "bar")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

        with context_redis_transaction() as ltr:
            assert tr == ltr

            ltr.set("bar", "baz")

            assert redis.get("foo") == None
            assert redis.get("bar") == None

        assert redis.get("bar") == None
        assert redis.get("foo") == None

    assert redis.get("foo") == b"bar"
    assert redis.get("bar") == b"baz"


def test_context_with_local_transaction(redis):
    with context_redis_transaction() as tr:
        tr.set("foo", "bar")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

        with local_redis_transaction() as ltr:
            assert tr != ltr

            ltr.set("bar", "baz")

            assert redis.get("foo") == None
            assert redis.get("bar") == None

        assert redis.get("bar") == b"baz"
        assert redis.get("foo") == None

    assert redis.get("foo") == b"bar"
