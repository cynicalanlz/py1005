import random
from collections import Counter

with open("data.csv", "w") as f:

	nums = [random.randint(1,n) for n in list(xrange(100))[1:]]

	nums = map(str, nums)

	f.write(';'.join(nums))


with open("data.csv", "r") as f:
	nums = f.read().split(';')
	nums = map(int, nums)


print nums[1:5], max(nums), min(nums), dict(Counter(nums))