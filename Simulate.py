import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import random
import copy
import time

from models.base import Grid
from models.base import Policy

#This class caters to just simulation. It required a Policy object and Grid object as input
class Simulate():
	def __init__(self, transmission_prob, individual_types,grid,policy):
		self.individual_types=individual_types		#The possible types of agents
		self.grid=grid 								#Grid object				#
		self.transmission_prob=transmission_prob    #transmission probabilities between states
		self.day=0 									#Day
		self.policy=policy 							#Policy object
		self.total_infected_days=0 					#Variable storing the cumilative sum of infected days
		self.global_state='Normal' 					#Gloabl policy state.  eg : Lockdown, Socially Distanced.

	#Creates a deep copy of self to be used in simualation
	def copy_cstr(self):
		gridtable=copy.deepcopy(self.grid.grid)
		grid=Grid.Grid(gridtable,self.individual_types)
		if self.policy.policy_name=="Vaccinate":
			policy=Policy.Vaccinate_block(grid, self.individual_types,self.policy.block_size,self.policy.cost,copy.deepcopy(self.policy.valid_actions))
		if self.policy.policy_name=="Quarantine":
			policy=Policy.Vaccinate_block(grid, self.individual_types,self.policy.max_quarantine_distance,self.policy.cost,copy.deepcopy(self.policy.valid_actions))
		temp_obj= Simulate(self.transmission_prob,self.individual_types,grid,policy)

		for i in range(grid.grid_size):
			for j in range(grid.grid_size):
				temp_obj.grid.agent_grid[i][j].policy_state=copy.deepcopy(self.grid.agent_grid[i][j].policy_state)

		return temp_obj


	#simulate one day given an action that is taken according to policy
	def simulate_day(self,action_no):
		no_quarantined=None
		if self.policy!=None:
			no_quarantined = self.policy.do_action(self.grid,action_no)
		grid=self.grid
		new_grid=copy.deepcopy(grid.grid)

		for i in range(grid.grid_size):
			for j in range(grid.grid_size):
				cur_agent=grid.agent_grid[i][j]

				conversion_type=self.find_conversion_type(cur_agent)
				new_grid[i][j]=grid.type_to_number[conversion_type]
				
		for i in range(grid.grid_size):
			for j in range(grid.grid_size):
				cur_type=grid.number_to_type[new_grid[i][j]]
				grid.convert_type(i,j,cur_type)

		self.day+=1
		grid.update_timeseries()
		if 'Infected' in self.individual_types:
			self.total_infected_days+=self.grid.current_types_pop['Infected']
		return no_quarantined, self.grid.current_types_pop['Infected']

	#Find new state of agent.  Eg 'Infected' -> 'Recovered'
	def find_conversion_type(self,agent):
		my_type=agent.individual_type
		r=random.random()
		p=0
		for t in self.individual_types:
			p+=self.transmission_prob[my_type][t](self.day,self.global_state,agent,agent.neighbours)
			if r<p:
				return t

		return my_type

	#Simulate multiple days without doing any action
	def simulate_days(self,n):
		for i in range(n):
			self.simulate_day(-1)

	#Simulate till the end of pandemic.
	def simulate_till_end(self, reward_fn):
		no_infected=self.grid.current_types_pop['Infected']+self.grid.current_types_pop['Asymptomatic']+self.grid.current_types_pop['Exposed']
		total_infected_days=0
		while(no_infected>0):
			action_no=random.choice(self.policy.valid_actions)

			self.simulate_day(action_no)
			no_infected=self.grid.current_types_pop['Infected']+self.grid.current_types_pop['Asymptomatic']+self.grid.current_types_pop['Exposed']
			total_infected_days+=no_infected

		return reward_fn(self.day,total_infected_days)

