import pandas as pd
from oemof.solph import Bus

from oemof.eesyplan import EnergySystem
from oemof.eesyplan import HeatPump
from oemof.eesyplan import Project
from oemof.eesyplan import optimise


def test_heat_pump():
    number = 10
    es = EnergySystem(2023, number=number)
    el_bus = Bus(label="electricity", balanced=False)
    ambient_bus = Bus(label="ambient", balanced=False)
    heat_bus = Bus(label="heat", balanced=False)
    es.add(el_bus, ambient_bus, heat_bus)
    heat_pump = HeatPump(
        name="air_source_heat_pump",
        bus_in_electricity=el_bus,
        bus_in_heat=ambient_bus,
        bus_out_heat=heat_bus,
        installed_capacity=15,
        opex_var=-0.1,
        cop=[3.5, 3.2] * 5,
        project_data=Project(
            name="Project_X",
            lifetime=20,
            tax=0,
            discount_factor=0.01,
        ),
    )
    es.add(heat_pump)
    results = optimise(es)
    flows = results["flow"]

    energy = heat_pump.installed_capacity * number

    assert (
        round(
            (
                pd.Series(heat_pump.cop)
                * flows["electricity"].reset_index(drop=True).squeeze()
            ).sum(),
            5,
        )
        == energy
    )

    assert flows["air_source_heat_pump"].sum().iloc[0] == energy
    assert (
        round((flows["electricity"].sum() + flows["ambient"].sum()).iloc[0], 5)
        == energy
    )
