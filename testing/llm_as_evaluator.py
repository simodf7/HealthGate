# llm_evaluator.py


from langchain.prompts import PromptTemplate
 
 
def llm_evaluator(llm, sintomi, age, sex, reports, decision, motivation):

    
    if len(reports) != 0:
        report_text = "\n".join(
        f"- Data Report: {r.get('data', 'N/A')}\n"
        f"  Sintomi: {r.get('sintomi', 'N/A')}\n"
        f"  Motivazioni date dall'LLM sul recarsi o meno al pronto soccorso: {r.get('motivazione', 'N/A')}\n"
        f"  Diagnosi del medico del pronto soccorso: {r.get('diagnosi', 'N/A')}\n"
        f"  Trattamento del medico del pronto soccorso: {r.get('trattamento', 'N/A')}\n"
        for r in reports
    )
    else:
        report_text = "\n Non sono presenti report clinici precedenti associati a questo paziente \n"

    prompt_template = """
        Sei un assistente sanitario virtuale incaricato di valutare risposte cliniche generate da un modello AI.
        Il compito del modello in questione è quello di prendere dei sintomi raccolti da un paziente, oltre alle sue informazioni personali \\
        e ai precedenti report clinici del paziente, e decidere se è necessario che si debba recare o meno al pronto soccorso \\
        oltrechè dare motivazione della decisione presa. 

        

        Gli input che ti verranno forniti sono questi (in parte sono gli stessi dati al modello di AI):
        - Sintomi attuali del paziente: {sintomi}
        - Età: {age}, Sesso: {sex}
        - Precedenti report clinici: {reports}
        - Decisione presa dal modello ("Pronto soccorso necessario" o "Pronto soccorso non necessario"): {decision} 
        - Risposta generata dal modello: {motivation}

        Il tuo compito è il seguente:
        1. Valutare se la decisione presa è corretta. 
        2. Valuta se la motivazione data è corretta e sufficiente rispetto ai dati clinici forniti.
        3. Fornisci a quel punto:
            - "output": "True" se la decisione presa è corretta / "False" altrimenti.
            - "score": punteggio da 0 a 1 a seconda della qualità della motivazione fornita in relazione alle linea guida (1 = ottima, 0 = scarsa)
            - "commento": breve spiegazione del punteggio e dell'output assegnati. 

        Regole:
        - Non inventare nuove informazioni o diagnosi.
        - Rispondi solo in formato JSON.

        Esempio di output atteso DA RISPETTARE OBBLIGATORIAMENTE:
        {{
            "output": True
            "score": 0.9,
            "commento": "La risposta del modello coglie correttamente l'infezione respiratoria e menziona i report precedenti rilevanti."
        }}

        """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["sintomi", "age", "sex", "reports", "model_output"]
    )

    formatted_prompt = prompt.format(
        sintomi=sintomi,
        age=age,
        sex=sex,
        reports=report_text, 
        decision = decision, 
        motivation = motivation
    )

    # Chiamata all'LLM
    response = llm.invoke(formatted_prompt, temperature=0)
    return response 




 
 