def binary_search(arr, targetVal):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == targetVal:
            return mid
        
        if arr[mid] < targetVal:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Exemplo

if __name__ == "__main__":
    array = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    target = 6
    result = binary_search(array, target)

    if result != -1:
        print(f"Elemento {target} encontrado no índice:{result}")
    else:
        print("Elemento não encontrado")