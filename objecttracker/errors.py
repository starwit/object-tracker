class StoppedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InputFullError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OutputEmptyError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)