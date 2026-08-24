from src.core.block_lists import banned, shadowbanned


class TestBanned:
    def test_exists(self):
        assert isinstance(banned, set)
        assert len(banned) == 0

    def test_add(self):
        banned.add(1)
        assert 1 in banned

    def test_discard(self):
        banned.add(1)
        banned.discard(1)
        assert 1 not in banned

    def test_discard_nonexistent(self):
        banned.discard(999)
        assert 999 not in banned


class TestShadowbanned:
    def test_exists(self):
        assert isinstance(shadowbanned, set)
        assert len(shadowbanned) == 0

    def test_add(self):
        shadowbanned.add(2)
        assert 2 in shadowbanned

    def test_discard(self):
        shadowbanned.add(2)
        shadowbanned.discard(2)
        assert 2 not in shadowbanned
