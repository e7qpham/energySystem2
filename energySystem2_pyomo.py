import pyomo.environ as pe
import pandas as pd 
import numpy as np 


# data of generation capacities in MW
capacities = {
    "Brazil": {"Coal": 52000, "Wind and Solar": 8000, "Gas": 12000},
    "Bolivia": {"Hydro": 2000, "Gas": 1000},
    "Paraguay": {"Hydro": 1500}
}


# data of transmission capacity in MW
transmission = {"Brazil-Bolivia": 600, "Bolivia-Paraguay": 50, "Brazil-Paraguay": 200} 


# data of electricity demand in MW
loads = {"Brazil": 65000, "Bolivia": 1100, "Paraguay": 900} # MW


# data of marginal costs, €/MWh
marginal_costs = {
    "Brazil": {"Coal": 35, "Wind and Solar": 0, "Gas":70},
    "Bolivia": {"Hydro": 4, "Gas": 65},
    "Paraguay": {"Hydro": 6}
}


# create a fresh model
m = pe.ConcreteModel()
# dual values or shadow prices
m.dual = pe.Suffix(direction=pe.Suffix.IMPORT)


# create set for countries
m.countries = pe.Set(initialize=loads.keys())
m.countries.pprint()


# create set for technologies
technologies = list(capacities["Brazil"].keys() | capacities["Bolivia"].keys() | capacities["Paraguay"].keys())
m.technologies = pe.Set(initialize=technologies)


# create decision variables for the generator dispatch
m.g = pe.Var(m.countries, m.technologies, within=pe.NonNegativeReals)
m.g.pprint()


# create set for transmission lines
m.transmission_lines = pe.Set(initialize=transmission.keys())
m.technologies.pprint()


# create variable for transmission flow
m.f = pe.Var(m.transmission_lines, within=pe.Reals)
m.f.pprint()


# the objective function for minimising the operational costs
m.cost = pe.Objective(expr=sum(marginal_costs[c][s] * m.g[c, s] 
                               for c in m.countries 
                               for s in capacities[c]
                               if s in marginal_costs[c]))
m.cost.pprint()


# build the capacity limits of the generators
@m.Constraint(m.countries, m.technologies)
def generator_limit(m, c, s):
    return m.g[c, s] <= capacities[c].get(s, 0)
m.generator_limit.pprint()


# build the Kirchhoff Laws constraints
@m.Constraint(m.countries)
def kcl(m, c):
    sign = -1 if c == "Paraguay" else 1 # minimal incidence matrix
    return sum(m.g[c, s] for s in m.technologies) - sign * m.f == loads[c]
m.kcl.pprint()


# constrain the transmission flows to the line's rated capacity
@m.Constraint(m.transmission_lines)
def transmission_limit(m, line):
    return (-transmission[line], m.f[line], transmission[line])
m.transmission_limit.pprint()


# solve the optimisation model with glpk solver
pe.SolverFactory("glpk").solve(m).write()