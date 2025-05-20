tuple_list = []
numx = []
numy = []
slope = []

for i in range(5):  
    x = int(input("Enter a number: "))
    y = int(input("Enter a number: "))
    numx.append(x)
    numy.append(y)
    a_tuple = (x, y)
    tuple_list.append(a_tuple)
print(tuple_list)

index = 0
index_two = 1
for i in range(4):
    changey = numy[index] - numy[index_two]
    changex = numx[index] - numx[index_two]
    slope_value = changey / changex
    slope.append(slope_value)
    print(f"Slope between {tuple_list[index]} and {tuple_list[index_two]}: {slope[index]}")
    index += 1
    index_two += 1
