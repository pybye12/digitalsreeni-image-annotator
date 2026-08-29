"""Bounded snapshot history for reversible annotation commits."""

import copy


class AnnotationHistory:
    def __init__(self, limit=40):
        self.limit = max(1, int(limit))
        self._undo = []
        self._redo = []

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)

    def clear(self):
        self._undo.clear()
        self._redo.clear()

    def record(self, state, label):
        snapshot = copy.deepcopy(state)
        if self._undo and self._undo[-1][1] == snapshot:
            return False
        self._undo.append((str(label), snapshot))
        del self._undo[:-self.limit]
        self._redo.clear()
        return True

    def undo(self, current_state):
        if not self._undo:
            return None
        label, state = self._undo.pop()
        self._redo.append((label, copy.deepcopy(current_state)))
        return label, copy.deepcopy(state)

    def redo(self, current_state):
        if not self._redo:
            return None
        label, state = self._redo.pop()
        self._undo.append((label, copy.deepcopy(current_state)))
        return label, copy.deepcopy(state)
