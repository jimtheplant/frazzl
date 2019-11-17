from frazzl import Service
from ariadne import QueryType
schema = """
type Query {
    getTest2: Test2
}

type Test2 {
    test1: String
}
"""

query = QueryType()
def resolve_getTest2(*args, **kwargs):
    return

query.set_field("getTest2", resolve_getTest2)

testService = Service("testService2", schema, query)
