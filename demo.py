def get_prime(l):
    primes = []
    
    for num in range(1, l+1):
        is_prime = True
        
        for i in range(1, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
            
        if is_prime:
            primes.append(num)
    return primes
    
answer = get_prime(2)
print(answer)