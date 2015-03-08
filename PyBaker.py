#!/usr/bin/env python
import argparse
import numpy as np
import json

##-------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
  description='''calculates the amount of each ingredient to use in a starter
                 based dough.  The mandatory arguments are the mass of your 
                 starter, the hydration of the starter (usually around 1.0) and
                 the dough to be made  (either sourdough or sweetdough).  The
                 sour factor is an optional argument which indicates how much
                 the starter should be diluted with flour and water/milk.''',
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
parser.add_argument(
  'TotalMass',
  metavar='TotalMass',
  type=float,
  help='''the mass of final dough'''
  ) 
parser.add_argument(
  'Starter',
  metavar='Starter',
  type=float,
  help='''hydration of the starter.  This is given as a bakers ratio which is 
          defined as the mass of the ingedient (water in this case) divided 
          by the mass of flour.  A typical starter has a hydration
          of 1.0'''
  ) 
parser.add_argument(
  'Name',
  metavar='Name',
  type=str,
  choices=['overnight','sour','sweet','bagel'],
  help='''The name of the dough you are making'''
  ) 

args = parser.parse_args()
total_mass = args.TotalMass
starter_hydration = args.Starter
name = args.Name

##-------------------------------------------------------------------------------
## Recipes

egg_density = 50.0 # grams per egg
salt_density = 3.33 # grams per tsp
butter_density = 113 # grams per stick
flour_density = 125 # grams per cup
water_density = 236 # grams per cup
milk_density = 234 # grams per cup
sugar_density = 200 # grams per cup

converter_file = open('converter.json','r')
converter = json.load(converter_file)
recipes_file = open('recipes.json','r')
recipes = json.load(recipes_file)

##------------------------------------------------------------------------------
def ingredient_mass(total_mass,recipe,starter_hydration):
  hydration = recipe['hydration']
  sour_factor = recipe['sour_factor']
  ingredient_no = len(recipe['ingredients']) + 3
  ingredients = recipe['ingredients'].keys()

  data = np.zeros(ingredient_no)
  data[2] = total_mass 

  ingredient_matrix = np.zeros((ingredient_no,ingredient_no))
  ingredient_matrix[0,0] = 1.0/(sour_factor*(hydration + 1.0)) - 1.0/(starter_hydration + 1.0)
  ingredient_matrix[0,1] = -1.0
  ingredient_matrix[1,0] = ((1.0/sour_factor) - 1.0)
  ingredient_matrix[1,1] = -1.0
  ingredient_matrix[1,2] = -1.0
  ingredient_matrix[2,:] = np.ones(ingredient_no)

  for idx,value in enumerate(recipe['ingredients'].itervalues()):  
    ingredient_line = np.zeros(ingredient_no)
    baker_weight = value
    ingredient_matrix[idx+3,0] = baker_weight / (1.0 + starter_hydration) 
    ingredient_matrix[idx+3,1] = baker_weight
    ingredient_matrix[idx+3,idx+3] = -1.0

  ingredient_mass = np.linalg.solve(ingredient_matrix,data)

  return (ingredients,ingredient_mass)

##-------------------------------------------------------------------------------
def print_ingredient(name,grams):
  conv = converter[name]['value']
  units = converter[name]['unit']
  string = '  %s: %g grams (%g %s)' % (name,
                                       grams,
                                       grams*conv,
                                       units)
  print(string)
                               
##-------------------------------------------------------------------------------
def print_all_ingredients(ingredients,mass):
  print_ingredient('starter',mass[0])
  print_ingredient('flour',mass[1])
  print_ingredient('water',mass[2])
  for itr,key in enumerate(ingredients):
    print_ingredient(key,mass[itr+3])


ingredients,mass = ingredient_mass(total_mass,recipes[name],starter_hydration)
print_all_ingredients(ingredients,mass)


