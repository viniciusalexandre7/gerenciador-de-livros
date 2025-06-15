import os
import json
import requests
import urllib.parse

class Livro:

    def __init__(self, titulo, autor, ano_publicado, status="quero ler"):
        
        self.titulo = titulo
        self.autor = autor
        self.ano_publicado = ano_publicado
        self.status = status

    def __str__(self):
        return f"{self.titulo} por {self.autor} ({self.ano_publicado}) - Status: {self.status}"


class Biblioteca:

    def __init__(self, nome_arquivo="biblioteca.json"):

        self.livros = []
        self.nome_arquivo = nome_arquivo
        self.carregar_de_json()

    def adicionar_livro(self, livro_obj):

        if any(not campo.strip() for campo in [livro_obj.titulo, livro_obj.autor, livro_obj.ano_publicado]):
            print("Erro: Todos os campos devem ser preenchidos corretamente.")
            return False

        self.livros.append(livro_obj)
        return True

    def listar_livros(self):
        return self.livros


    def salvar_em_json(self):

        salvamento_dos_dados = [{ 
        "titulo":livro.titulo,
        "autor":livro.autor,
        "ano_publicado":livro.ano_publicado,
        "status":livro.status}
        
        for livro in self.livros

        ]

        with open(self.nome_arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(salvamento_dos_dados, arquivo_json, indent=4)

        print(f"Biblioteca salva em {self.nome_arquivo} com sucesso")


    def carregar_de_json(self):

        if os.path.exists(self.nome_arquivo):

            try:
                with open(self.nome_arquivo, "r", encoding="utf-8") as arquivo_json:
                    dados_lido_do_arquivo = json.load(arquivo_json)

                    for dados in dados_lido_do_arquivo:
                        novo_livro = Livro(dados["titulo"], dados["autor"], dados["ano_publicado"], dados["status"])
                        self.livros.append(novo_livro)

            except json.JSONDecodeError:
                pass

    
    #================
    #   Interface
    #================


def gerenciar_adicao(biblioteca_obj):

    print("\n--- Adicionar Novo Livro ---")

    titulo = input("Digite o título do livro que deseja buscar: ").strip()
    titulo_formato = urllib.parse.quote(titulo)
    
    url_da_api = f"https://www.googleapis.com/books/v1/volumes?q={titulo_formato}"

    try:

        print("Buscando online...")
        response = requests.get(url_da_api)

        #verifica se a resposta foi um sucesso ou um erro, se for erro vai levantar uma exceção http
        response.raise_for_status()
        dados = response.json()

        if 'items' in dados and dados['items']:

            livros_encontrados_api = dados['items']
            print("\n--- Livros Encontrados ---")
            print("Por favor, escolha um da lista abaixo:")

            for i, livro_api in enumerate(livros_encontrados_api[:5], start=1):

                info = livro_api.get('volumeInfo', {})

                titulo_livro = info.get('title', 'Título não disponível')
                lista_de_autores = info.get('authors', ['Autor desconhecido'])
                primeiro_autor = lista_de_autores[0]
                data_completa = info.get('publishedDate', '0000')
                ano = data_completa[:4]

                print(f"{i}: {titulo_livro}({ano}) por {primeiro_autor}")
            
            try:
                escolha = 1 if len(livros_encontrados_api) == 1 else int(input(f"\nDigite o número do livro que deseja adicionar (1-{len(livros_encontrados_api[:5])}): " ))

                if not(1 <= escolha <= len(livros_encontrados_api[:5])):
                    print("Escolha inválida. Fora do intervalo de opções.")
                    return

                livro_escolhido_dict = livros_encontrados_api[escolha - 1]
                

                info = livro_escolhido_dict.get('volumeInfo', {})
                titulo = info.get('title', 'Título Desconhecido')
                autores = info.get('authors', ['Autor Desconhecido'])
                autor = autores[0]
                data_publicacao = info.get('publishedDate', '0000')
                ano = data_publicacao[:4]

                print(f"Você escolheu: {titulo} de {autor}")

                novo_livro = Livro(titulo=titulo, autor=autor, ano_publicado=ano)

                confirmar = input(f"Tem certeza que deseja adcionar? (s/n): ").lower().strip()

                if confirmar == "s":
                    if biblioteca_obj.adicionar_livro(novo_livro):
                        print("Livro adicionado com Sucesso!")
                    else:
                        print("Erro ao adicionar livro. Verifique os dados e tente novamente.")
                else:
                    print("O livro não foi adicionado")

            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")
        else:
            print(f"Nenhum livro encontrado com o título '{titulo}'.")


    #pega erros de conexão, timeout, URL inválida, e também os erros do raise_for_status
    except requests.exceptions.RequestException as error:
        print(f"Erro de conexão ou com a requisição: {error}")
    
    #pega o erro que acontece se o response.json falhar
    except json.JSONDecodeError:
        print("Erro: A resposta do servidor não é um JSON válido.")
        return



def gerenciar_biblioteca(biblioteca_obj):

    print("\n--- Minha Biblioteca ---")
    livros = biblioteca_obj.listar_livros()

    if not livros:
        print("Sua biblioteca está vazia.")
        return
        
    for livro in livros:
        print(f"- {livro}")


    #================
    #   Executor
    #================

    
def main():

    biblioteca = Biblioteca()

    while True:
        print("\n==== MENU DA BIBLIOTECA ====")
        print("1. Adicionar Livro")
        print("2. Listar Livros")
        print("0. Sair")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            gerenciar_adicao(biblioteca)

        elif escolha == '2':
            gerenciar_biblioteca(biblioteca)

        elif escolha == '0':
            print("Salvando biblioteca antes de sair...")
            biblioteca.salvar_em_json()
            print("Saindo...")
            break

        else:
            print("Opção inválida.")



if __name__ == "__main__":
    main()