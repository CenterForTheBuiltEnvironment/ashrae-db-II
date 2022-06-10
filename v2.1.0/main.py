import numpy as np
import pandas as pd
from pythermalcomfort.models import pmv_ppd, set_tmp
from pythermalcomfort.utilities import (
    v_relative,
    clo_dynamic,
    running_mean_outdoor_temperature,
)


def data_validation():
    import matplotlib as mpl

    mpl.use("Qt5Agg")  # or can use 'TkAgg', whatever you have/prefer
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_style("whitegrid")
    plt.rc("axes.spines", top=False, right=False, left=False)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["figure.figsize"] = (7, 3)

    db_210 = pd.read_csv(
        "./v2.1.0/db_measurements_v2.1.0.csv.gz",
        compression="gzip",
        dtype={"air_movement_preference": str, "air_movement_acceptability": str},
        low_memory=False,
    )

    # check data types
    for col in db_210.columns:
        print(col, set(type(x) for x in db_210[col].unique()))
        print(col, db_210[col].unique())

    db_201 = pd.read_csv(
        "./v2.1.0/source_data/db_measurements_v2.0.1.csv.gz",
        compression="gzip",
        low_memory=False,
    )

    # check weather data
    plt.subplots(1, 1, constrained_layout=True)
    df_combined = pd.merge(db_201, db_210, on="record_id", how="left")
    plt.scatter(x="t_out_isd_x", y="t_out_isd_y", data=df_combined)
    plt.show()

    _df_meta = pd.read_csv(
        "./v2.1.0/db_metadata.csv",
    )

    # check PMV
    print(df_combined[["pmv_x", "pmv_y", "pmv_ce"]].describe().to_markdown())

    f, axs = plt.subplots(1, 2, sharey=True, sharex=True, constrained_layout=True)
    axs[0].scatter(y="pmv_x", x="pmv_y", data=df_combined, s=1, alpha=0.05)
    axs[1].scatter(y="pmv_x", x="pmv_ce", data=df_combined, s=1, alpha=0.05)
    axs[0].plot([-4, 4], [-4, 4])
    axs[1].plot([-4, 4], [-4, 4])
    axs[0].set(ylabel="PMV DB II", xlabel="PMV ISO")
    axs[1].set(xlabel="PMV ASHRAE")
    inset_ax = f.add_axes([0.35, 0.25, 0.15, 0.2])
    inset_ax.hist(df_combined.pmv_x - df_combined.pmv_y, 100)
    inset_ax.set(title="Delta", xlim=(-0.25, 1), yticks=[])
    inset_ax = f.add_axes([0.80, 0.25, 0.15, 0.2])
    inset_ax.hist(df_combined.pmv_x - df_combined.pmv_ce, 100)
    inset_ax.set(title="Delta", xlim=(-0.25, 1), yticks=[])
    plt.show()

    f, axs = plt.subplots(1, 1, constrained_layout=True)
    axs.scatter(x="set_y", y="set_x", data=df_combined, s=5, alpha=0.3)
    axs.set(ylabel="SET DB II", xlabel="SET pythermalcomfort")
    axs.plot([10, 40], [10, 40], c="k")
    inset_ax = f.add_axes([0.65, 0.25, 0.3, 0.2])
    inset_ax.hist(df_combined.set_x - df_combined.set_y, 200)
    inset_ax.set(title="Delta", xlim=(-1, 3), yticks=[])
    plt.show()

    _data = pd.merge(db_210, _df_meta, on="building_id")

    print(_data[["ta", "tr", "rh", "met", "vel", "clo"]].describe().to_markdown())

    # check for anomalies in the thermal_sensation data
    for _id in _data.contributor.unique():
        df_building = _data.query("contributor == @_id")
        if df_building.dropna(subset=["thermal_preference"]).shape[0] == 0:
            continue
        plt.figure()
        sns.boxplot(
            x="thermal_preference",
            y="thermal_sensation",
            data=df_building.sort_values("thermal_preference"),
        )
        plt.title(_id)
        plt.tight_layout()
        plt.show()

    plt.figure()
    sns.boxenplot(
        x="thermal_preference", y="ta", data=_data.sort_values("thermal_preference")
    )
    plt.tight_layout()
    plt.show()

    plt.figure()
    sns.boxenplot(
        x="thermal_preference", y="set", data=_data.sort_values("thermal_preference")
    )
    plt.tight_layout()
    plt.show()

    plt.figure()
    sns.boxenplot(
        x="thermal_preference",
        y="thermal_sensation",
        data=_data.sort_values("thermal_preference"),
    )
    plt.tight_layout()
    plt.show()

    plt.figure()
    sns.boxenplot(
        x="air_movement_preference",
        y="vel",
        data=_data.sort_values("thermal_preference"),
    )
    plt.tight_layout()
    plt.show()


