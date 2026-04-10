Here is a comprehensive Markdown guide for bitwise "creation" and manipulation tricks. I've categorized them so you can easily reference them for competitive programming or system-level tasks.

---

# 🛠️ The Bitwise Cheat Sheet

Bitwise operations allow you to manipulate numbers at the binary level. In these examples, `n` usually represents the number you are transforming, and `i` represents the bit index (starting from 0 at the right).

## 1. Creating Powers and Masks
These are the building blocks for most bitwise logic.

| Goal | Operation | Binary Example ($i=3$) | Result |
| :--- | :--- | :--- | :--- |
| **Create $2^i$** | `1 << i` | `0000 -> 1000` | $8$ |
| **All 1s (Size $i$)** | `(1 << i) - 1` | `(1 << 3) - 1` | $7$ (`0111`) |
| **All 1s (Full)** | `-1` or `~0` | `11111111...` | All bits set |

---

## 2. Setting and Clearing Specific Bits
Use these to "flip switches" inside an integer.

### **Set a Bit (Make it 1)**
Use the `OR` operator. It ensures the bit is 1 regardless of its previous state.
* **Formula:** `n | (1 << i)`
* **Use Case:** Enabling a specific flag in a bitmask.

### **Clear a Bit (Make it 0)**
Use `AND` with a "NOT" mask.
* **Formula:** `n & ~(1 << i)`
* **Use Case:** Disabling a specific feature or permission.

### **Toggle a Bit (Flip it)**
Use the `XOR` operator.
* **Formula:** `n ^ (1 << i)`
* **Use Case:** Switching a state back and forth (e.g., On to Off).

### **Check a Bit**
Extract the value of a specific bit.
* **Formula:** `(n >> i) & 1`
* **Use Case:** Checking if a number is even/odd (`n & 1`) or checking a specific permission.

---

## 3. The "Rightmost Bit" Tricks
These are highly optimized tricks used in advanced algorithms (like Fenwick Trees).



* **Isolate Rightmost 1:** `n & -n`
    * *Input:* `12` (`1100`) $\rightarrow$ *Output:* `4` (`0100`)
* **Remove Rightmost 1:** `n & (n - 1)`
    * *Input:* `12` (`1100`) $\rightarrow$ *Output:* `8` (`1000`)
* **Find Smallest $2^k - 1 \ge n$:** `(1 << n.bit_length()) - 1`
    * *Input:* `10` (`1010`) $\rightarrow$ *Output:* `15` (`1111`)

---

## 4. Arithmetic Shortcuts
These are often faster than standard math operators in low-level languages.

| Math Equivalent | Bitwise Operation | Note |
| :--- | :--- | :--- |
| **Multiply by 2** | `n << 1` | Shifts all bits left |
| **Divide by 2** | `n >> 1` | Integer division (floored) |
| **Is Even?** | `(n & 1) == 0` | Checks the $2^0$ bit |
| **Is Power of 2?** | `n > 0 and (n & (n - 1)) == 0` | Powers of 2 only have one `1` |
| **Absolute Value** | `(n ^ mask) - mask` | Where `mask = n >> 31` |

---

## 5. The XOR Magic
The `XOR` (`^`) operator is unique because it is its own inverse.

* **Swap two numbers:**
    ```python
    a ^= b
    b ^= a
    a ^= b
    ```
* **Find the non-duplicate:** Given an array where every element appears twice except one, `XOR` all elements together. The duplicates cancel out to `0`, leaving the unique number.
    * `2 ^ 3 ^ 2 == 3`

---

> **Pro Tip:** When using these in Python or C++, remember that **operator precedence** can be tricky. Bitwise operators usually have lower precedence than addition or subtraction. **Always use parentheses** to be safe: 
> `(n & (1 << i))` instead of `n & 1 << i`

## Live example - 1 [_is_prime_set]

This code creates a lookup table (_is_prime_set) to instantly check if the number of set bits (1s) in any integer up to 1,000,000 is a prime number.

### How it works

   1. The Mask (665772): This is a bitmask where the 1s are placed at the positions of prime numbers. In binary, 665772 is 1010001010001010101100.
   * If you count from the right (starting at 0), the bits at positions 2, 3, 5, 7, 11, 13, 17, and 19 are set to 1. These are all the prime numbers possible for a 20-bit integer (since $2^{20} > 1,000,000$).
   2. The Loop: It iterates through every number $i$ from 0 to 1,000,000.
   3. i.bit_count(): This counts how many 1s are in the binary form of the current number $i$.
   4. The Check (_mask >> i.bit_count() & 1): It shifts the mask right by the number of set bits. If the bit at that position is 1, it means the count is a prime number.
   5. The Storage: If the count is prime, it marks _is_prime_set[i] as 1.

### Example: Checking the number 7
Let's see what happens when the loop reaches i = 7:

* Binary of 7: 111
* i.bit_count(): There are 3 set bits.
* Shift the Mask: The code shifts the mask 665772 right by 3 spots.
* Result: Since the 3rd bit of the mask is 1 (because 3 is prime), the condition is true.
* Final Action: _is_prime_set[7] is set to 1. [1] 
