import mysql.connector
from mysql.connector import Error

# --- CONEXÃO COM O BANCO DE DADOS ---


def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="*******",
            database="instituto_livre_acesso"
        )
        return conexao
    except Error as e:
        print(f"\n[ERRO DE CONEXÃO] Não foi possível conectar ao banco: {e}")
        return None


# --- 1. CADASTRAR ALUNO E MATRICULAR LOGO EM SEGUIDA ---

# --- 1. CADASTRAR ALUNO (CRIANÇA) E MATRICULAR LOGO EM SEGUIDA ---

def cadastrar_aluno():
    print("\n--- CADASTRO DE ALUNO (CRIANÇA) ---")
    nome = input("Nome da criança: ")
    
    try:
        idade = int(input("Idade da criança: "))
    except ValueError:
        print("\n❌ Idade inválida. Introduza apenas números.")
        return

    nome_responsavel = input("Nome do responsável (Pai/Mãe/Tutor): ")
    email = input("E-mail do responsável: ")
    telefone = input("Telefone/WhatsApp do responsável: ")
    senha = input("Senha para acesso ao site: ")

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        sql = """
            INSERT INTO alunos (nome, idade, nome_responsavel, email, telefone, senha) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (nome, idade, nome_responsavel, email, telefone, senha)
        try:
            cursor.execute(sql, val)
            conexao.commit()

            aluno_id = cursor.lastrowid
            print(f"\n✅ Criança '{nome}' ({idade} anos) cadastrada com sucesso! (ID do Aluno: {aluno_id})")

            opcao_matricular = input("\nDeseja matricular esta criança em uma turma agora? (s/n): ").strip().lower()

            if opcao_matricular == 's':
                cursor.close()
                conexao.close()
                listar_horarios_aulas()
                agendar_horario(aluno_id_direto=aluno_id)
                return

        except Error as e:
            print(f"\n❌ Erro ao cadastrar aluno: {e}")
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

# --- 2. CADASTRAR TURMA ---

def cadastrar_turma():
    print("\n--- CADASTRO DE TURMA ---")
    nome_curso = input("Nome do Curso/Atividade (ex: Jiu Jitsu, Balé): ")
    instrutor = input(
        "Instrutor/Coordenador (ex: Prof. Glauber, Márcia Ribeiro): ")
    dia_semana = input("Dias da semana (ex: Terça e Quinta, Sexta): ")
    horario_inicio = input("Horário de Início (ex: 16:00:00 ou 08:00:00): ")
    horario_fim = input("Horário de Fim (ex: 17:00:00 ou 09:30:00): ")
    limite = input("Limite de vagas (padrão 20): ")
    limite_vagas = int(limite) if limite.strip().isdigit() else 20

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        sql = """
            INSERT INTO turmas (nome_curso, instrutor, dia_semana, horario_inicio, horario_fim, limite_vagas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (nome_curso, instrutor, dia_semana,
               horario_inicio, horario_fim, limite_vagas)
        try:
            cursor.execute(sql, val)
            conexao.commit()
            print(f"\n✅ Turma de '{nome_curso}' cadastrada com sucesso!")
        except Error as e:
            print(f"\n❌ Erro ao cadastrar turma: {e}")
        finally:
            cursor.close()
            conexao.close()


# --- 3. VER HORÁRIOS DE AULAS ---

def listar_horarios_aulas():
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        sql = "SELECT id, nome_curso, instrutor, dia_semana, horario_inicio, horario_fim, limite_vagas, vagas_ocupadas FROM turmas"
        try:
            cursor.execute(sql)
            turmas = cursor.fetchall()
            if not turmas:
                print("\nNenhuma turma cadastrada no momento.")
            else:
                print("\n" + "="*80)
                print("                     TURMAS E HORÁRIOS DISPONÍVEIS")
                print("="*80)
                for t in turmas:
                    print(
                        f"ID: {t['id']} | Curso: {t['nome_curso']} | Prof: {t['instrutor']}")
                    print(
                        f"Dias: {t['dia_semana']} | Horário: {t['horario_inicio']} às {t['horario_fim']}")
                    print(
                        f"Vagas Ocupadas: {t['vagas_ocupadas']}/{t['limite_vagas']}")
                    print("-" * 80)
        except Error as e:
            print(f"\n❌ Erro ao buscar turmas: {e}")
        finally:
            cursor.close()
            conexao.close()


# --- 4. MARCAR / AGENDAR HORÁRIO PARA ALUNO ---

def agendar_horario(aluno_id_direto=None):
    print("\n--- AGENDAMENTO / MATRÍCULA EM TURMA ---")
    try:
        if aluno_id_direto:
            aluno_id = aluno_id_direto
        else:
            aluno_id = int(input("ID do Aluno: "))

        turma_id = int(input("Digite o ID da Turma desejada: "))
    except ValueError:
        print("\n❌ ID inválido. Digite apenas números inteiros.")
        return

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            # Verifica se a turma existe e se tem vaga disponível
            cursor.execute(
                "SELECT vagas_ocupadas, limite_vagas FROM turmas WHERE id = %s", (turma_id,))
            turma = cursor.fetchone()

            if not turma:
                print("\n❌ Turma não encontrada.")
                return

            if turma['vagas_ocupadas'] >= turma['limite_vagas']:
                print("\n❌ Turma lotada! Não há vagas disponíveis.")
                return

            # Efetua o registro na tabela AGENDAMENTOS
            sql_agendar = "INSERT INTO agendamentos (aluno_id, turma_id) VALUES (%s, %s)"
            cursor.execute(sql_agendar, (aluno_id, turma_id))

            # Atualiza a contagem de vagas ocupadas na tabela TURMAS
            sql_update = "UPDATE turmas SET vagas_ocupadas = vagas_ocupadas + 1 WHERE id = %s"
            cursor.execute(sql_update, (turma_id,))

            conexao.commit()
            print(
                f"\n✅ Matrícula do Aluno ID {aluno_id} na Turma ID {turma_id} salva na tabela 'agendamentos' com sucesso!")
        except Error as e:
            conexao.rollback()
            if e.errno == 1062:  # Erro de chave duplicada (UNIQUE)
                print("\n❌ Este aluno já está matriculado nesta turma!")
            else:
                print(f"\n❌ Erro ao realizar agendamento: {e}")
        finally:
            cursor.close()
            conexao.close()


# --- 5. VER ALUNOS DE UMA TURMA ---

# --- 5. VER ALUNOS DE UMA TURMA ---

def ver_alunos_da_turma():
    print("\n--- CONTROLE DE ALUNOS POR TURMA ---")
    try:
        turma_id = int(input("Digite o ID da Turma: "))
    except ValueError:
        print("\n❌ ID inválido.")
        return

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT a.id, a.nome, a.idade, a.nome_responsavel, a.email, a.telefone, ag.status
            FROM agendamentos ag
            JOIN alunos a ON ag.aluno_id = a.id
            WHERE ag.turma_id = %s
        """
        try:
            cursor.execute(sql, (turma_id,))
            alunos = cursor.fetchall()

            if not alunos:
                print(f"\nNenhum aluno matriculado na turma ID {turma_id}.")
            else:
                print(f"\n--- ALUNOS MATRICULADOS NA TURMA {turma_id} ---")
                for a in alunos:
                    print(
                        f"ID: {a['id']} | Aluno(a): {a['nome']} ({a['idade']} anos) | "
                        f"Responsável: {a['nome_responsavel']} | Tel: {a['telefone']}"
                    )
        except Error as e:
            print(f"\n❌ Erro ao consultar alunos: {e}")
        finally:
            cursor.close()
            conexao.close()

 # --- 6. EXCLUIR TURMA ---

def excluir_turma():
    print("\n--- EXCLUSÃO DE TURMA ---")
    try:
        turma_id = int(input("Digite o ID da Turma que deseja excluir: "))
    except ValueError:
        print("\n❌ ID inválido. Digite apenas números inteiros.")
        return

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            # 1. Verifica se a turma existe
            cursor.execute("SELECT nome_curso FROM turmas WHERE id = %s", (turma_id,))
            turma = cursor.fetchone()

            if not turma:
                print(f"\n❌ Nenhuma turma encontrada com o ID {turma_id}.")
                return

            # Confirmação de segurança
            confirmacao = input(f"Tem certeza que deseja excluir a turma '{turma['nome_curso']}' (ID: {turma_id})? (s/n): ").strip().lower()

            if confirmacao == 's':
                # Deleta a turma (os agendamentos vinculados serão deletados via CASCADE)
                sql_deletar = "DELETE FROM turmas WHERE id = %s"
                cursor.execute(sql_deletar, (turma_id,))
                conexao.commit()
                print(f"\n✅ Turma '{turma['nome_curso']}' (ID: {turma_id}) excluída com sucesso!")
            else:
                print("\nOpção cancelada. A turma não foi excluída.")

        except Error as e:
            conexao.rollback()
            print(f"\n❌ Erro ao excluir turma: {e}")
        finally:
            cursor.close()
            conexao.close()

# --- 7. CANCELAR MATRÍCULA DE UM ALUNO ---

def cancelar_matricula():
    print("\n--- CANCELAMENTO DE MATRÍCULA ---")
    try:
        aluno_id = int(input("Digite o ID do Aluno: "))
        turma_id = int(input("Digite o ID da Turma para cancelar a matrícula: "))
    except ValueError:
        print("\n❌ ID inválido. Digite apenas números inteiros.")
        return

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            # 1. Verifica se a matrícula existe
            cursor.execute(
                "SELECT * FROM agendamentos WHERE aluno_id = %s AND turma_id = %s",
                (aluno_id, turma_id)
            )
            agendamento = cursor.fetchone()

            if not agendamento:
                print(f"\n❌ Matrícula do Aluno ID {aluno_id} na Turma ID {turma_id} não foi encontrada.")
                return

            # Confirmação
            confirmacao = input(f"Tem certeza que deseja cancelar a matrícula do Aluno ID {aluno_id} na Turma ID {turma_id}? (s/n): ").strip().lower()

            if confirmacao == 's':
                # Remove o agendamento/matrícula
                cursor.execute(
                    "DELETE FROM agendamentos WHERE aluno_id = %s AND turma_id = %s",
                    (aluno_id, turma_id)
                )

                # Libera uma vaga na tabela turmas
                cursor.execute(
                    "UPDATE turmas SET vagas_ocupadas = GREATEST(0, vagas_ocupadas - 1) WHERE id = %s",
                    (turma_id,)
                )

                conexao.commit()
                print(f"\n✅ Matrícula cancelada com sucesso! Vaga liberada na turma {turma_id}.")
            else:
                print("\nOperação cancelada.")

        except Error as e:
            conexao.rollback()
            print(f"\n❌ Erro ao cancelar matrícula: {e}")
        finally:
            cursor.close()
            conexao.close()

# --- 8. EXCLUIR ALUNO DO SISTEMA ---

def excluir_aluno():
    print("\n--- EXCLUSÃO DE ALUNO ---")
    try:
        aluno_id = int(input("Digite o ID do Aluno que deseja excluir: "))
    except ValueError:
        print("\n❌ ID inválido. Digite apenas números inteiros.")
        return

    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            # 1. Busca os dados do aluno
            cursor.execute("SELECT nome FROM alunos WHERE id = %s", (aluno_id,))
            aluno = cursor.fetchone()

            if not aluno:
                print(f"\n❌ Nenhum aluno encontrado com o ID {aluno_id}.")
                return

            confirmacao = input(f"Tem certeza que deseja excluir o cadastro de '{aluno['nome']}' (ID: {aluno_id})? Isso removerá todas as suas matrículas. (s/n): ").strip().lower()

            if confirmacao == 's':
                # Abater 1 vaga das turmas onde ele estava matriculado antes de deletar
                cursor.execute("SELECT turma_id FROM agendamentos WHERE aluno_id = %s", (aluno_id,))
                turmas_aluno = cursor.fetchall()

                for t in turmas_aluno:
                    cursor.execute(
                        "UPDATE turmas SET vagas_ocupadas = GREATEST(0, vagas_ocupadas - 1) WHERE id = %s",
                        (t['turma_id'],)
                    )

                # Remove as matrículas
                cursor.execute("DELETE FROM agendamentos WHERE aluno_id = %s", (aluno_id,))

                # Deleta o cadastro do aluno
                cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))

                conexao.commit()
                print(f"\n✅ Cadastro de '{aluno['nome']}' excluído com sucesso do sistema!")
            else:
                print("\nOperação cancelada.")

        except Error as e:
            conexao.rollback()
            print(f"\n❌ Erro ao excluir aluno: {e}")
        finally:
            cursor.close()
            conexao.close()


def menu():
    while True:
        print("\n==================================")
        print("  INSTITUTO LIVRE ACESSO - SISTEMA")
        print("==================================")
        print("1. Cadastrar Aluno")
        print("2. Cadastrar Turma")
        print("3. Ver Horários de Aulas")
        print("4. Marcar/Agendar Horário para Aluno")
        print("5. Ver Alunos de uma Turma (Controle)")
        print("6. Excluir Turma")
        print("7. Cancelar Matrícula em Turma")
        print("8. Excluir Aluno do Sistema")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_aluno()
        elif opcao == '2':
            cadastrar_turma()
        elif opcao == '3':
            listar_horarios_aulas()
        elif opcao == '4':
            agendar_horario()
        elif opcao == '5':
            ver_alunos_da_turma()
        elif opcao == '6':
            excluir_turma()
        elif opcao == '7':
            cancelar_matricula()
        elif opcao == '8':
            excluir_aluno()
        elif opcao == '0':
            print("\nSaindo do sistema... Até mais!")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
