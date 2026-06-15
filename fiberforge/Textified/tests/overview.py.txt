from utils import FiberRun, FiberSpan, SpanType

fiber_run = FiberRun(
    "HUB Span",
    FiberSpan(SpanType.EXISTING_CAN),
    # BOOKMARK
    # HUB to HUB_20
    # TNP0
    FiberSpan(
        SpanType.OL,
        226,
        298,
        153,
        152,
        192,
        176,
        204,
        304,
        266,
        350,
        362,
    ),
    FiberSpan(
        SpanType.NEW_OL,
        122,
        64,
        89,
        149,
    ),
    FiberSpan(
        SpanType.OL,
        218,
        222,
    ),
    FiberSpan(SpanType.RISER, 25),
    FiberSpan(
        SpanType.UG,
        4,
        126,
        87,
        139,
        125,
        37,
        72,
        161,
        130,
    ),
    # TNP0
    FiberSpan(SpanType.EXISTING_CAN),
    # HUB to HUB_21
    # TNP0
    FiberSpan(
        SpanType.UG,
        190,
        150,
        109,
        110,
        174,
        87,
        86,
        87,
        108,
        50,
        46,
        22,
        100,
        54,
        14,
        29,
        36,
        88,
        111,
        78,
        255,
        1,
    ),
    FiberSpan(SpanType.RISER, 25),
    FiberSpan(
        SpanType.OL,
        177,
        203,
        197,
        136,
        181,
        137,
        180,
        257,
        147,
        204,
        173,
        124,
        171,
        167,
    ),
    # TNP0
    FiberSpan(SpanType.EXISTING_CAN),
    # HUB to HUB_22
    # TNP0
    FiberSpan(
        SpanType.OL,
        217,
        275,
        243,
        247,
        198,
        138,
        146,
        149,
    ),
    FiberSpan(SpanType.RISER, 25),
    FiberSpan(
        SpanType.UG,
        153,
        419,
        120,
        148,
        86,
        173,
        6,
    ),
    FiberSpan(SpanType.RISER, 25),
    FiberSpan(
        SpanType.OL,
        195,
        101,
        348,
        263,
        170,
        224,
        286,
    ),
    # TNP0
    FiberSpan(SpanType.EXISTING_CAN),
    # HUB to HUB_23
    # TNP0
    FiberSpan(
        SpanType.NEW_OL,
        364,
    ),
    FiberSpan(
        SpanType.OL,
        127,
        132,
        211,
        195,
        193,
        232,
        172,
        271,
        259,
        286,
        311,
        233,
        285,
        229,
        59,
    ),
    FiberSpan(SpanType.RISER, 25),
    FiberSpan(
        SpanType.UG,
        1,
        10,
        59,
        125,
        127,
        59,
        12,
        16,
        21,
        335,
    ),
)


def main():
    total: int = 0
    for run in fiber_run:
        print(run, flush=True)
        for span in run.span_list:
            total += sum(span.lengths)

    print(f"Total Fiber = {total}")


if __name__ == "__main__":
    main()
