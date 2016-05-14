#coding=utf-8
#1. Дан список людей, типа Билл, Джон, Карл
#их характеристика это рост и количество детей
#Нужно создать из них список, где-то имя...где-то фамилия...
#Бежим по ним циклом и выводим суммарное кол-во детей, средний рост и кол-во букв А во всех именах.

import numpy as np
import pandas
import itertools

mu, sigma = 170, 80 # mean and standard deviation

s = np.random.normal(mu, sigma, 1000)

kids = []

for x in range(10):
	kids.extend([x]*100)

kids = np.random.permutation(kids)

with open("census-derived-all-first.txt", "r") as  f:
	names = [l.split(" ")[0] for l in f] 

names = np.random.permutation(names)

data = [0, 0, 0]

inp = [x for x in itertools.izip(names, s, kids)]

for name,height,children in inp:
	data[0]+= name.count("A")
	data[1]+= height
	data[2]+= children


data[1] = data[1]/float(len(inp))

print data

def get_a(x):
	return x.count("A")

print reduce(get_a, names)

print sum(kids), sum(height) / float(len(inp)), sum()