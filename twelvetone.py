def transpose(row, interval):
    return [(x + interval) % 12 for x in row]

def invert(row):
    return [(2 * row[0] - x) % 12 for x in row]

class TwelveToneMatrix:

    def __init__(self, user_row):
        if len(user_row) != 12 or len(set(user_row)) != 12:
            raise ValueError("Input must be a list of 12 unique pitch classes (0–11)")
        start_pitch = user_row[0]
        interval_to_zero = (-start_pitch) % 12
        p0 = transpose(user_row, interval_to_zero)
        self.p_rows = { (p0[0] + i) % 12: transpose(p0, i) for i in range(12) }
        i0 = invert(p0)
        self.i_rows = { (i0[0] + i) % 12: transpose(i0, i) for i in range(12) }

    def get_row(self, form):
        """Returns a row form by label (e.g. 'P0', 'I3', 'R7', 'RI10')"""
        form = form.upper()

        if form.startswith("RI"):
            index = int(form[2:])
            row = self.i_rows.get(index)
            return row[::-1] if row else None

        elif form.startswith("R"):
            index = int(form[1:])
            row = self.p_rows.get(index)
            return row[::-1] if row else None

        elif form.startswith("P"):
            index = int(form[1:])
            return self.p_rows.get(index)

        elif form.startswith("I"):
            index = int(form[1:])
            return self.i_rows.get(index)

        else:
            raise ValueError("Form must be Pn, In, Rn, or RIn (e.g., P0, I9, R2, RI11)")
