import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import random
import copy
import Grid
import Simulate
import time

def normal_spread():

	#Function determining the probability of infecting neighbour
	def p_infection(day,global_state,my_agent,neighbour_agents):  # probability of infectiong neighbour
		p_inf=0.5
		p_not_inf=1
		for nbr_agent in neighbour_agents:
			if nbr_agent.individual_type in ['Infected','Asymptomatic'] and not nbr_agent.policy_state['quarantined']:
				p_not_inf*=(1-p_inf)
		#print(1-p_not_inf)
		return 1 - p_not_inf

	#Standard fixed probability of changing state
	def p_standard(p):
		def p_fn(day,global_state,a1,nbrs):
			return p
		return p_fn


	#Define all possible states and corresponding colors
	individual_types=['Susceptible','Infected','Recovered','Vaccinated','Asymptomatic','Exposed','Asymptomatic Recovered']
	color_list=['white', 'black','red','blue','blue','grey','pink']


	transmission_prob={}
	for t in individual_types:
		transmission_prob[t]={}

	for t1 in individual_types:
		for t2 in individual_types:
			transmission_prob[t1][t2]=p_standard(0)

	#define the transmission probabilities between states
	transmission_prob['Susceptible']['Exposed']= p_infection
	transmission_prob['Exposed']['Infected']= p_standard(0.5)
	transmission_prob['Exposed']['Asymptomatic']= p_standard(0.3)
	transmission_prob['Infected']['Recovered']= p_standard(0.2)
	transmission_prob['Asymptomatic']['Asymptomatic Recovered']= p_standard(0.2)
	transmission_prob['Recovered']['Susceptible']= p_standard(0)

	#Initialise grid and agents with states
	gridtable =np.zeros((50,50))
	gridtable[35][6]=1    #Infected = individual_types[1] at (35,6)
	gridtable[22][43]=1
	gridtable[7][2]=1
	gridtable[15][2]=1
	grid=Grid.Grid(gridtable,individual_types)
	#policy=Policy.Quarantine_area(grid, individual_types, 4, 0)
	policy=None
	sim_obj= Simulate.Simulate(transmission_prob,individual_types,grid,policy)
	
	#define reward function to be maximised for given policy
	def reward_fn(days,no_infected):
		return -days

	#Simulate n days of disease spread without policy intervention 
	n_days=10
	sim_obj.simulate_days(n_days)

	#sim_obj.simulate_till_end(reward_fn)
	sim_obj.grid.animate(False,color_list,0.3)  #animate n_days of disease spread
	sim_obj.grid.plot_time_series()   			#plot time series of individual_types(Infected, recovered...)

def co_pandemic_spread():

	def p_infection(day,global_state,my_agent,neighbour_agents):  # probability of infectiong neighbour

		p_inf=0.4
		p_not_inf=1
		for nbr_agent in neighbour_agents:
			if nbr_agent.individual_type in ['Infected','Asymptomatic'] and not nbr_agent.policy_state['quarantined']:
				p_not_inf*=(1-p_inf)

		return 1 - p_not_inf

	def p_infection_flu(day,global_state,my_agent,neighbour_agents):  # probability of infectiong neighbour

		p_inf=0.2
		p_not_inf=1
		for nbr_agent in neighbour_agents:
			if nbr_agent.individual_type in ['Flu'] and not nbr_agent.policy_state['quarantined']:
				p_not_inf*=(1-p_inf)

		return 1 - p_not_inf


	def p_standard(p):
		def p_fn(day,global_state,a1,nbrs):
			return p
		return p_fn


	individual_types=['Susceptible','Infected','Recovered','Flu','Flu Recovered','grey']
	color_list=['white', 'black','red','blue','yellow','grey']

	transmission_prob={}
	for t in individual_types:
		transmission_prob[t]={}

	for t1 in individual_types:
		for t2 in individual_types:
			transmission_prob[t1][t2]=p_standard(0)

	transmission_prob['Susceptible']['Infected']= p_infection
	transmission_prob['Susceptible']['Flu']= p_infection_flu
	transmission_prob['Flu']['Infected']= p_infection
	transmission_prob['Flu']['Flu Recovered']= p_standard(0.1)
	transmission_prob['Flu Recovered']['Infected']= p_infection
	transmission_prob['Infected']['Recovered']= p_standard(0.2)
	transmission_prob['Recovered']['Susceptible']= p_standard(0)

	gridtable =np.zeros((50,50))

	for i in range(6):
		x= random.randint(0,49)
		y= random.randint(0,49)
		gridtable[x][y]=1
	for i in range(4):
		x= random.randint(0,49)
		y= random.randint(0,49)
		gridtable[x][y]=3

	grid=Grid.Grid(gridtable,individual_types)
	#policy=Policy.Vaccinate_block(grid, individual_types,1,0)
	policy=None
	sim_obj= Simulate.Simulate(transmission_prob,individual_types,grid,policy)
	
	def reward_fn(days,no_infected):
		return -days

	sim_obj.simulate_days(20)

	#sim_obj.simulate_till_end(reward_fn)
	sim_obj.grid.animate(False,color_list,0.3)
	sim_obj.grid.plot_time_series()

#normal_spread()
co_pandemic_spread()