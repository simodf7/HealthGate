import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # o Gemini embeddings se hai accesso
 
# === Configurazione modello LLM ===

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,  # più basso per evitare invenzioni
    max_output_tokens=500
)
 
# === Prompt JSON ===

decision_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""

Sei un sistema medico. 
Devi classificare se un paziente deve recarsi al pronto soccorso o no.
Regole:

- Usa SOLO le informazioni contenute nei documenti ufficiali e nei report clinici forniti.
- Considera sia i sintomi attuali che i precedenti storici del paziente.
- Rispondi **solo in JSON** con i seguenti campi:
  - classificazione: "Pronto soccorso" o "Non urgente"
  - motivazione: breve spiegazione clinica basata su documenti
  - fonti: elenco delle fonti usate (titoli o ID documenti)
 
Contesto (documenti ufficiali + report paziente):
{context}
Sintomi attuali:
{question}
Risposta JSON:

"""

)
 
# === Recuperatore (esempio con FAISS) ===
# Carichi FAISS da disco (dove hai già inserito linee guida + report paziente)
vectorstore = FAISS.load_local("vector_db", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
 
# === Chain RAG ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": decision_prompt}
)
 
# === ESECUZIONE ===

if __name__ == "__main__":
    sintomi_correnti = "Dolore toracico acuto da 2 ore, sudorazione fredda, respiro corto"
    result = qa_chain.invoke(sintomi_correnti)
    print(result["result"])

 