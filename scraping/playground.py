# Python3 code to demonstrate working of
# Splitting text and number in string
from re import sub
 
def snake_case(s) :
    return '-'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('\'', '').replace('à', 'a').replace('ç', 'c').replace('é', 'e').replace('è', 'e'))).split()).lower()


print(snake_case("glaçon"))
print(snake_case("oeufs + 1 jaune (pas obligé)"))



# initializing string
test_str = "1"
 
# printing original string
print("The original string is : " + str(test_str))
 
 
# Splitting text and number in string
text=""
numbers=""
res=[]
for i in test_str:
    if(i.isdigit()):
        numbers+=i
    else:
        text+=i
res.append(text)
res.append(numbers)
 
# printing result
print("The tuple after the split of string and number : " + str(res))