"""Appel de l'agent ALMPilot depuis Python, avec le SDK Microsoft Foundry.

L'agent garde dans le portail ses instructions, son moteur de calcul, ses données
et sa politique : ce script lui envoie simplement deux questions dans la même
conversation, puis affiche ses réponses.

Prérequis, depuis la racine du dépôt :
    pip install -r agent/requirements.txt
    az login
Puis collez le point de terminaison de votre projet (page Accueil du projet Foundry)
dans POINT_DE_TERMINAISON, et lancez :
    python agent/appel_agent.py
"""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

POINT_DE_TERMINAISON = "https://VOTRE-RESSOURCE.services.ai.azure.com/api/projects/proj-riskpilot"
NOM_AGENT = "almpilot-ble"

projet = AIProjectClient(endpoint=POINT_DE_TERMINAISON, credential=DefaultAzureCredential())

# Client relié à l'agent : instructions, moteur de calcul, données et politique sont ceux du portail
client = projet.get_openai_client(agent_name=NOM_AGENT)
conversation = client.conversations.create()

print("Question 1 : note ALM complète (environ 30 secondes)\n")
reponse = client.responses.create(
    conversation=conversation.id,
    input="Rédige la note ALM complète pour le Comité ALM.",
)
print(reponse.output_text)

# Question de suivi dans la même conversation : l'agent garde le contexte
print("\n\nQuestion 2 : simulation\n")
suite = client.responses.create(
    conversation=conversation.id,
    input="Simule la résiliation du swap de couverture H01 : que deviennent la perte d'EVE et la perte de MNI ?",
)
print(suite.output_text)
