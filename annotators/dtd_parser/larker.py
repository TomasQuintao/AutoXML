from lark import Lark

grammar = """
start: subject verb object
subject: "I" | "You"
verb: "see" | "like"
object: "dogs" | "cats"
"""

parser = Lark(grammar)

try:
    parser.parse("I like dogs")
    print("Valid")
except:
    print("Invalid")