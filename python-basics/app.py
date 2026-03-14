student = ("Alice", [85, 90, 78])

print("Before:", student)

# Modify the list INSIDE the tuple — no list conversion needed
student[1].append(95)
student[1][0] = 99

print("After: ", student)