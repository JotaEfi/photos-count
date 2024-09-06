# Contador de Fotos

Este projeto é um programa em Python feito com GPT para gerenciar e contar fotos selecionadas pelos clientes e associar essas fotos aos fotógrafos cadastrados. O banco de dados é utilizado para armazenar informações sobre fotógrafos, suas fotos e a contagem de fotos selecionadas.

## Funcionalidades

- **Adicionar fotógrafos e suas fotos**: Processa pastas de fotógrafos e registra os fotógrafos e suas fotos no banco de dados.
- **Comparar fotos selecionadas pelos clientes**: Compara as fotos selecionadas pelos clientes com as fotos dos fotógrafos e atualiza a contagem de fotos selecionadas para cada fotógrafo.
- **Resetar o banco de dados**: Limpa e reinicializa o banco de dados quando necessário.

## Requisitos

Certifique-se de ter as seguintes bibliotecas instaladas:

- `sqlite3` (incluso na biblioteca padrão do Python)
- `tkinter` (incluso na biblioteca padrão do Python)

### Instalação

1. **Crie e ative um ambiente virtual** (opcional, mas recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

2. **Instale as dependências** (não são necessárias bibliotecas externas além das padrão):

   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o script**:
   ```bash
   python app.py
   ```

## Uso

1. **Limpar e reinicializar o banco de dados**:

   - Escolha a opção `1` no menu principal para limpar e recriar o banco de dados.

2. **Processar pastas de fotógrafos**:

   - Escolha a opção `2` no menu principal e selecione a pasta que contém as pastas dos fotógrafos. Cada pasta deve estar nomeada com o nome do fotógrafo e conter fotos com extensões `.jpg`, `.jpeg`, ou `.png`.

3. **Comparar fotos selecionadas pelos clientes**:

   - Escolha a opção `3` no menu principal e selecione a pasta que contém as pastas dos clientes. Cada pasta pode conter fotos selecionadas pelos clientes.

4. **Sair**:
   - Escolha a opção `4` para sair do programa.

## Nota

- **Reset do banco de dados**: O banco de dados precisa ser reinicializado toda vez que o conjunto de dados for alterado para garantir que as informações estejam atualizadas. Isso é feito usando a opção `1` no menu principal.

## Contribuição

Sinta-se à vontade para contribuir com melhorias, relatórios de bugs ou novas funcionalidades.

---

Obrigado por usar o projeto! Se precisar de mais assistência, entre em contato.
