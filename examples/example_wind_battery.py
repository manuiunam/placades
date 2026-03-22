#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: Wind turbine with battery storage
Only uses eesyplan facades (no direct solph usage)
"""

from oemof import eesyplan
from oemof.eesyplan import DatetimeIndex

# Create a datetime index for the year 2021 (hourly resolution)
date_time_index = DatetimeIndex(
    freq='1H',
    start='2021-01-01 00:00:00',
    end='2021-01-07 00:00:00'  # 7 days for quick test
)

# Create energy system
energy_system = eesyplan.EnergySystem(
    timeindex=date_time_index,
    timezone='Europe/Berlin'
)

# Create bus (electricity)
bus = eesyplan.Bus(
    label='electricity_bus'
)
energy_system.add(bus)

# Create wind turbine (1 MW capacity, location: Bremen)
wind_turbine = eesyplan.WindTurbine(
    label='wind_turbine_1',
    bus=bus,
    capacity=1e6,  # 1 MW
    longitude=10.0,
    latitude=53.0,
    hub_height=80,
    turbine_type='E-101'  # Enercon E-101
)
energy_system.add(wind_turbine)

# Create electrical storage (battery) - 500 kWh capacity
battery_storage = eesyplan.ElectricalStorage(
    label='battery_storage',
    bus=bus,
    capacity=500e3,  # 500 kWh
    max_input=250e3,  # 250 kW charge power
    max_output=250e3,  # 250 kW discharge power
    efficiency_input=0.95,
    efficiency_output=0.95
)
energy_system.add(battery_storage)

# Create DSO (grid connection)
dso = eesyplan.DSO(
    label='dso',
    bus=bus,
    price=0.30,  # 30 Cent/kWh
    capacity=1e6  # 1 MW grid connection
)
energy_system.add(dso)

# Create electricity demand (example: 100 kW constant)
demand = eesyplan.ElectricityDemand(
    label='demand',
    bus=bus,
    amount=100e3,  # 100 kW
    profile='residential'  # Use standard residential profile
)
energy_system.add(demand)

# Solve the optimization problem
print("Solving optimization problem...")
model = eesyplan.Model(energy_system)
results = model.solve(solver='cbc')

# Process results
results_df = eesyplan.process_results(results)

# Print summary
print("\n" + "="*50)
print("OPTIMIZATION RESULTS")
print("="*50)

# Wind turbine production
wind_production = results_df['wind_turbine_1']['sequences']['P']
print(f"Wind Production: {wind_production.sum()/1e6:.2f} MWh")

# Battery storage behavior
battery_charge = results_df['battery_storage']['sequences']['P']
print(f"Battery Charging: {battery_charge[battery_charge > 0].sum()/1e3:.2f} kWh")
print(f"Battery Discharging: {abs(battery_charge[battery_charge < 0].sum())/1e3:.2f} kWh")

# DSO interaction
dso_flow = results_df['dso']['sequences']['P']
print(f"Grid Import: {dso_flow[dso_flow > 0].sum()/1e3:.2f} kWh")
print(f"Grid Export: {abs(dso_flow[dso_flow < 0].sum())/1e3:.2f} kWh")

# Demand coverage
total_demand = results_df['demand']['sequences']['P'].sum()
print(f"Total Demand: {total_demand/1e3:.2f} kWh")
print(f"Self-consumption rate: {(1 - dso_flow[dso_flow > 0].sum()/total_demand)*100:.1f}%")

print("\nDone! ✅")
