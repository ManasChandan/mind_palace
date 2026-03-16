### Getting the unique numner of substrings starting with a different letter

In the terms of unique number any substring can start with any letter in the string, hence the answer is always len(set(nums))

### Two pointer - Sort of pointer

If we want to maintain order, it can be both left to right and vice-versa too. 
so left ++ and right -- both maintains orders

### deci-integer, Min number of deci-numbers

**VERY GREEDY**

let us cosnider we have a number 8, for to get the sum via a deci number you need at least that many 1s. 

### Remainder Tricks

if you wnat to fine the min number to be deducted or added to make it divisible it would go via the remainder only
sum(nums) % k

the trick for min operation is as follows - min(ele%3, 3-(ele%3))