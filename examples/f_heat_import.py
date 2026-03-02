from pathlib import Path

from matplotlib import pyplot as plt

from oemof.eesyplan.importer.heat_demand import import_heat_demand_f_heat


df = import_heat_demand_f_heat(
    Path(Path.home(), "Downloads", "Uebung_FHeat_Barntrup.zip"), "Netz1"
)
df.plot()
plt.show()
