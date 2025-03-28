# 1)GCD

# def gcd_subtraction(a,b):

#     while a!=b:
#         if a>b :
#             a-=b
#         else:
#             b-=a
#     return a

# a = int(input("enter a: "))
# b = int ( input("enter b: "))

# print(gcd_subtraction(a,b))


# 2) LEAP YEAR

# year = int(input("enter the year"))

# if(year%4==0 and year%100!=0) or (year%400==0):
#     print("leap year")
# else:
#     print("not leap year")


# 3) COUNT DIGITS IN A NUMBER:

# num = int(input("enter the number: "))
# num_str = str(num)
# num_count = 0

# for i in str(num):
#     num_count+=1
# print(num_count)


# 4) SUM OF DIGITS OF A NUMBER
# num = int(input("enter the number: "))
# count = 0
# for i in str(num):
#     count+=int(i)
# print("sum is: ", count)


# 5) REVERSE WORDS IN A STRING

sentence=input("enter a sentence: ")
words=sentence.split()
reversed_words=[]

for word in reversed(words):
    reversed_words.append(word)

print(" ".join(reversed_words))