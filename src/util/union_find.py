class UnionFind:
    # Index -> connected-index
    _lead_to: list[int]

    def __init__(self, size: int):
        self._lead_to = [-1] * size

    def connect(self, from_idx: int, to_idx: int) -> None:
        if from_idx == to_idx:
            return
        if self.get_id(to_idx) == from_idx:
            return
        self._lead_to[from_idx] = to_idx

    def get_id(self, from_idx: int) -> int:
        cur = from_idx
        while True:
            next_idx = self._lead_to[cur]
            if next_idx == -1:
                break
            cur = next_idx
        if cur != from_idx:
            self._lead_to[from_idx] = cur
        return cur

    def get_groups(self) -> list[list[int]]:
        result: dict[int, list[int]] = {}

        for i in range(len(self._lead_to)):
            dest = self.get_id(i)
            if dest not in result:
                result[dest] = []
            result[dest].append(i)

        return list(result.values())

    def __str__(self) -> str:
        ret = "UF("
        for to_id in self._lead_to:
            ret += str(to_id)
            ret += ", "
        ret += ")"
        return ret
