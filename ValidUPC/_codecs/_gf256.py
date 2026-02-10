"""GF(256) arithmetic for Reed-Solomon error correction.

Uses the QR code polynomial: x^8 + x^4 + x^3 + x^2 + 1 (0x11d).
"""

EXP_TABLE = [0] * 512
LOG_TABLE = [0] * 256


def _init_tables():
    val = 1
    for i in range(255):
        EXP_TABLE[i] = val
        LOG_TABLE[val] = i
        val <<= 1
        if val >= 256:
            val ^= 0x11d
    # Double the exp table for convenience
    for i in range(255, 512):
        EXP_TABLE[i] = EXP_TABLE[i - 255]


_init_tables()


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[LOG_TABLE[a] + LOG_TABLE[b]]


def gf_poly_mul(p: list[int], q: list[int]) -> list[int]:
    result = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            result[i + j] ^= gf_mul(a, b)
    return result


def rs_generator_poly(nsym: int) -> list[int]:
    """Build RS generator polynomial for nsym error correction codewords."""
    g = [1]
    for i in range(nsym):
        g = gf_poly_mul(g, [1, EXP_TABLE[i]])
    return g


def rs_encode(data: list[int], nsym: int) -> list[int]:
    """Encode data with nsym RS EC codewords. Returns EC codewords only."""
    gen = rs_generator_poly(nsym)
    # Polynomial division
    feedback = [0] * (len(data) + nsym)
    feedback[:len(data)] = data[:]
    for i in range(len(data)):
        if feedback[i] != 0:
            coef = LOG_TABLE[feedback[i]]
            for j in range(1, len(gen)):
                feedback[i + j] ^= EXP_TABLE[coef + LOG_TABLE[gen[j]]]
    return feedback[len(data):]
