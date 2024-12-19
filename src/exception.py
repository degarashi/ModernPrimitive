class DGException(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

    def draw_func(self, context) -> None:
        pass


class DGFileNotFound(DGException):
    def __init__(self, file_path: str):
        msg = f"file path '{file_path}' not found"
        super().__init__(msg)


class DGObjectNotFound(DGException):
    def __init__(self, object_name: str, base_file: str | None = None):
        msg = f"object '{object_name}' not found"
        if base_file is not None:
            msg += f"\nwhere: {base_file}"
        super().__init__(msg)


class DGInvalidVersionNumber(DGException):
    def __init__(self, num: int):
        msg = f"Invalid version number ({num})"
        super().__init__(msg)


class DGUnknownAssetFound(DGException):
    def __init__(self, file_path: str):
        msg = f"unknown asset file '{file_path}' found"
        super().__init__(msg)


class DGNodeGroupNotFound(DGException):
    def __init__(self, ng_name: str, base_file: str | None = None):
        msg = f"node_group '{ng_name}' not found"
        if base_file is not None:
            msg += f"\nwhere: {base_file}"
        super().__init__(msg)
