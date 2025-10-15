import os, sys, json, asyncio
import pandas as pd


from model import load_all   # Importa la funzione che costruisce il graph

# ==========================================================
# Setup: carica LLM, embeddings, vector store e graph
# ==========================================================

async def setup_graph():
    print("🔄 Caricamento del grafo e dei modelli...")
    graph = await load_all()
    print("✅ Caricamento completato.")
    return graph

# ==========================================================
# 1️⃣ Operational Testing
# ==========================================================

def operational_testing(graph):
    operational_data = [
        {"sintomi": "dolore toracico e difficoltà respiratoria", "expected": "Pronto soccorso necessario"},
        {"sintomi": "mal di testa lieve e raffreddore", "expected": "Pronto soccorso non necessario"},
        {"sintomi": "febbre alta e brividi intensi", "expected": "Pronto soccorso necessario"},
        {"sintomi": "tosse leggera e naso chiuso", "expected": "Pronto soccorso non necessario"},
        {"sintomi": "svenimento improvviso e confusione", "expected": "Pronto soccorso necessario"},
    ]

    correct = 0
    for case in operational_data:
        state = {"sintomi": case["sintomi"], "age": 40, "sex": "M", "reports": []}
        output = graph.invoke(state)
        answer = json.loads(output["answer"])
        decision = answer["decisione"]
        print(f"[Test] Sintomi: {case['sintomi']} → Decisione: {decision}")
        if decision == case["expected"]:
            correct += 1

    return round(correct / len(operational_data), 2)



# ==========================================================
# 3️⃣ Robustness Testing
# ==========================================================

def robustness_testing(graph):
    sintomi_base = "dolore toracico e difficoltà respiratoria"
    perturbazioni = [
        "dolore al petto e respiro corto",
        "leggero dolore toracico e affanno",
        "pressione al petto con respiro affannoso",
    ]

    base_state = {"sintomi": sintomi_base, "age": 50, "sex": "M"}
    base_decision = json.loads(graph.invoke(base_state)["answer"])["decisione"]

    consistenti = 0
    for s in perturbazioni:
        decision = json.loads(graph.invoke({"sintomi": s, "age": 50, "sex": "M"})["answer"])["decisione"]
        if decision == base_decision:
            consistenti += 1

    robustness_score = consistenti / len(perturbazioni)
    return round(robustness_score, 2)


# ==========================================================
# MAIN EXECUTION
# ==========================================================

async def main():
    graph = await setup_graph()

    results = {
        "Operational Test": {"Metric": "Operational Accuracy", "Result": operational_testing(graph), "Threshold": 0.8},
        "Robustness Test": {"Metric": "Robustness Score", "Result": robustness_testing(graph), "Threshold": 0.8},
    }

    df = pd.DataFrame.from_dict(results, orient="index")
    df["Status"] = df.apply(lambda r: "✅" if r["Result"] >= r["Threshold"] else "⚠️", axis=1)

    print("\n=== AI System Testing Report ===\n")
    print(df.to_string())
    print("\nInterpretazione:")
    print("- Operational Accuracy → affidabilità del sistema in casi reali")
    print("- Fairness Score → coerenza decisionale rispetto a sesso/età")
    print("- Robustness Score → stabilità di risposta a variazioni minime di input\n")


if __name__ == "__main__":
    asyncio.run(main())
