from src.handlers import setup_routers


class TestSetupRouters:
    def test_returns_router_with_seven_subrouters(self):
        router = setup_routers()
        assert router is not None
        assert len(router.sub_routers) == 7
