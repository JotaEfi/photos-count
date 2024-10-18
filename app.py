import os
import sqlite3
from tkinter import Tk
from tkinter.filedialog import askdirectory


# Função para inicializar o banco de dados de um evento específico
def initialize_database(db_name):
    conn = sqlite3.connect(f"{db_name}.db")
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS photographers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        selected_count INTEGER DEFAULT 0)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS photos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT NOT NULL UNIQUE,
                        photographer_id INTEGER,
                        FOREIGN KEY (photographer_id) REFERENCES photographers(id))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS selected_photos (
                        photographer_id INTEGER,
                        file_name TEXT NOT NULL,
                        FOREIGN KEY (photographer_id) REFERENCES photographers(id))"""
    )

    conn.commit()
    return conn, cursor


# Função para listar eventos existentes (bancos de dados)
def list_events():
    databases = [f for f in os.listdir() if f.endswith(".db")]
    events = [db.replace(".db", "") for db in databases]
    return events


# Função para selecionar ou criar um evento
# Função para selecionar ou criar um evento
def select_event():
    while True:
        events = list_events()
        if events:
            print("\nEventos disponíveis:")
            for i, event in enumerate(events):
                print(f"{i + 1}. {event}")
        else:
            print("Nenhum evento disponível.")

        print(f"{len(events) + 1}. Criar novo evento")
        print(f"{len(events) + 2}. Sair")

        option = input(
            "Digite o número do evento ou a opção para criar um novo evento: "
        )

        if option.isdigit():
            option = int(option)
            if 1 <= option <= len(events):
                return events[option - 1]  # Retorna o nome do evento selecionado
            elif option == len(events) + 1:
                event_name = input("Digite o nome do novo evento: ")
                if event_name:
                    # Criar imediatamente o banco de dados do novo evento
                    initialize_database(
                        event_name
                    )  # Inicializa o banco de dados para garantir que ele seja criado
                    return event_name  # Retorna o nome do novo evento
            elif option == len(events) + 2:
                print("Saindo do programa.")
                exit()  # Finaliza o programa
        print("Opção inválida. Tente novamente.")


# Função para limpar o banco de dados de um evento
def reset_database(db_name):
    conn, cursor = initialize_database(db_name)

    # Apagar as tabelas existentes
    cursor.execute("DROP TABLE IF EXISTS photographers")
    cursor.execute("DROP TABLE IF EXISTS photos")
    cursor.execute("DROP TABLE IF EXISTS selected_photos")

    # Recriar as tabelas
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS photographers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        selected_count INTEGER DEFAULT 0)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS photos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT NOT NULL UNIQUE,
                        photographer_id INTEGER,
                        FOREIGN KEY (photographer_id) REFERENCES photographers(id))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS selected_photos (
                        photographer_id INTEGER,
                        file_name TEXT NOT NULL,
                        FOREIGN KEY (photographer_id) REFERENCES photographers(id))"""
    )

    conn.commit()
    conn.close()
    print(f"Banco de dados do evento '{db_name}' limpo e reinicializado com sucesso.")


# Função para adicionar fotógrafo
def add_photographer(cursor, conn, name):
    cursor.execute("INSERT OR IGNORE INTO photographers (name) VALUES (?)", (name,))
    conn.commit()


# Função para adicionar fotos
def add_photo(cursor, conn, file_name, photographer_name):
    cursor.execute("SELECT id FROM photographers WHERE name=?", (photographer_name,))
    photographer_id = cursor.fetchone()

    if photographer_id:
        photographer_id = photographer_id[0]
        cursor.execute(
            "INSERT OR IGNORE INTO photos (file_name, photographer_id) VALUES (?, ?)",
            (file_name, photographer_id),
        )
        conn.commit()


# Função para processar as pastas e registrar os fotógrafos e suas fotos
def process_folders(directory_path, db_name):
    conn, cursor = initialize_database(db_name)

    for folder_name in os.listdir(directory_path):
        photographer_folder_path = os.path.join(directory_path, folder_name)

        if os.path.isdir(photographer_folder_path):
            # Registrar fotógrafo
            add_photographer(cursor, conn, folder_name)

            # Registrar fotos na pasta
            for file_name in os.listdir(photographer_folder_path):
                if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    add_photo(cursor, conn, file_name, folder_name)

    conn.close()


# Função para comparar fotos selecionadas pelos clientes com as fotos dos fotógrafos
def compare_selected_photos(selected_folder_path, db_name):
    conn = sqlite3.connect(f"{db_name}.db")
    cursor = conn.cursor()

    # Usar um conjunto para armazenar fotos únicas selecionadas
    selected_photos_set = set()

    for selected_folder in os.listdir(selected_folder_path):
        selected_photographer_folder = os.path.join(
            selected_folder_path, selected_folder
        )

        if os.path.isdir(selected_photographer_folder):
            for file_name in os.listdir(selected_photographer_folder):
                if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    selected_photos_set.add(file_name)

    # Atualizar a contagem de fotos selecionadas para cada fotógrafo
    for file_name in selected_photos_set:
        cursor.execute(
            """SELECT photographer_id FROM photos 
                          WHERE file_name=?""",
            (file_name,),
        )
        result = cursor.fetchone()

        if result:
            photographer_id = result[0]
            cursor.execute(
                """INSERT OR IGNORE INTO selected_photos (photographer_id, file_name)
                              VALUES (?, ?)""",
                (photographer_id, file_name),
            )
            cursor.execute(
                """UPDATE photographers 
                              SET selected_count = (SELECT COUNT(DISTINCT file_name) 
                                                    FROM selected_photos 
                                                    WHERE photographer_id = ?) 
                              WHERE id = ?""",
                (photographer_id, photographer_id),
            )
            conn.commit()

    # Exibir a quantidade total de fotos selecionadas para cada fotógrafo
    cursor.execute("""SELECT name, selected_count FROM photographers""")
    photographers = cursor.fetchall()
    print("\nTotal de fotos selecionadas por fotógrafo:")
    for photographer in photographers:
        print(f"{photographer[0]}: {photographer[1]} fotos selecionadas")

    conn.close()


# Função para selecionar a pasta via tkinter
def select_folder():
    Tk().withdraw()  # Oculta a janela principal do Tkinter
    folder_selected = askdirectory(title="Selecione a pasta")
    return folder_selected


# Função principal
if __name__ == "__main__":
    while True:
        db_name = select_event()  # Pergunta qual evento usar ou criar um novo evento

        while True:
            print(f"\nBanco de dados em uso: {db_name}")
            print("Escolha uma opção:")
            print("1. Limpar e reinicializar o banco de dados")
            print("2. Processar pastas de fotógrafos")
            print("3. Comparar fotos selecionadas pelos clientes")
            print("4. Voltar para seleção de eventos")

            option = input("Digite a opção desejada: ")

            if option == "1":
                reset_database(db_name)
            elif option == "2":
                directory_path = select_folder()
                if directory_path:
                    process_folders(directory_path, db_name)
                else:
                    print("Nenhuma pasta foi selecionada.")
            elif option == "3":
                selected_folder_path = select_folder()
                if selected_folder_path:
                    compare_selected_photos(selected_folder_path, db_name)
                else:
                    print("Nenhuma pasta foi selecionada.")
            elif option == "4":
                break  # Volta para a seleção de eventos
            else:
                print("Opção inválida. Tente novamente.")
