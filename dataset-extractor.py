import google.generativeai as genai
import pandas as pd
import json
import time

# 1. Configure sua API Key (Gere gratuitamente no Google AI Studio)
# AVISO: Substitua pela sua chave, mas não compartilhe a original publicamente!
genai.configure(api_key="API-KEY")


# 2. Escolha o modelo. 

model = genai.GenerativeModel(
    'gemini-2.5-pro',
    generation_config={
        "temperature": 0.1, # Temperatura super baixa para respostas determinísticas
        "response_mime_type": "application/json" # FORÇA o modelo a devolver apenas JSON
    },
    system_instruction="""You are a computational linguist expert in board games. Your task is to perform Aspect-Based Sentiment Analysis (ABSA) on reviews from the BoardGameGeek website.

Strict Rules:

You must extract the aspects discussed in the text and classify them.

Allowed aspects: "rules", "components", "replayability", "interaction", "complexity", "luck". (If the text discusses another topic, ignore it. Do not create new aspects).

Allowed sentiments: "positive", "negative", "neutral".

Return ONLY a valid JSON object, without markdown or additional explanations.

Input Example:
"The learning curve is steep and the rulebook is a mess, but the miniatures are absolutely stunning."

Expected Output Example:

{
    "Game": "bgg_003",
    "text": "You can plan your strategy perfectly, but in the end, the dice rolls determine the winner. The cardboard tokens also feel a bit cheap and flimsy.",
    "annotations": [
      {
        "aspect": "luck",
        "sentiment": "negative"
      },
      {
        "aspect": "components",
        "sentiment": "negative"
      }
    ]
  }"""
)

# 1. Load the dataset
# Replace 'cleaned_reviews.csv' with the actual path to your file
try:
    # ✅ FIX 2: .dropna() adicionado para ignorar linhas vazias (evita erro 'nan')
    df = pd.read_csv('cleaned_reviews.csv').dropna(subset=['Game', 'Review'])
    print("✓ CSV file loaded successfully.\n")
except FileNotFoundError:
    # Creating a dummy dataset so the script runs without errors if the file is missing
    print("⚠ 'cleaned_reviews.csv' not found. Creating a temporary dataset instead...\n")
    # ✅ BÔNUS FIX: Colunas corrigidas para bater com o loop ('Game' e 'Review')
    data = {
        'Game': ['bgg_001', 'bgg_002'],
        'Review': ['The rules are terrible but the components are amazing!', 'A very lucky game with good replayability.']
    }
    df = pd.DataFrame(data)

dataset_anotado = []

# 3. Loop para anotar os dados
for index, row in df.iterrows():
    # Garantindo que o texto seja tratado como string para evitar falhas
    texto_review = str(row['Review']).strip()
    
    try:
        # Envia a review para o Gemini
        response = model.generate_content(f"Analise esta review: '{texto_review}'")
        
        # Como forçamos o mime_type, a resposta já é uma string JSON pura
        anotacoes_json = json.loads(response.text)
        
        # Monta o registro no formato que criamos anteriormente
        registro = {
            "Game": str(row['Game']).strip(),
            "text": texto_review,
            "annotations": anotacoes_json.get("annotations", [])
        }
        dataset_anotado.append(registro)
        
        print(f"✅ Sucesso na review {row['Game']}")
        
        # Pequena pausa para evitar limites de taxa (Rate Limit) da API gratuita
        time.sleep(2) 
        
    except Exception as e:
        print(f"❌ Erro na review {row['Game']}: {e}")

# 4. Salva o resultado final no arquivo pronto para a Hugging Face
with open("meu_dataset_gemini.json", "w", encoding="utf-8") as f:
    json.dump(dataset_anotado, f, ensure_ascii=False, indent=2)

