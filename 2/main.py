# coding=utf-8

# 1-я часть: Создать базу данных писем
# Шаблон письма, как служба поддержки отвечает на заявки.

# Типа Здравствуйте %user%! Ваша заявка %№% принята к исполнению %date% и бла бла бла...

# 2-я часть: Создадим словарь заявок
# имя человека, что он там писал и время создания заявки (либо в строке либо надо посмотреть как делается дата)

# 3-я часть: В цикле бежим по этим заявкам и создаем новый словарь с ответами пользователям 

# 4-я часть: если пишет человек из черного списка, то ему не отвечать

# Import smtplib for the actual sending function

import datetime
import string
import random
import numpy as np

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

def random_text(size=12, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


with open("../1/census-derived-all-first.txt", "r") as  f:
	names = [l.split(" ")[0] for l in f] 

names = np.random.permutation(names)

d1 = datetime.datetime.strptime('1/1/2008 1:30 PM', '%m/%d/%Y %I:%M %p')
d2 = datetime.datetime.strptime('1/1/2009 4:50 AM', '%m/%d/%Y %I:%M %p')

d = {}

for name in names:
	d[name] = [random_text(), random_date(d1,d2)]

bl = names[1:5]

print bl

responses = {}

n = 1

for key in d:
	if key not in bl:

		strg = 'Здравствуйте {user} Ваша заявка {n} принята к исполнению. Текст заявки {text}'
		text, date = d[key]
		responses[key] = strg.format(user=key, n=n, text=text)
		n+=1


print [responses.get(name) for name in bl]

print [responses.get(name) for name in names[6:10]]

