from fiberforge.models import NamedSpan


class ContinuityService:
    @staticmethod
    def is_continuous(spans: tuple[NamedSpan, ...]) -> bool:
        return all(a.end_can == b.start_can for a, b in zip(spans, spans[1:]))

    @staticmethod
    def find_break(spans: tuple[NamedSpan, ...]):
        for a, b in zip(spans, spans[1:]):
            if a.end_can != b.start_can:
                return (a, b)
        return None
