import json
from aider_mcp import code_with_ai

def test_complex_algorithm():
    prompt = (
        "Design and implement a complex algorithm that requires advanced reasoning "
        "and sophisticated data structures. The algorithm should efficiently solve "
        "the problem of finding the shortest path in a weighted graph with negative "
        "weights but no negative cycles. Provide the implementation in Python."
    )
    working_dir = "."
    editable_files = []
    readonly_files = []
    model = None  # Let strategic selection pick the best model

    result = code_with_ai(
        prompt=prompt,
        working_dir=working_dir,
        editable_files=editable_files,
        readonly_files=readonly_files,
        model=model,
    )
    print("=== Strategic Model Selection Test Result ===")
    print(result)

if __name__ == "__main__":
    test_complex_algorithm()
