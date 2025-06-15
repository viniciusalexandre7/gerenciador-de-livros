import os
import json

class Livro:

    def __init__(self, titulo, autor, ano_publicado, status="quero ler"):
        
        self.titulo = titulo
        self.autor = autor
        self.ano_publicado = ano_publicado
        self.status = status

    def __str__(self):
        return f"'{self.titulo}' por {self.autor} ({self.ano_publicado}) - Status: {self.status}"


class Biblioteca:

    def __init__(self, nome_arquivo="biblioteca.json"):

        self.livros = []
        self.nome_arquivo = nome_arquivo
        #self.carregar_de_json()
        pass

    def adicionar_livro(self, livro_obj):

        if any(not campo.strip() for campo in [livro_obj.titulo, livro_obj.autor, livro_obj.ano_publicado]):
            print("Erro: Todos os campos devem ser preenchidos corretamente.")
            return False

        self.livros.append(livro_obj)
        return True

    def listar_livros(self):
        return self.livros

    
    #================
    #   Interface
    #================


def gerenciar_adicao(biblioteca_obj):

    print("\n--- Adicionar Novo Livro ---")

    titulo = input("Digite o título do livro: ")
    autor = input("Digite o nome do autor do livro: ")
    ano = input("Digite o ano do livro: ")


    novo_livro = Livro(titulo, autor, ano)

    if biblioteca_obj.adicionar_livro(novo_livro):
        print("Livro adicionado com Sucesso!")
    else:
        print("Erro ao adicionar livro. Verifique os dados e tente novamente.")

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
            print("Saindo...")
            break

        else:
            print("Opção inválida.")



if __name__ == "__main__":
    main()