#!/usr/bin/env python3
import pathlib
import pandas

out_dir = pathlib.Path("out/")

def main():
    """Main method."""
    dfs = []
    for path in out_dir.glob("*.csv"):
        df = pandas.read_csv(path)
        dfs.append(df)

    df = pandas.concat(dfs)
    assert df.amount.sum() == 0


if __name__ == "__main__":
    main()
