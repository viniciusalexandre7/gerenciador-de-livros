import os
import json
import requests
import urllib.parse


#Criação das Classes utilizadas
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

    #Metodo para adicionar um livro na biblioteca
    def adicionar_livro(self, livro_obj):

        if any(not campo.strip() for campo in [livro_obj.titulo, livro_obj.autor, livro_obj.ano_publicado]):
            print("Erro: Todos os campos devem ser preenchidos corretamente.")
            return False

        self.livros.append(livro_obj)
        return True

    #Metodo para retornar a listas de livros da biblioteca
    def listar_livros(self):
        return self.livros


    #Metodo para apagar um livro escolhido da biblioteca
    def apagar_livro(self, livro_deletar):

        if livro_deletar in self.livros:
            self.livros.remove(livro_deletar)
            return True
        return False


    #Metodo para salvar a lista de livros em um arquivo json
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

    #Metodo para carregar um json e transformar em uma lista de livros na biblioteca
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
        return None
        
    for i, livro in enumerate(livros, start=1):
        print(f"{i}- {livro}")
    
    return livros



def apagar_um_livro(biblioteca_obj):

    livros_encontrados = gerenciar_biblioteca(biblioteca_obj)

    if livros_encontrados is None:
        print("Não há livros adicionado na lista!")

    try:
        escolha = 1 if len(livros_encontrados) == 1 else int(input(f"Escolha o índice do livro que deseja excluir(1-{len(livros_encontrados)}):"))

        if not (1 <= escolha <= len(livros_encontrados)):
            print("Indice fora do intervalo")
            return


        livro_a_excluir = livros_encontrados[escolha-1]

        confirmar = input(f"Tem certeza que deseja excluir o livro '{livro_a_excluir.titulo}' da sua biblioteca? (s/n): ").strip().lower()

        if confirmar == "s":
            if biblioteca_obj.apagar_livro(livro_a_excluir):
                print("Livro excluido com sucesso!")
            else:
                print("Erro: O livro não foi encontrado na sua biblioteca para deleção.")
        else:
            print("Operação cancelada ")

    except ValueError:
        print("Entrada inválida. Por favor, digite um número.")
    

def mudar_status(biblioteca_obj):
    
    livros_encontrados = gerenciar_biblioteca(biblioteca_obj)

    if livros_encontrados is None:
        print("Não há livros adicionado na lista!")

    try:
        escolha = 1 if len(livros_encontrados) == 1 else int(input(f"Escolha o índice do livro que deseja mudar o status(1-{len(livros_encontrados)}):"))

        if not (1 <= escolha <= len(livros_encontrados)):
            print("Indice fora do intervalo")
            return

        livro_selecionado = livros_encontrados[escolha-1]

        print(f"Status atual do livro ({livro_selecionado.titulo} - Status: {livro_selecionado.status})")

        status_map = {
                1: "quero ler",
                2: "lendo",
                3: "lido"}

        escolha_status = int(input("Selecione o novo status do livro\n1- Quero ler\n2- Lendo\n3- Lido\nEscolha: "))


        if escolha_status in status_map:
            novo_status = status_map[escolha_status]
            livro_selecionado.status = novo_status
            print(f"Status do livro ({livro_selecionado.titulo}) definido como: {novo_status}")

        else:
            print("Escolha um índice válido")
            return

    except ValueError:
        print("Entrada inválida. Por favor, digite um número.")
    

def mostrar_status(biblioteca_obj):

    if not biblioteca_obj.livros:
        print("Sua biblioteca está vazia.")
        return
    
    livros_por_status = {}

    for livro in biblioteca_obj.livros:
        status_do_livro = livro.status

        if status_do_livro not in livros_por_status:
            livros_por_status[status_do_livro] = []
        
        livros_por_status[status_do_livro].append(livro)

    print(f"Você possui um total de {len(biblioteca_obj.livros)} livros na sua biblioteca")
    print("\nQuantidade atual de status de cada livro:")
  
    for status, lista_de_livros in livros_por_status.items():
        print(f"\nLivros com status ({status}): {len(lista_de_livros)}")
        for i, livro in enumerate(lista_de_livros, start=1):
            print(f"{i} - {livro.titulo}")



    #================
    #   Executor
    #================

    
def main():

    biblioteca = Biblioteca()

    while True:
        print("\n==== MENU DA BIBLIOTECA ====")
        print("1. Adicionar Livro")
        print("2. Listar Livros")
        print("3. Apagar Livros")
        print("4. Mostrar status dos livros")
        print("5. Mudar status de leitura")
        
        

        print("0. Sair")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            os.system("cls")
            gerenciar_adicao(biblioteca)

        elif escolha == '2':
            os.system("cls")
            gerenciar_biblioteca(biblioteca)

        elif escolha == '3':
            os.system("cls")
            apagar_um_livro(biblioteca)

        elif escolha == '4':
            os.system("cls")
            mostrar_status(biblioteca)

        elif escolha == '5':
            os.system("cls")
            mudar_status(biblioteca)

        elif escolha == '0':
            os.system("cls")
            print("Salvando biblioteca antes de sair...")
            biblioteca.salvar_em_json()
            print("Saindo...")
            break

        else:
            print("Opção inválida.")



if __name__ == "__main__":
    main()