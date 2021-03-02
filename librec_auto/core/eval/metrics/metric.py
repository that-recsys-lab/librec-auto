class Metric:
    def __init__(self, params: dict) -> None:
        self._params = params

    def get_params(self) -> dict:
        return self._params

    def evaluate(self):
        # Overridden by instances
        pass
