## Merge Sort [COUNTING RELATIVE ORDER]

```python
class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        
        def merge_two(left, right):

            result = []
            i = j = 0

            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])

            return result
        
        if len(nums) <= 1:
            return nums
        
        mid = len(nums) // 2
        
        left_arr = self.sortArray(nums[:mid])
        right_arr = self.sortArray(nums[mid:])

        merge_sort = merge_two(left_arr, right_arr)

        return merge_sort
```

## Merge Sort Variation i>j but arr[j] > arr[i]

```python
class Solution:
    def reversePairs(self, nums: List[int]) -> int:
        
        def sort_n_count(left, right):

            if left >= right:
                return 0
            
            mid = (left + right) // 2

            count = sort_n_count(left, mid) + sort_n_count(mid+1, right)

            j = mid + 1

            for i in range(left, mid+1):

                while j <= right and nums[i] > 2 * nums[j]:
                    j+=1
                
                count += (j - (mid+1))
            
            nums[left:right+1] = sorted(nums[left:right+1])

            return count
        
        return sort_n_count(0, len(nums)-1)
```