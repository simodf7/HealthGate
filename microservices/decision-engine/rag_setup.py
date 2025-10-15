from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict, Dict


# Define state for application
class State(TypedDict):
    sintomi: str
    age: int
    sex: str
    reports: List[Dict]
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State, vector_store):
    query_parts = [f"Sintomi attuali: {state['sintomi']}"]

    # Se ci sono report precedenti, aggiungili
    if state.get("reports"):
        reports_text = []
        for report in state["reports"]:
            r_text = (
                f"Report precedente - Sintomi: {report.get('sintomi', '')}. "
                f"Motivazione della visita: {report.get('motivazione', '')}."
                f"Diagnosi del medico del pronto soccorso: {report.get('diagnosi', '')}. "
                f"Trattamento del medico del pronto soccorso: {report.get('trattamento', '')}. "
            )
            reports_text.append(r_text)

        query_parts.append(" ".join(reports_text))

    # Crea la query finale per la similarity search
    query = "\n".join(query_parts)

    
    retrieved_docs = vector_store.similarity_search(query, k=6)
    print("\n\n--- RETRIEVED DOCS ---\n\n")
    for doc in retrieved_docs:
        print("Content: " +  doc.page_content + "\n")
        print("Source: " + doc.metadata['source'] + "\n")
        print("------------------------------------- + \n")


    return {"context": retrieved_docs}


def generate(state: State, llm):
    docs_content = "\n\n".join("'" + doc.page_content + "'" for doc in state["context"])

    print("\n\n--- DOCS CONTENT ---\n\n")
    print(docs_content)
    print("\n\n-----\n\n")

    if len(state['reports']) != 0:
        report_text = "\n".join(
        f"- Data Report: {r.get('data', 'N/A')}\n"
        f"  Sintomi: {r.get('sintomi', 'N/A')}\n"
        f"  Motivazioni date dall'LLM sul recarsi o meno al pronto soccorso: {r.get('motivazione', 'N/A')}\n"
        f"  Diagnosi del medico del pronto soccorso: {r.get('diagnosi', 'N/A')}\n"
        f"  Trattamento del medico del pronto soccorso: {r.get('trattamento', 'N/A')}\n"
        for r in state["reports"]
    )
    else:
        report_text = "\n Non sono presenti report clinici precedenti associati a questo paziente \n"



    print("\n\n--- REPORT TEXT ---\n\n")
    print(report_text)
    print("\n\n-----\n\n")


    messages = prompt.invoke({"sintomi": state["sintomi"], "age": state["age"], "sex": state['sex'], "report": report_text, "context": docs_content})
    response = llm.invoke(messages, temperature=0)
    return {"answer": response.content}


prompt_template = """
    Sei un assistente sanitario virtuale.

    Un paziente ti fornisce informazioni sui suoi sintomi. 
    Riceverai inoltre informazioni da un Retriever che ha accesso a linee guida ospedialiere ufficiali.
    Inoltre sempre il retriever ti fornirà uno storico clinico del paziente, se presente.
    
    IMPORTANTE:
    - Le tue decisioni devono basarsi **esclusivamente** sui documenti forniti dal Retriever.
    - Non utilizzare conoscenze esterne o supposizioni personali.
    
    Il tuo compito è il seguente: 
    - Classificare se il paziente deve recarsi al pronto soccorso immediatamente o se non è necessario.
    - Fornire una motivazione concisa basata sui documenti forniti.
    
    Input: 

    - Sintomi attuali del paziente: {sintomi}
    - Età del paziente: {age}
    - Sesso del paziente: {sex}
    - Precedenti Report clinici del paziente: {report}
    - Estratti da linee guida ufficiali relativi ai sintomi: {context}

    Rispondi seguendo ESATTAMENTE con un dizionario come segue.
    
    Answer: {
        "decisione": "Pronto soccorso necessario" o "Pronto soccorso non necessario",
        "motivazione": Breve spiegazione della decisione
    }
       

    ---

   ### ESEMPIO

    **Esempio di input:**
    - Sintomi attuali del paziente: 
    "Il paziente lamenta dolore toracico oppressivo irradiato al braccio sinistro, associato a difficoltà respiratoria e sudorazione fredda, insorti da circa 20 minuti."

    - Età del paziente: 58  
    - Sesso del paziente: "M"  

    - Precedenti Report clinici del paziente:  
        - Data Report: 2024-06-15  
        Sintomi: Febbre alta e tosse persistente  
        Motivazioni date dall'LLM sul recarsi al pronto soccorso o meno: Possibile infezione respiratoria non grave  
        Diagnosi del medico del pronto soccorso: Bronchite acuta  
        Trattamento del medico del pronto soccorso: Antibiotico orale e riposo domiciliare  

        - Data Report: 2024-08-02  
        Sintomi: Dolore epigastrico e nausea post-prandiale  
        Motivazioni date dall'LLM sul recarsi al pronto soccorso o meno: Probabile gastrite, non richiede accesso urgente  
        Diagnosi del medico del pronto soccorso: Gastrite acuta  
        Trattamento del medico del pronto soccorso: Inibitori di pompa protonica e dieta leggera per 7 giorni  

    - Estratti da linee guida ufficiali relativi ai sintomi:  
    "Il dolore toracico di tipo oppressivo, irradiato al braccio o alla mandibola e associato a dispnea o sudorazione, deve essere considerato un possibile segno di sindrome coronarica acuta.  
    È raccomandato l’invio immediato del paziente al pronto soccorso per valutazione cardiologica urgente."

    **Esempio di output:**
    {
        "decisione": "Pronto soccorso necessario",
        "motivazione": "Il dolore toracico oppressivo irradiato e la dispnea sono compatibili con una possibile sindrome coronarica acuta, come indicato dalle linee guida. È indicato l’invio immediato in pronto soccorso per accertamenti urgenti."
    }

"""


prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["sintomi", "age", "sex", "report", "context"]
)

def graph_building(vector_store, llm):

    def retrieve_step(state):
        return retrieve(state, vector_store)
    
    def generate_step(state):
        return generate(state, llm)
        
    graph_builder = StateGraph(State).add_sequence([retrieve_step, generate_step])
    graph_builder.add_edge(START, "retrieve_step")
    graph = graph_builder.compile()

    return graph

