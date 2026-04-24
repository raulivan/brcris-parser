import csv
import json

if __name__ == "__main__":
    conjunto_lattes = []
    conjunto_grupos_pesquisa = []
    temp_conjunto_lattes = None
    temp_conjunto_grupos_pesquisa = {}

    with open(r'.\src\data\ids_lattes2026.csv', mode='r', encoding='utf-8') as f:
                # O arquivo é um JSON array de objetos
                temp_conjunto_lattes = list(csv.DictReader(f))

    for item in temp_conjunto_lattes:
        conjunto_lattes.append(item['id'])

    with open(r'.\src\data\output\person_grupos_pesquisa.json', 'r', encoding='utf-8') as f:
        # O arquivo é um JSON array de objetos
        temp_conjunto_grupos_pesquisa = json.load(f)

    for k in temp_conjunto_grupos_pesquisa:
        conjunto_grupos_pesquisa.append(k)


    sobraram = set(conjunto_grupos_pesquisa) - set(conjunto_lattes)

    with open('PESSOAS_INVALIDAS.txt', 'w', encoding='utf-8') as ficheiro:
        for item in sobraram:
            ficheiro.write(f"{item}\n")

