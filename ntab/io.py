import csv

from   . import tab

#-------------------------------------------------------------------------------

def load_csv(lines):
    reader = csv.reader(lines)
    names = next(reader)
    return tab.from_row_seqs(names, reader)


def load_csv_file(path, **kwargs):
    with open(path, "r") as file:
        return load_csv(file, **kwargs)


