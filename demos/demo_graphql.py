import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(description="A typical hello world")

    def resolve_hello(self, info):
        return "World"


schema = graphene.Schema(query=Query)

query = """
    query SayHello {
      hello
    }
"""
result = schema.execute(query)
print(result)
