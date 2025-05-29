def fibonacci_sequence(n):
    """
    Generate the Fibonacci sequence up to n terms.

    Args:
        n (int): The number of terms to generate. Must be a non-negative integer.

    Returns:
        list: A list containing the Fibonacci sequence up to n terms.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence


if __name__ == "__main__":
    # Simple test cases
    print("Fibonacci sequence with 0 terms:", fibonacci_sequence(0))  # []
    print("Fibonacci sequence with 1 term:", fibonacci_sequence(1))   # [0]
    print("Fibonacci sequence with 5 terms:", fibonacci_sequence(5))  # [0, 1, 1, 2, 3]
    print("Fibonacci sequence with 10 terms:", fibonacci_sequence(10))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
