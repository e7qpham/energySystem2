import pypsa 
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pypsa.plot import add_legend_patches


# create a new pypsa network
n = pypsa.Network()


# add bus for each country to the network
n.add("Bus", "BR", y=-22.83014, x=-43.11040, v_nom=380, carrier="AC")
n.add("Bus", "BO", y=-15.91405, x=-68.16363, v_nom=400, carrier="AC")
n.add("Bus", "PR", y=-23.25673, x=-58.49566, v_nom=380, carrier="AC")
n.buses


# t/MWh thermal
emissions = dict(
    Coal=0.34,
    Gas=0.2,
    Hydro=0,
)
n.madd(
    "Carrier",
    ["Coal", "Wind and Solar", "Gas", "Hydro"],
    co2_emissions=emissions,
    color=["grey", "dodgerblue", "indianred", "aquamarine"],
)
# data of power plant capacities in MW
power_plants = {
    "BR": {"Coal": 52000, "Wind and Solar": 8000, "Gas": 12000},
    "BO": {"Hydro": 2000, "Gas": 1000},
    "PR": {"Hydro": 1500}
}
# data of electrical load in MW
loads = {
    "BR": 65000,
    "BO": 1100,
    "PR": 900
}
# data of marginal costs, €/MWh
marginal_costs = {
    "Brazil": {"Coal": 35, "Wind and Solar": 0, "Gas":70},
    "Bolivia": {"Hydro": 4, "Gas": 65},
    "Paraguay": {"Hydro": 6}
}


# add generators for the power plants in Brazil
for tech, p_nom in power_plants["BR"].items():
    # retrieve the marginal cost for the technology
    cost = marginal_costs["Brazil"][tech]
    # add generators
    n.add(
        "Generator",
        f"BR {tech}",
        bus = "BR",
        carrier=tech,
        p_nom=p_nom, #MW
        marginal_cost = cost,
    )
# add generators for the power plants in Bolivia
for tech, p_nom in power_plants["BO"].items():
    n.add(
        "Generator",
        f"BO {tech}",
        bus = "BO",
        carrier=tech,
        p_nom=p_nom, #MW
        marginal_cost = marginal_costs["Bolivia"][tech],
    )
# add generators for the power plants in Paraguay
n.add(
    "Generator",
    "PR Hydro",
    bus = "PR",
    carrier="Hydro",
    p_nom=1500, #MW
    marginal_cost = 6,
)
# show all generators
n.generators


# add loads in Brazil
n.add(
    "Load",
    "BR electricity demand",
    bus="BR",
    p_set=loads["BR"],
    carrier="electricity",
)
# add loads in Bolivia
n.add(
    "Load",
    "BO electricity demand",
    bus="BO",
    p_set=loads["BO"],
    carrier="electricity",
)
# add loads in Paraguay
n.add(
    "Load",
    "PR electricity demand",
    bus="PR",
    p_set=loads["PR"],
    carrier="electricity",
)
# show all loads
n.loads


# add the connection between Brazil and Bolivia with a 600 MW line
n.add(
    "Line",
    "BR-BO",
    bus0="BR",
    bus1="BO",
    s_nom=600,
    x=1,
    r=1,
)
# add the connection between Bolivia and Paraguay with a 50 MW line
n.add(
    "Line",
    "BO-PR",
    bus0="BO",
    bus1="PR",
    s_nom=50,
    x=1,
    r=1,
)
# add the connection between Brazil and Paraguay with a 200 MW line
n.add(
    "Line",
    "BR-PR",
    bus0="BR",
    bus1="PR",
    s_nom=200,
    x=1,
    r=1,
)
# show all transmission lines
n.lines


# solve the prepared network with glpk solver
n.optimize(solver_name="glpk")


# retrieve the dispatch of the generators in MW
n.generators_t.p
# retrieve the power flow in transmission lines from bus0 to bus1 in MW
n.lines_t.p0
# retrieve the power flow in transmission lines from bus1 to bus0 in MW
n.lines_t.p1
# retrieve the shadow price in €/MWh
n.buses_t.marginal_price
# retrieve the objective function in €/MWh
n.objective


# plot a map (include country borders) showing the dispatch per technology for each node
## at first, group the dispatch of each generator by the bus and carrier
s = n.generators_t.p.loc["now"].groupby([n.generators.bus, n.generators.carrier]).sum()
## plotting
fig, ax = plt.subplots(figsize=(12,15), subplot_kw={"projection":ccrs.PlateCarree()})
carriers = n.generators.carrier.unique()
colors = ["grey", "dodgerblue", "indianred", "aquamarine"]
n.madd("Carrier", carriers, color=colors)

n.plot(
    ax=ax,
    bus_sizes=s/3000,
    #bus_colors="orange",
    bus_alpha=0.7,
    color_geomap=True,
    line_colors=n.lines_t.p0.mean(),
    #line_widths=n.lines.s_nom,
    line_widths=2
)

add_legend_patches(
    ax, colors, carriers, legend_kw=dict(frameon=False, bbox_to_anchor=(0, 1))
)







