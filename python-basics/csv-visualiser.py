import csv

def read_csv(filepath):
    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    return rows

def compute_col_widths(rows):
    num_cols = len(rows[0])
    widths = []
    for col in range(num_cols):
        max_width = max(len(row[col]) for row in rows if col < len(row))
        widths.append(max_width)
    return widths

def build_separator(widths):
    parts = ['-' * (w + 2) for w in widths]
    return '+' + '+'.join(parts) + '+'

def build_row(row, widths, highlight_cols=None):
    PINK  = '\033[91m'
    RESET = '\033[0m'
    cells = []
    for i, (cell, width) in enumerate(zip(row, widths)):
        padded = cell.center(width)
        if highlight_cols and i in highlight_cols:
            padded = PINK + padded + RESET
        cells.append(f' {padded} ')
    return '|' + '|'.join(cells) + '|'

def visualize_table(filepath):
    rows = read_csv(filepath)
    if not rows:
        print("CSV file is empty.")
        return

    widths = compute_col_widths(rows)
    separator = build_separator(widths)

    # Detect numeric columns (all data rows are numeric)
    num_cols = len(rows[0])
    numeric_cols = set()
    for col in range(num_cols):
        if all(rows[r][col].strip().lstrip('-').isdigit() for r in range(1, len(rows)) if col < len(rows[r])):
            numeric_cols.add(col)

    print(separator)
    # Header row — highlight header labels of numeric columns too
    print(build_row(rows[0], widths, highlight_cols={0}))  # highlight "Name" header in pink
    print(separator)
    # Data rows
    for row in rows[1:]:
        print(build_row(row, widths, highlight_cols=numeric_cols))
    print(separator)

if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data.csv'
    visualize_table(filepath)