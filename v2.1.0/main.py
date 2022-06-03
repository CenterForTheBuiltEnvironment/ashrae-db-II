import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pythermalcomfort.models import pmv_ppd, set_tmp
from pythermalcomfort.utilities import (
    v_relative,
    clo_dynamic,
    running_mean_outdoor_temperature,
)


def data_validation(data):
    import matplotlib as mpl

    mpl.use("Qt5Agg")  # or can use 'TkAgg', whatever you have/prefer
    import matplotlib.pyplot as plt
    import seaborn as sns

    df_meta = pd.read_csv(
        "./v2.1.0/db_metadata.csv",
    )

    data = pd.merge(data, df_meta, on="building_id")

    print(data[["ta", "tr", "rh", "met", "vel", "clo"]].describe().to_markdown())

    sns.set_style("whitegrid")
    plt.rc("axes.spines", top=False, right=False, left=False)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["figure.figsize"] = (7, 3)

    # check for anomalies in the thermal_sensation data
    for id in data.contributor.unique():
        df_building = data.query("contributor == @id")
        # sns.regplot(x="ta", y="thermal_sensation", data=df_building)
        if df_building.dropna(subset="thermal_preference").shape[0] == 0:
            continue
        plt.figure()
        sns.boxplot(
            x="thermal_preference",
            y="thermal_sensation",
            data=df_building.sort_values("thermal_preference"),
        )
        plt.title(id)
        plt.tight_layout()

    # check data types
    for col in data.columns[[3, 36, 37]]:
        print(col, set(type(x) for x in data[col].unique()))

    f, axs = plt.subplots(1, 2, sharey=True, sharex=True, constrained_layout=True)
    sc = axs[0].scatter(x="pmv_ashrae", y="pmv", data=data, s=1, alpha=0.3)
    axs[1].scatter(x="pmv_iso", y="pmv", data=data, s=1, alpha=0.3)
    axs[0].plot([-4, 4], [-4, 4])
    axs[1].plot([-4, 4], [-4, 4])
    axs[0].set(ylabel="PMV DB II", xlabel="PMV ASHRAE")
    axs[1].set(xlabel="PMV ISO")
    # f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
    # cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
    # plt.colorbar(sc, cax=cax)
    plt.show()

    f, axs = plt.subplots(1, 2, sharey=True, sharex=True, constrained_layout=True)
    sc = axs[0].scatter(x="pmv_no_adj", y="pmv", data=data, s=1, alpha=0.3)
    axs[1].scatter(x="pmv_iso", y="pmv", data=data, s=1, alpha=0.3)
    axs[0].plot([-4, 4], [-4, 4])
    axs[1].plot([-4, 4], [-4, 4])
    axs[0].set(ylabel="PMV DB II", xlabel="PMV NO CLO, VEL ADJUSTMENT")
    axs[1].set(xlabel="PMV ISO")
    # f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
    # cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
    # plt.colorbar(sc, cax=cax)
    plt.show()

    f, axs = plt.subplots(1, 1, sharey=True, sharex=True, constrained_layout=True)
    sc = axs.scatter(x="set", y="asv", data=data, s=5, alpha=0.3)
    axs.set(ylabel="TSV", xlabel="set")
    # f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
    # cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
    # plt.colorbar(sc, cax=cax)
    plt.show()

    f, axs = plt.subplots(1, 1, sharey=True, sharex=True, constrained_layout=True)
    sc = axs.scatter(x="set_py", y="set", data=data, s=5, alpha=0.3)
    axs.set(ylabel="SET DB II", xlabel="SET pythermalcomfort")
    axs.plot([10, 40], [10, 40], c="k")
    inset_ax = f.add_axes([0.65, 0.25, 0.3, 0.2])
    inset_ax.hist(data.set - data.set_py, 200)
    inset_ax.set(title="Delta", xlim=(-1, 3), yticks=[])
    # f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
    # cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
    # plt.colorbar(sc, cax=cax)

    plt.figure()
    sns.boxenplot(
        x="thermal_preference", y="ta", data=data.sort_values("thermal_preference")
    )
    plt.tight_layout()

    plt.figure()
    sns.boxenplot(
        x="thermal_preference", y="set", data=data.sort_values("thermal_preference")
    )
    plt.tight_layout()

    plt.figure()
    sns.boxenplot(
        x="thermal_preference", y="asv", data=data.sort_values("thermal_preference")
    )
    plt.tight_layout()

    plt.figure()
    sns.boxenplot(
        x="air_movement_preference",
        y="vel",
        data=data.sort_values("thermal_preference"),
    )
    plt.tight_layout()


