from langchain_core.tools import tool

@tool
def add_numbers(a:int, b:int) -> int:
    """Add two numbers"""
    return a+b

@tool
def multiply_numbers(a:int, b:int) -> int:
    """Multiply two numbers"""
    return a*b

add_numbers.invoke({
    "a":1,
    "b":2
})

multiply_numbers.invoke({
    "a":1,
    "b":2
})