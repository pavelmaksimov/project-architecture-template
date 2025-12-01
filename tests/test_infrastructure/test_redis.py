from project.infrastructure.adapters.cache import redis_transaction, isolated_redis_transaction


def test_local_transaction(redis):
    with isolated_redis_transaction() as tr:
        tr.set("foo", "bar")
        tr.set("bar", "baz")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

    assert redis.get("foo") == b"bar"
    assert redis.get("bar") == b"baz"


def test_context_transaction(redis):
    with redis_transaction() as tr:
        tr.set("foo", "bar")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

        with redis_transaction() as ltr:
            assert tr == ltr

            ltr.set("bar", "baz")

            assert redis.get("foo") == None
            assert redis.get("bar") == None

        assert redis.get("bar") == None
        assert redis.get("foo") == None

    assert redis.get("foo") == b"bar"
    assert redis.get("bar") == b"baz"


def test_context_with_local_transaction(redis):
    with redis_transaction() as tr:
        tr.set("foo", "bar")

        assert redis.get("foo") == None
        assert redis.get("bar") == None

        with isolated_redis_transaction() as ltr:
            assert tr != ltr

            ltr.set("bar", "baz")

            assert redis.get("foo") == None
            assert redis.get("bar") == None

        assert redis.get("bar") == b"baz"
        assert redis.get("foo") == None

    assert redis.get("foo") == b"bar"
