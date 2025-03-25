# 1) LARGEST NUMBER

# a=int(input("Enter first number: "))
# b=int(input("Enter second number: "))
# c=int(input("Enter third number: "))

# if a>b and a>c:
#     print("first number is largest")

# elif b>a and b>c:
#     print("second number is largest")

# else:
    
#     print("third number is largest")


# 2) FACTORIAL

# num=int(input("enter a number: "))
# fact=1

# for i in range(1,num+1):
#     fact*=i
# print(fact)

# 3)Swap Two Variables Without Using a Third Variable

# a=int(input("Enter first number: "))
# b=int(input("Enter second number: "))

# a,b=b,a
# print("After swapping: a =", a, ", b =", b)

# 4)REVERSE A NUMBER

# num =int(input("enter a number: "))
# reversed =0

# while num>0:
#     last_digit = num%10
#     reversed = reversed*10+last_digit
#     num//=10
# print("reversed number: ", reversed)


# 5)COUNT VOWELS AND CONSONANTS

sentence = input("enter a string: ").lower()
vowels ='aeiou'
vowels_count = 0
consonants_count=0

for i in sentence:
    if i in vowels:
        vowels_count+=1
    else:
        consonants_count+=1
print("vowels count",vowels_count)
print("consonant count",consonants_count)


