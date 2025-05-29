from sqlalchemy import text

from project.infrastructure.adapters.database import Session, Transaction, CurrentTransaction


def test_session_fixture(session):
    assert session.execute(text("SELECT 1")).scalar() == 1


def test_session():
    with Session() as s:
        with Session() as s2:
            assert s.hash_key == s2.hash_key
            assert s2.execute(text("SELECT 1")).scalar() == 1
        assert s.execute(text("SELECT 1")).scalar() == 1


def test_transaction():
    with Transaction() as s:
        assert s.execute(text("SELECT 1")).scalar() == 1


def test_nested_transaction():
    with Transaction() as s0:
        assert s0.execute(text("SELECT 1")).scalar() == 1

        with Transaction() as s:
            assert s.execute(text("SELECT 1")).scalar() == 1

        with Transaction() as s:
            with CurrentTransaction() as s:
                with Transaction() as s:
                    with CurrentTransaction() as s:
                        with Session() as s:
                            assert s.execute(text("SELECT 1")).scalar() == 1

            assert s.execute(text("SELECT 1")).scalar() == 1

        assert s0.execute(text("SELECT 1")).scalar() == 1

    with Session():
        with Transaction() as s1:
            assert s1.execute(text("SELECT 1")).scalar() == 1

            with Transaction() as s:
                assert s.execute(text("SELECT 1")).scalar() == 1

            with Transaction() as s:
                assert s.execute(text("SELECT 1")).scalar() == 1

            assert s1.execute(text("SELECT 1")).scalar() == 1
