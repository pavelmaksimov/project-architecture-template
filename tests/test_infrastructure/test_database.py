from sqlalchemy import text

from project.infrastructure.adapters.database import Session, transaction, current_transaction


def test_session_fixture(session):
    assert session.execute(text("SELECT 1")).scalar() == 1


def test_session():
    with Session() as s:
        with Session() as s2:
            assert s.hash_key == s2.hash_key
            assert s2.execute(text("SELECT 1")).scalar() == 1
        assert s.execute(text("SELECT 1")).scalar() == 1


def test_transaction():
    with transaction() as s:
        assert s.execute(text("SELECT 1")).scalar() == 1


def test_nested_transaction():
    with transaction() as s0:
        assert s0.execute(text("SELECT 1")).scalar() == 1

        with transaction() as s:
            assert s.execute(text("SELECT 1")).scalar() == 1

        with transaction() as s:
            with current_transaction():
                with transaction():
                    with current_transaction():
                        with Session() as s4:
                            assert s4.execute(text("SELECT 1")).scalar() == 1

            assert s.execute(text("SELECT 1")).scalar() == 1

        assert s0.execute(text("SELECT 1")).scalar() == 1

    with Session():
        with transaction() as s1:
            assert s1.execute(text("SELECT 1")).scalar() == 1

            with transaction() as s:
                assert s.execute(text("SELECT 1")).scalar() == 1

            with transaction() as s:
                assert s.execute(text("SELECT 1")).scalar() == 1

            assert s1.execute(text("SELECT 1")).scalar() == 1
