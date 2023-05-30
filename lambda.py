people = [
    {"name": "Harry", "house": "Gryffindor"},
    {"name": "Cho", "house": "Ravenclaw"},
    {"name": "Draco", "house": "Slytherin"}
]

def f(person):
    return person["house"]

# Print name of person to find the house
name = input("Student: ")
print(name + "in " + f(name))

# people.sort(key=lambda person: person["name"])

# print(people) 