def calculate_running_mean_outdoor_temperature():
    """This function calculates the running mean outdoor temperature using
    pythermalcomfort function running_mean_outdoor_temperature.

    It uses the default values for alpha, and it calculates the value
    using 7-day of data.
    """

    df_weather = pd.read_csv(
        "./v2.1.0/weather_data.gz",
        compression="gzip",
    )

    df_weather.date = pd.to_datetime(df_weather.date).dt.date
    df_weather["t_rmt"] = np.nan
    for station in df_weather.code.unique():
        df_station = df_weather.query("code == @station").sort_values("date")
        for date in df_station.date.unique():
            dates = pd.date_range(end=date, periods=8)
            _ = df_station[
                (df_station.date <= dates[-2].date())
                & (df_station.date >= dates[0].date())
            ]
            _ = _[["date", "t_out_isd"]].sort_values("date", ascending=False)
            if _.shape[0] == 7:
                t_rmt = running_mean_outdoor_temperature(_.t_out_isd.values)
                df_weather.loc[
                    (df_weather.code == station) & (df_weather.date == date), "t_rmt"
                ] = t_rmt

    df_weather.to_csv("./v2.1.0/weather_data_t_rmt.gz", compression="gzip", index=False)


if __name__ == "__main__":

    # read old version of the DB
    df = pd.read_csv(
        "./v2.1.0/source_data/db_measurements_v2.0.1.csv.gz",
        low_memory=False,
        compression="gzip",
    )

    # dropping entries without ta and keeping only those with 10 < ta < 40
    df = df[df["ta"] < 40]
    df = df[df["ta"] > 10]

    # filtering other variables too
    df = df.drop(df[(df.met < 0) | (df.met > 4)].index)
    df = df.drop(df[(df.clo < 0) | (df.clo > 4)].index)
    df = df.drop(df[(df.vel < 0) | (df.vel > 4)].index)
    df = df.drop(df[(df.tr < 0) | (df.tr > 50)].index)

    # drop PMV, PPD, and SET values previously calculated
    df = df.drop(columns=["pmv", "ppd", "set"])

    # estimate mean radiant temperature from operative temperature
    df.loc[df.tr.isna(), "tr"] = 2 * df[df.tr.isna()].top - df[df.tr.isna()].ta

    # drop rows which do not have the necessary data to calculate the PMV
    df_pmv = df.copy().dropna(subset=["ta", "tr", "rh", "met", "vel", "clo"])

    # calculate relative air speed and dynamic clothing
    v_rel = v_relative(v=df_pmv["vel"], met=df_pmv["met"])
    clo_d = clo_dynamic(clo=df_pmv["clo"], met=df_pmv["met"])
    df_pmv["vel_r"] = v_rel
    df_pmv["clo_d"] = clo_d

    # calculate SET temperature
    df_pmv["set"] = set_tmp(
        tdb=df_pmv.ta,
        tr=df_pmv.tr,
        v=df_pmv.vel,
        rh=df_pmv.rh,
        met=df_pmv.met,
        clo=df_pmv.clo,
    )

    df = pd.merge(df, df_pmv[["set"]], left_index=True, right_index=True, how="left")

    # calculate different PMV indices
    results = pmv_ppd(
        tdb=df_pmv["ta"],
        tr=df_pmv["tr"],
        vr=df_pmv["vel_r"],
        rh=df_pmv["rh"],
        met=df_pmv["met"],
        clo=df_pmv["clo_d"],
        wme=0,
        standard="ashrae",
    )

    df_pmv["pmv_ce"] = results["pmv"]
    df_pmv["ppd_ce"] = results["ppd"]

    results = pmv_ppd(
        tdb=df_pmv["ta"],
        tr=df_pmv["tr"],
        vr=df_pmv["vel_r"],
        rh=df_pmv["rh"],
        met=df_pmv["met"],
        clo=df_pmv["clo_d"],
        wme=0,
        standard="iso",
    )

    df_pmv["pmv"] = results["pmv"]
    df_pmv["ppd"] = results["ppd"]

    df = pd.merge(
        df,
        df_pmv[["pmv", "ppd", "pmv_ce", "ppd_ce"]],
        left_index=True,
        right_index=True,
        how="left",
    )

    # merge weather data
    df_meta = pd.read_csv(
        "./v2.1.0/db_metadata.csv",
    )

    # merging database II data with metadata since I need to get station number
    data = pd.merge(df, df_meta, on="building_id", how="left")
    data.timestamp = pd.to_datetime(data.timestamp).dt.date

    # open the weather data file
    df_rmt = pd.read_csv(
        "./v2.1.0/source_data/weather_data_t_rmt.gz", compression="gzip"
    )
    df_rmt.date = pd.to_datetime(df_rmt.date).dt.date

    # merge database II data with weather data
    test = pd.merge(
        data[
            [
                "isd_station",
                "timestamp",
                "contributor",
            ]
        ],
        df_rmt,
        left_on=["isd_station", "timestamp"],
        right_on=["code", "date"],
        how="left",
    )

    df.reset_index(inplace=True)
    test.reset_index(inplace=True)

    # replace old weather data with new one
    df[["rh_out_isd", "t_out_isd"]] = test[["rh_out_isd", "t_out_isd"]].values

    df["t_mot_isd"] = test[["t_rmt"]].values

    # save a new and updated version of the DB II
    df.to_csv("./v2.1.0/db_measurements_v2.1.0.csv.gz", compression="gzip", index=False)
