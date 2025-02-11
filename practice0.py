friends = []
values = [16, 3, 2, 13]

for i in range(len(values)):
    values[i] = i * i
print(values)

friends.append("Bob")
friends.insert(0, "Amy")

if "Amy" in friends:
    n = friends.index("Amy")
    friends.pop()

print(friends)
