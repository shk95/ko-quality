"""Plain-text stock report. Synthetic fixture for the ko-quality corpus."""


def format_rows(rows):
    out = ""
    for name, quantity in rows:
        out = out + f"{name:<20}{quantity:>6}\n"
    return out


def total(rows):
    return sum(q for _, q in rows)
