import os
import sqlite3
from tkinter import Tk
from tkinter.filedialog import askdirectory


# Função para inicializar o banco de dados e garantir que as tabelas existem
def initialize_database():
    conn = sqlite3.connect("photographers.db")
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


# Função para limpar o banco de dados e recriar as tabelas
def reset_database():
    conn, cursor = initialize_database()

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
    print("Banco de dados limpo e reinicializado com sucesso.")


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
def process_folders(directory_path):
    conn, cursor = initialize_database()

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
def compare_selected_photos(selected_folder_path):
    conn = sqlite3.connect("photographers.db")
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
        print("Escolha uma opção:")
        print("1. Limpar e reinicializar o banco de dados")
        print("2. Processar pastas de fotógrafos")
        print("3. Comparar fotos selecionadas pelos clientes")
        print("4. Sair")

        option = input("Digite a opção desejada: ")

        if option == "1":
            reset_database()
        elif option == "2":
            directory_path = select_folder()
            if directory_path:
                process_folders(directory_path)
            else:
                print("Nenhuma pasta foi selecionada.")
        elif option == "3":
            selected_folder_path = select_folder()
            if selected_folder_path:
                compare_selected_photos(selected_folder_path)
            else:
                print("Nenhuma pasta foi selecionada.")
        elif option == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
