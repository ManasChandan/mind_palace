### Revert Binray tree

```python
if root is None:
    return None
        
root.left, root.right = root.right, root.left

self.invertTree(root.left)
self.invertTree(root.right)

return root
```

### Reverse LL
```python
if head is None:
    return None

prev=None
curr=head

while curr:
    next_n = curr.next
    curr.next = prev
    prev = curr
    curr = next_n
return prev
```