def calculate_running_mean_outdoor_temperature():
    """This function calculates the running mean outdoor temperature using
    pythermalcomfort function running_mean_outdoor_temperature.

    It uses the default values for alpha and it calculates the value
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
        "./v2.1.0/db_measurements_v2.0.1.csv.gz",
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

    # calculate weather data
    df_meta = pd.read_csv(
        "./v2.1.0/db_metadata.csv",
    )

    # merging database II data with metadata since I need to get station number
    data = pd.merge(df, df_meta, on="building_id", how="left")
    data.timestamp = pd.to_datetime(data.timestamp).dt.date

    # open the weather data file
    df_rmt = pd.read_csv("./v2.1.0/weather_data_t_rmt.gz", compression="gzip")
    df_rmt.date = pd.to_datetime(df_rmt.date).dt.date

    # merge database II data with weather data
    test = pd.merge(
        data[
            [
                "isd_station",
                "timestamp",
                "t_mot_isd",
                "rh_out_isd",
                "t_out_isd",
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

    # plt.figure()
    # plt.scatter(df.t_out_isd, test.t_out_isd_y)
    # plt.plot([-30, 40], [-30, 40], c="k")
    # plt.show()
    # plt.figure()
    # plt.scatter(df.rh_out_isd, test.rh_out_isd_y)
    # plt.plot([10, 100], [10, 100], c="k")
    # plt.show()
    # plt.figure()
    # plt.scatter(test.t_mot_isd, test.t_rmt)
    # plt.plot([-30, 40], [-30, 40], c="k")
    # plt.show()
    #
    # test["delta_t_out"] = df.t_out_isd - test.t_out_isd_y
    # print(
    #     test.loc[
    #         test["delta_t_out"].abs() > 1,
    #         ["isd_station", "date", "delta_t_out", "t_out_isd_x", "t_out_isd_y"],
    #     ].to_markdown()
    # )
    # print(
    #     test.loc[test["delta_t_out"].abs() > 1]
    #     .groupby(["isd_station", "date"])[["delta_t_out", "t_out_isd_x", "t_out_isd_y"]]
    #     .mean()
    #     .to_markdown()
    # )
    # df_rmt.query(
    #     "code == '967470-99999' & date > datetime.datetime(1993,5,3).date() & date < datetime.datetime(1993,5,5).date()"
    # )
    # df_rmt = pd.read_csv("./v2.1.0/weather_data.gz", compression="gzip")
    # print(
    #     df_rmt.query(
    #         "code == '967470-99999' & date == '1993-05-05T00:00:00Z'"
    #     ).to_markdown()
    # )
    #
    # df_201 = pd.read_csv(
    #     "./v2.1.0/db_measurements_v2.0.1.csv.gz",
    #     low_memory=False,
    #     compression="gzip",
    # )
    # data_201 = pd.merge(df_201, df_meta, on="building_id", how="left")
    # print(
    #     data_201.query(
    #         "isd_station == '967470-99999' & timestamp == '1993-05-05T00:00:00Z'"
    #     )[["isd_station", "timestamp", "t_out_isd"]]
    #     .head()
    #     .to_markdown()
    # )
    #
    # print(df_rmt.query("code == '967470-99999'").to_markdown())
    #
    # test[test["delta_t_out"].abs() > 1].contributor.unique()
    # test[test["delta_t_out"].abs() > 1].date.unique()
    #
    # test["delta_rh_out"] = df.rh_out_isd - test.rh_out_isd_y
    # print(test.loc[test["delta_rh_out"].abs() > 1, ["rh_out_isd_x", "rh_out_isd_y"]])
    # test[test["delta_rh_out"].abs() > 1].contributor.unique()

    # replace old weather data with new one
    df[["t_mot_isd", "rh_out_isd", "t_out_isd"]] = test[
        ["t_rmt", "rh_out_isd_y", "t_out_isd_y"]
    ].values

    # save a new and updated version of the DB II
    df.to_csv("./v2.1.0/db_measurements_v2.1.0.csv.gz", compression="gzip", index=False)
