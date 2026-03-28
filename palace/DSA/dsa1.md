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

### The solution to get n number of combinations

How many 2 element array can be made can be answere by nc2, which is nothing but n(n-1)//2.

### The index of the alphabtes like a=1 or a=26

for a=1, use ord(ele) - 96, for a=26 123-ord(ele)

### The setting of the matrix for cols to 0s where (i,j) is 0

Store the row and col arr. Make their indexes as 0 wherever applicable.
Re-iterate the array and maek if col[i] is 0 or row[j] is 0

### Kadane's Algorithm

```python
max_sum = float('-inf')
        cont_sum = 0
        for ele in nums:
            cont_sum += ele
            max_sum = max(max_sum, cont_sum)
            if cont_sum < 0:
                cont_sum = 0
        return max_sum
```

### Min Bits !

The Logic XOR the two numbers: The XOR operation ($start \oplus goal$) compares each bit of two numbers. It returns 1 if the bits are different and 0 if they are the same.Example: 
- If start = 10 (1010) and goal = 7 (0111).$1010 \oplus 0111 = 1101$Count the 1s: The resulting number has a 1 at every position where a flip is necessary. 
- Therefore, the total count of set bits (1s) in the XOR result is answer.
- There is no sighn change if we change the directionality. 

### The Two-Pass OptimizationRow [DC]

- Maxima: Create a temporary matrix where each element at (i, j) is the maximum of grid[i][j], grid[i][j+1], and grid[i][j+2]. This reduces the width from $n$ to $n-2$.Column 
- Maxima: Take that temporary matrix and, for each column, find the maximum of three consecutive vertical cells.

### Min Operations between 2 arrays

- sorting and continuos difference of elements.

### https://leetcode.com/problems/minimum-number-of-operations-to-move-all-balls-to-each-box

```python
n = len(boxes)
answer = [0]*n

ball_cnt = 0
movements = 0
for i in range(n):
        answer[i] += movements
        ball_cnt += int(boxes[i])
        movements += ball_cnt

ball_cnt = 0
movements = 0
for i in range(n-1, -1, -1):
        answer[i] += movements
        ball_cnt += int(boxes[i])
        movements += ball_cnt

return answer
```

### https://leetcode.com/problems/find-the-number-of-good-pairs-i/description/

complexity NlogN

```python
from collections import Counter

        c1 = Counter(nums1)

        c2 = Counter([i*k for i in nums2])

        pairs = 0

        max_num1 = max(nums1)

        for divisior, freq in c2.items():

            for d in range(divisior, max_num1+1, divisior):

                if d in c1:

                    pairs += freq * c1[d]
        
        return pairs
```
### https://leetcode.com/problems/number-of-steps-to-reduce-a-number-to-zero/submissions/1961147361/

BIT MANIPULATION

```python
if num == 0: return 0
        binary_str = bin(num)[2:]
        return (len(binary_str) - 1) + binary_str.count('1')
```
