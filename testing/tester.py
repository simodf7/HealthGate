# llm_tester.py

import json
import re
from sentence_transformers import SentenceTransformer, util
from model import load_all
import asyncio

# soglia minima di similarità per considerare il test superato
SIMILARITY_THRESHOLD = 0.75


async def setup():
    _, _, _, graph = await load_all()
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model, graph


def semantic_similarity(model, text1: str, text2: str) -> float:
    """
    Restituisce la similarità semantica (cosine similarity) tra due testi.
    Valori vicini a 1 indicano alta somiglianza.
    """
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1])
    return float(score.item())


def run_operational_tests(embedding_model, graph):
    with open("test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("Avvio testing \n")

    results = []
    for case in test_cases:
        case_id = case.get("id")
        sintomi = case.get("input")
        age = case.get("age")
        sex = case.get("sex")
        reports = case.get("reports", [])
        expected_text = case.get("expected", "")
        expected_decision = case.get("decisione", "")

        # Invoca il RAG graph
        response = graph.invoke({"sintomi": sintomi, "age": age, "sex": sex, "reports": reports})

        # Pulizia eventuale codice markdown JSON
        answer_text = re.sub(r"^```json\s*|```$", "", response.get("answer").strip(), flags=re.MULTILINE)
        answer_json = json.loads(answer_text)

        # Estrai motivazione e decisione
        output_text = answer_json.get("motivazione", "")
        output_decision = answer_json.get("decisione", "")

        # calcolo della similarità semantica
        similarity = semantic_similarity(embedding_model, output_text, expected_text)
        passed_text = similarity >= SIMILARITY_THRESHOLD

        # controllo decisione esatta
        passed_decision = output_decision.strip() == expected_decision.strip()

        print(f"\n🔹 Test {case_id}")
        print(f"Input sintomi  : {sintomi}")
        print(f"Output modello : {output_text}")
        print(f"Atteso        : {expected_text}")
        print(f"Similarità    : {similarity:.2f} {'✅' if passed_text else '❌'}")
        print(f"Decisione modello : {output_decision}")
        print(f"Decisione attesa   : {expected_decision} {'✅' if passed_decision else '❌'}")

        results.append({
            "id": case_id,
            "input": sintomi,
            "output_text": output_text,
            "expected_text": expected_text,
            "similarity": similarity,
            "passed_text": passed_text,
            "output_decision": output_decision,
            "expected_decision": expected_decision,
            "passed_decision": passed_decision
        })

    # Risultati finali
    total = len(results)
    passed_text_count = sum(r["passed_text"] for r in results)
    passed_decision_count = sum(r["passed_decision"] for r in results)

    print("\n📊 RISULTATI FINALI")
    print(f"Test superati (motivazione): {passed_text_count}/{total} | Accuratezza media: {(passed_text_count/total)*100:.1f}%")
    print(f"Test superati (decisione)  : {passed_decision_count}/{total} | Accuratezza media: {(passed_decision_count/total)*100:.1f}%")


async def main():
    embedding_model, graph = await setup()
    run_operational_tests(embedding_model, graph)


if __name__ == "__main__":
    asyncio.run(main())
