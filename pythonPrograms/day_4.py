# 1) Remove Duplicates from a List

# def remove_duplicates(lst):
#     seen = set()
#     result = []
#     for num in lst:
#         if num not in seen:
#             seen.add(num)
#             result.append(num)
#     return result

# numbers = list(map(int, input("Enter numbers: ").split()))
# print("List after removing duplicates:", remove_duplicates(numbers))


# 2)Check if Two Strings are Anagrams

# string1=input("enter string 1")
# string2=input("enter string 2")

# SortedString1= sorted(string1)
# SortedString2= sorted(string2)

# if SortedString1==SortedString2:
#     print("Anagrams")
# else:
#     print("Not anagrams")

# 3) COUNT WORDS IN A SENTENCE

# string = input("enter a string")
# splitted = string.split()

# count = 0

# for i in splitted:
#     count+=1
# print(count)



# 4)  Find the Longest Word in a Sentence

# def longest_word(sentence):
#     words = sentence.split()
#     longest = "" 
    
#     for word in words:
#         if len(word) > len(longest):  
#             longest = word
    
#     return longest

# text = input("Enter a sentence: ")
# print("Longest word:", longest_word(text))


# 5) Count Digits, Letters, and Special Characters in a String

def count_characters(string):
    letters = digits = special_chars = 0

    for char in string:
        if char.isalpha():
            letters += 1
        elif char.isdigit():
            digits += 1
        else:
            special_chars += 1

    print("Letters:", letters)
    print("Digits:", digits)
    print("Special Characters:", special_chars)

text = input("Enter a string: ")
count_characters(text)
