def llm_invocation(sintomi: str, storia: str):

    response = graph.invoke({"sintomi": sintomi, "storia_paziente": storia})
    print(response["answer"])
