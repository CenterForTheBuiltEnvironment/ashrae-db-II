import matplotlib as mpl

mpl.use("Qt5Agg")  # or can use 'TkAgg', whatever you have/prefer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pythermalcomfort.models import pmv_ppd, set_tmp
from pythermalcomfort.utilities import v_relative, clo_dynamic

sns.set_style("whitegrid")
plt.rc("axes.spines", top=False, right=False, left=False)
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.figsize"] = (7, 3)

# # open Tom's csv file
# df = pd.read_csv(
#     "./data/db_measurements_v21.csv", low_memory=False
# )
# df.to_csv("./data/db_measurements_v21.csv.gzip", compression="gzip", index=False)

df = pd.read_csv(
    "./data/db_measurements_v21.csv.gzip",
    low_memory=False,
    compression="gzip",
)

# check data types
for col in df.columns[[3, 36, 37]]:
    print(set(type(x) for x in df[col].unique()))

# calculate relative air speed and dynamic clothing
v_rel = v_relative(df["vel"], df["met"])
clo_d = clo_dynamic(df["clo"], df["met"])
df["vr"] = v_rel
df["clo_d"] = clo_d

print(df[["ta", "tr", "rh", "met", "vel", "clo"]].describe().to_markdown())

# exclude some values otherwise the code breaks
df_pmv = df.dropna(subset=["ta", "tr", "rh", "clo_d", "vr", "met", "vel", "clo"])
df_pmv = df_pmv[df_pmv["vel"] > 0.01]  # todo fix this issue
df_pmv = df_pmv[df_pmv["met"] > 0.01]  # todo fix this issue
df_pmv = df_pmv[df_pmv["clo"] > 0.01]  # todo fix this issue
df_pmv = df_pmv[df_pmv["clo"] < 3]  # todo fix this issue
df_pmv = df_pmv[df_pmv["met"] < 4]  # todo fix this issue
df_pmv = df_pmv[df_pmv["vel"] < 4]  # todo fix this issue
df_pmv = df_pmv[df_pmv["tr"] < 50]  # todo fix this issue
df_pmv = df_pmv[df_pmv["ta"] < 40]  # todo fix this issue
df_pmv = df_pmv[df_pmv["ta"] > 10]  # todo fix this issue

# calculate SET temperature
df_pmv["set_py"] = set_tmp(
    tdb=df_pmv.ta,
    tr=df_pmv.tr,
    v=df_pmv.vel,
    rh=df_pmv.rh,
    met=df_pmv.met,
    clo=df_pmv.clo,
)

db_II = pd.merge(df, df_pmv[["set_py"]], left_index=True, right_index=True, how="left")

# calculate different PMV indices
results = pmv_ppd(
    df_pmv["ta"],
    df_pmv["tr"],
    df_pmv["vr"],
    df_pmv["rh"],
    df_pmv["met"],
    df_pmv["clo_d"],
    0,
    "ashrae",
)

df_pmv["pmv_ashrae"] = results["pmv"]
df_pmv["ppd_ashrae"] = results["ppd"]

results = pmv_ppd(
    df_pmv["ta"],
    df_pmv["tr"],
    df_pmv["vr"],
    df_pmv["rh"],
    df_pmv["met"],
    df_pmv["clo_d"],
    0,
    "iso",
)

df_pmv["pmv_iso"] = results["pmv"]
df_pmv["ppd_iso"] = results["ppd"]

results = pmv_ppd(
    df_pmv["ta"],
    df_pmv["tr"],
    df_pmv["vel"],
    df_pmv["rh"],
    df_pmv["met"],
    df_pmv["clo"],
    0,
    "iso",
)

df_pmv["pmv_no_adj"] = results["pmv"]
df_pmv["ppd_no_adj"] = results["ppd"]

db_II = pd.merge(
    db_II,
    df_pmv[["pmv_iso", "ppd_iso", "pmv_ashrae", "ppd_ashrae", "pmv_no_adj"]],
    left_index=True,
    right_index=True,
    how="left",
)

f, axs = plt.subplots(1, 2, sharey=True, sharex=True, constrained_layout=True)
sc = axs[0].scatter(x="pmv_ashrae", y="pmv", data=db_II, s=1, alpha=0.3)
axs[1].scatter(x="pmv_iso", y="pmv", data=db_II, s=1, alpha=0.3)
axs[0].plot([-4, 4], [-4, 4])
axs[1].plot([-4, 4], [-4, 4])
axs[0].set(ylabel="PMV DB II", xlabel="PMV ASHRAE")
axs[1].set(xlabel="PMV ISO")
# f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
# plt.colorbar(sc, cax=cax)
plt.show()

f, axs = plt.subplots(1, 2, sharey=True, sharex=True, constrained_layout=True)
sc = axs[0].scatter(x="pmv_no_adj", y="pmv", data=db_II, s=1, alpha=0.3)
axs[1].scatter(x="pmv_iso", y="pmv", data=db_II, s=1, alpha=0.3)
axs[0].plot([-4, 4], [-4, 4])
axs[1].plot([-4, 4], [-4, 4])
axs[0].set(ylabel="PMV DB II", xlabel="PMV NO CLO, VEL ADJUSTMENT")
axs[1].set(xlabel="PMV ISO")
# f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
# plt.colorbar(sc, cax=cax)
plt.show()

f, axs = plt.subplots(1, 1, sharey=True, sharex=True, constrained_layout=True)
sc = axs.scatter(x="set", y="asv", data=db_II, s=5, alpha=0.3)
axs.set(ylabel="TSV", xlabel="set")
# f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
# plt.colorbar(sc, cax=cax)
plt.show()

f, axs = plt.subplots(1, 1, sharey=True, sharex=True, constrained_layout=True)
sc = axs.scatter(x="set_py", y="set", data=db_II, s=5, alpha=0.3)
axs.set(ylabel="SET DB II", xlabel="SET pythermalcomfort")
axs.plot([10, 40], [10, 40], c="k")
inset_ax = f.add_axes([0.65, 0.25, 0.3, 0.2])
inset_ax.hist(db_II.set - db_II.set_py, 200)
inset_ax.set(title="Delta", xlim=(-1, 3), yticks=[])
# f.subplots_adjust(bottom=0.1, top=1, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cax = f.add_axes([0.83, 0.1, 0.02, 0.8])
# plt.colorbar(sc, cax=cax)

plt.figure()
sns.boxenplot(x="thermal_preference", y="ta", data=df.sort_values("thermal_preference"))
plt.tight_layout()

plt.figure()
sns.boxenplot(
    x="thermal_preference", y="set", data=df.sort_values("thermal_preference")
)
plt.tight_layout()

plt.figure()
sns.boxenplot(
    x="thermal_preference", y="asv", data=df.sort_values("thermal_preference")
)
plt.tight_layout()

plt.figure()
sns.boxenplot(
    x="air_movement_preference", y="vel", data=df.sort_values("thermal_preference")
)
plt.tight_layout()
