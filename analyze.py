#!/usr/bin/env python
import matplotlib.pyplot as plt
import pandas as pd


def plot(fname):
    df = pd.read_csv(fname)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")
    df["power"].plot()
    plt.show()


def main():
    from sys import argv

    if len(argv) != 2:
        exit("Usage: analyze timeseries.csv")
    fname = argv[1]
    plot(fname)


if __name__ == "__main__":
    main()
