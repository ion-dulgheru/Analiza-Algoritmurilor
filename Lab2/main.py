from __future__ import annotations

from bisect import bisect_left
from heapq import merge as _heapq_merge
from random import randint
from typing import List

def merge_sort(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    result: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result



def quick_sort(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]
    pivot = a[randint(0, len(a) - 1)]
    lo, eq, hi = [], [], []
    for x in a:
        if x < pivot:
            lo.append(x)
        elif x > pivot:
            hi.append(x)
        else:
            eq.append(x)
    return quick_sort(lo) + eq + quick_sort(hi)

#  3.  HEAP SORT
def heap_sort(a: List[int]) -> List[int]:
    a = a[:]
    n = len(a)

    def _sift_down(start: int, end: int) -> None:
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                root = child
            else:
                break

    for start in range((n - 2) // 2, -1, -1):
        _sift_down(start, n - 1)

    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(0, end - 1)

    return a


def patience_sort(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]

    piles: List[List[int]] = []
    tops: List[int] = []         

    for x in a:
        pos = bisect_left(tops, x)
        if pos == len(piles):
            piles.append([x])     
            tops.append(x)
        else:
            piles[pos].append(x)  # place on existing pile
            tops[pos] = x         # update the top

    for p in piles:
        p.reverse()

    return list(_heapq_merge(*piles))


def merge_sort_opt(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]
    mid = len(a) // 2
    left = merge_sort_opt(a[:mid])
    right = merge_sort_opt(a[mid:])
    return _merge_opt(left, right)

def _merge_opt(left: List[int], right: List[int]) -> List[int]:
    if left[-1] <= right[0]:
        return left + right

    result: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort_opt(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]
    
    # Median-of-3: alege mediana dintre primul, mijlocul si ultimul element
    mid = len(a) // 2
    candidates = sorted([a[0], a[mid], a[-1]])
    pivot = candidates[1]
    
    lo, eq, hi = [], [], []
    for x in a:
        if x < pivot:
            lo.append(x)
        elif x > pivot:
            hi.append(x)
        else:
            eq.append(x)
    return quick_sort_opt(lo) + eq + quick_sort_opt(hi)

def heap_sort(a: List[int]) -> List[int]:
    a = a[:]
    n = len(a)

    def _sift_down_opt(start: int, end: int) -> None:
        root = start
        # Coboara direct pana la frunza
        child = 2 * root + 1
        while child <= end:
            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1
            a[root], a[child] = a[child], a[root]
            root = child
            child = 2 * root + 1
        # Urca inapoi pana la pozitia corecta
        while root > start:
            parent = (root - 1) // 2
            if a[parent] < a[root]:
                a[parent], a[root] = a[root], a[parent]
                root = parent
            else:
                break

    for start in range((n - 2) // 2, -1, -1):
        _sift_down_opt(start, n - 1)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down_opt(0, end - 1)
    return a



from collections import deque

def patience_sort_opt(a: List[int]) -> List[int]:
    if len(a) < 2:
        return a[:]
    
    piles: List[deque] = []
    tops: List[int] = []

    for x in a:
        pos = bisect_left(tops, x)
        if pos == len(piles):
            piles.append(deque([x]))
            tops.append(x)
        else:
            piles[pos].appendleft(x)  # adauga direct la inceput, fara reverse
            tops[pos] = x

    return list(_heapq_merge(*piles))