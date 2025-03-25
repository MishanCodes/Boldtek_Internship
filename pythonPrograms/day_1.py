#1)  Given an integer,n , perform the following conditional actions:

# If n is odd, print Weird
# If n is even and in the inclusive range of 2 to 5, print Not Weird
# If n is even and in the inclusive range of 6 to 20 , print Weird
# If n is even and greater than 20, print Not Weird

# n = int(input("Enter an integer: "))

# if n % 2 != 0:
#     print("Weird")
# elif n % 2 == 0 and n in range(2, 6):
#     print("Not Weird")  
# elif n % 2 == 0 and n in range(6, 21):
#     print("Weird")  
# elif n % 2 == 0 and n > 20:
#     print("Not Weird")

# 2) FIBONACCI SERIES

# def fibonacci(n):
#     a,b=0,1

#     for _ in range(n):
#         print(a,end=" ")
#         a,b=b,a+b
# num = int(input("Enter the no. of fibonacci series: "))

# if num<=0:
#     print("Enter a positive integer")
# else:
#     fibonacci(num)


# 3) PALINDROME STRING 

# text = input("Enter a string: ")
# reverseText = ""

# for char in text:
#     reverseText = char+reverseText
# if text == reverseText:
#     print("String is palindrome")
# else:
#     print("String is not palindrome")


# 4) PRIME OR NOT

# num = int(input("enter a number: "))

# if num>1:
#     for x in range(2,num):
#         if num % x == 0:
#             print("not prime")
#             break
#     else:
#         print("is prime")
# else:
#     print("not prime")



# 5) ARMSTRONG NUMBER

num = int(input("enter a number: "))

num_digits = len(str(num))
powered=0

for i in str(num):
    powered += int(i)**num_digits
if powered == num:
    print("armstrong no.")
else : 
    print("not armstrong no.")