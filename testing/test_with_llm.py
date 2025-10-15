# llm_tester.py

import json
import re
from time import sleep
from model import load_all
import asyncio
from llm_as_evaluator import llm_evaluator

async def setup():
    llm, _, _, graph = await load_all()
    return llm, graph



def run_operational_tests(llm, graph):
    with open("test_cases_llm.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("Avvio testing \n")

    results = []
    for case in test_cases:
        case_id = case.get("id")
        sintomi = case.get("input")
        age = case.get("age")
        sex = case.get("sex")
        reports = case.get("reports", [])


        # Invoca il RAG graph
        response = graph.invoke({"sintomi": sintomi, "age": age, "sex": sex, "reports": reports})

        # Pulizia eventuale codice markdown JSON
        answer_text = re.sub(r"^```json\s*|```$", "", response.get("answer").strip(), flags=re.MULTILINE)
        answer_json = json.loads(answer_text)

        # Estrai motivazione e decisione
        output_motivation = answer_json.get("motivazione", "")
        output_decision = answer_json.get("decisione", "")

        response_from_evaluator = llm_evaluator(llm, sintomi, age, sex, reports, output_decision, output_motivation)
        print(response_from_evaluator)
    
        eval_text = response_from_evaluator.content.strip()
        eval_text = re.sub(r"^```json\s*|\s*```$", "", eval_text, flags=re.MULTILINE).strip()

        eval_text = eval_text.replace("True", "true").replace("False", "false")


        eval_json = json.loads(eval_text)

        # Risultati evaluator
        passed_decision = eval_json.get("output", False)  # True/False sulla decisione
        motivation_score = eval_json.get("score", 0.0)    # punteggio motivazione
        comment = eval_json.get("commento", "")

        print(f"\n🔹 Test {case_id}")
        print(f"Input sintomi        : {sintomi}")
        print(f"Decisione modello    : {output_decision}")
        print(f"Motivazione modello  : {output_motivation}")
        print(f"Decisione corretta?  : {'True' if passed_decision else 'False'}")
        print(f"Score motivazione    : {motivation_score:.2f}")
        print(f"Commento dell'evaluator   : {comment}")

        results.append({
            "id": case_id,
            "input": sintomi,
            "output_decision": output_decision,
            "output_motivation": output_motivation,
            "passed_decision": passed_decision,
            "motivation_score": motivation_score,
            "evaluator_comment": comment
        })

        sleep(2)

    # Risultati finali
    total = len(results)
    passed_decision_count = sum(r["passed_decision"] for r in results)
    avg_motivation_score = sum(r["motivation_score"] for r in results) / total

    print("\nRISULTATI FINALI")
    print(f"Test superati (decisione)       : {passed_decision_count}/{total} | Accuratezza: {(passed_decision_count/total)*100:.1f}%")
    print(f"Score medio motivazione modello  : {avg_motivation_score:.2f}")

async def main():
    llm, graph = await setup()
    run_operational_tests(llm, graph)


if __name__ == "__main__":
    asyncio.run(main())
