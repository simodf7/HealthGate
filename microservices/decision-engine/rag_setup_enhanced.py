from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict, Dict, Optional
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from sentence_transformers import CrossEncoder
import numpy as np
import json
import logging
from datetime import datetime
import hashlib
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedState(TypedDict):
    sintomi: str
    storia_paziente: str
    context: List[Document]
    answer: str
    confidence_score: float
    metadata: Dict


class MedicalRAGPipeline:
    """Enhanced RAG pipeline for medical triage"""
    
    def __init__(self, vector_store, llm, use_cache=True):
        self.vector_store = vector_store
        self.llm = llm
        self.use_cache = use_cache
        self.cache = {} if use_cache else None
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
    def expand_query(self, query: str) -> str:
        """Espande la query con sinonimi medici"""
        expansion_prompt = """
        Dato il termine medico: {query}
        Genera 3 sinonimi o termini correlati in italiano.
        Rispondi SOLO con i termini separati da virgole.
        """
        
        try:
            expanded = self.llm.invoke(expansion_prompt.format(query=query))
            return f"{query} {expanded.content}"
        except:
            return query
    
    def retrieve_enhanced(self, state: EnhancedState) -> Dict:
        """Retrieval migliorato con reranking e filtering"""
        
        # Combina e espandi query
        combined_query = f"{state['sintomi']} {state['storia_paziente']}"
        expanded_query = self.expand_query(combined_query)
        
        # Check cache
        if self.use_cache:
            cache_key = hashlib.md5(expanded_query.encode()).hexdigest()
            if cache_key in self.cache:
                logger.info("Cache hit for query")
                return {"context": self.cache[cache_key]}
        
        # Retrieve più documenti del necessario
        retrieved_docs = self.vector_store.similarity_search(
            expanded_query, 
            k=12  # Retrieve di più per poi fare reranking
        )
        
        # Reranking con cross-encoder
        if retrieved_docs:
            pairs = [[expanded_query, doc.page_content] for doc in retrieved_docs]
            scores = self.reranker.predict(pairs)
            
            # Ordina per score e filtra per threshold
            threshold = 0.5
            filtered_docs = [
                (doc, score) for doc, score in zip(retrieved_docs, scores) 
                if score > threshold
            ]
            filtered_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Prendi top-k documenti
            top_docs = [doc for doc, _ in filtered_docs[:6]]
            
            # Log retrieval metrics
            logger.info(f"Retrieved {len(retrieved_docs)} docs, filtered to {len(top_docs)}")
            logger.info(f"Avg relevance score: {np.mean(scores):.3f}")
            
            # Cache results
            if self.use_cache and cache_key:
                self.cache[cache_key] = top_docs
            
            return {"context": top_docs}
        
        return {"context": []}
    
    def generate_with_validation(self, state: EnhancedState) -> Dict:
        """Generazione con validazione e confidence scoring"""
        
        if not state["context"]:
            return {
                "answer": json.dumps({
                    "decisione": "Consultare medico",
                    "motivazione": "Informazioni insufficienti per valutazione",
                    "confidence": 0.0
                }),
                "confidence_score": 0.0
            }
        
        # Prepara context con metadata
        docs_content = "\n\n".join([
            f"[Fonte: {doc.metadata.get('source', 'N/A')}]\n{doc.page_content}"
            for doc in state["context"]
        ])
        
        # Prompt migliorato con few-shot examples
        enhanced_prompt = """
        Sei un assistente sanitario specializzato nel triage di pronto soccorso.
        
        ESEMPI DI VALUTAZIONE CORRETTA:
        
        Esempio 1:
        Sintomi: "Dolore toracico oppressivo, irradiato al braccio sinistro, sudorazione profusa"
        Decisione: Pronto soccorso necessario
        Motivazione: Sintomi fortemente suggestivi di sindrome coronarica acuta, richiede valutazione immediata
        Red flags: dolore toracico tipico, irradiazione, sintomi neurovegetativi
        
        Esempio 2:
        Sintomi: "Mal di gola da 2 giorni, no febbre, deglutizione normale"
        Decisione: Pronto soccorso non necessario
        Motivazione: Faringite lieve, gestibile con terapia sintomatica domiciliare
        Red flags: nessuno
        
        VALUTAZIONE ATTUALE:
        
        Sintomi riferiti: {sintomi}
        
        Storia clinica: {storia_paziente}
        
        Linee guida pertinenti:
        {context}
        
        ISTRUZIONI:
        1. Identifica TUTTI i red flags (sintomi di allarme)
        2. Valuta la gravità su scala 1-10
        3. Considera le comorbidità dalla storia clinica
        4. Basa la decisione ESCLUSIVAMENTE sulle linee guida fornite
        5. In caso di dubbio, err on the side of caution
        
        CRITERI ASSOLUTI PER PS:
        - Dolore toracico acuto
        - Difficoltà respiratoria severa
        - Alterazione stato mentale
        - Segni di shock
        - Trauma cranico con perdita di coscienza
        - Dolore addominale acuto severo
        
        Rispondi in formato JSON:
        {{
            "red_flags": ["lista dei sintomi di allarme identificati"],
            "gravita": numero da 1 a 10,
            "decisione": "Pronto soccorso necessario" oppure "Pronto soccorso non necessario",
            "motivazione": "spiegazione dettagliata basata sulle linee guida",
            "raccomandazioni": "consigli specifici per il paziente",
            "confidence": numero da 0.0 a 1.0 indicante la certezza della valutazione
        }}
        """
        
        # Genera risposta
        messages = enhanced_prompt.format(
            sintomi=state["sintomi"],
            storia_paziente=state["storia_paziente"],
            context=docs_content
        )
        
        # Multiple sampling per consistency
        responses = []
        for _ in range(3):
            response = self.llm.invoke(messages, temperature=0.1)
            try:
                parsed = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
                responses.append(parsed)
            except:
                continue
        
        if not responses:
            return {
                "answer": json.dumps({
                    "decisione": "Consultare medico",
                    "motivazione": "Errore nella valutazione, consultare personale medico",
                    "confidence": 0.0
                }),
                "confidence_score": 0.0
            }
        
        # Verifica consenso tra le risposte
        decisions = [r.get("decisione") for r in responses]
        if len(set(decisions)) == 1:
            # Consenso completo
            final_response = responses[0]
            final_response["confidence"] = 0.9
        else:
            # Prendi la decisione più conservativa (PS necessario)
            ps_count = sum(1 for d in decisions if "necessario" in d.lower() and "non" not in d.lower())
            if ps_count >= 2:
                final_response = next(r for r in responses if "necessario" in r.get("decisione", "").lower() and "non" not in r.get("decisione", "").lower())
                final_response["confidence"] = 0.6
            else:
                final_response = responses[0]
                final_response["confidence"] = 0.5
                final_response["motivazione"] += " (Valutazione con incertezza, si consiglia comunque consulto medico)"
        
        # Log della decisione
        logger.info(f"Decision: {final_response['decisione']} (confidence: {final_response['confidence']})")
        
        return {
            "answer": json.dumps(final_response),
            "confidence_score": final_response.get("confidence", 0.5)
        }


def create_enhanced_graph(vector_store, llm):
    """Crea il grafo LangGraph ottimizzato"""
    
    pipeline = MedicalRAGPipeline(vector_store, llm)
    
    def retrieve_step(state: EnhancedState):
        return pipeline.retrieve_enhanced(state)
    
    def generate_step(state: EnhancedState):
        return pipeline.generate_with_validation(state)
    
    def add_metadata_step(state: EnhancedState):
        """Aggiunge metadata per tracking"""
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "2.0",
                "model": "gemini-2.0-flash",
                "num_docs_used": len(state.get("context", []))
            }
        }
    
    # Costruisci il grafo
    graph_builder = StateGraph(EnhancedState)
    
    # Aggiungi i nodi
    graph_builder.add_node("retrieve", retrieve_step)
    graph_builder.add_node("generate", generate_step)
    graph_builder.add_node("add_metadata", add_metadata_step)
    
    # Definisci il flusso
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", "add_metadata")
    
    return graph_builder.compile()


# Funzione per backward compatibility
def graph_building(vector_store, llm):
    """Wrapper per mantenere compatibilità con codice esistente"""
    return create_enhanced_graph(vector_store, llm)