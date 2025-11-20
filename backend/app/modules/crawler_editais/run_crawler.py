import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import requests
import os

# Configurações
API_URL = 'http://localhost:8000/api/editais/' 
JSON_FILE = 'editais.json' 
HEADERS = {'Content-Type': 'application/json'}  

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl('editais') 
    process.start()  

def send_to_api(edital_data):
    try:
        response = requests.post(API_URL, json=edital_data, headers=HEADERS)
        if response.status_code == 201:  # Sucesso (Created)
            print(f"Edital enviado com sucesso: {edital_data.get('titulo')}")
        else:
            print(f"Erro ao enviar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

def integrate_with_apoema():
    if not os.path.exists(JSON_FILE):
        print("Arquivo JSON não encontrado. Execute o spider primeiro.")
        return
    
    with open(JSON_FILE, 'r') as f:
        for line in f:
            edital = json.loads(line.strip())
          
            send_to_api(edital)

if __name__ == '__main__':
    print("Executando crawler...")
    run_spider()
    print("Integrando com Apoema...")
    integrate_with_apoema()
    print("Integração concluída.")
