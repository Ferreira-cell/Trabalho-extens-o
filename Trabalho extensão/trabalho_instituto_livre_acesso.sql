CREATE DATABASE IF NOT EXISTS instituto_livre_acesso;
USE instituto_livre_acesso;

-- 1. Tabela de Alunos / Usuários (Cadastro do site)
CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    senha VARCHAR(255) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Turmas (Controle de turmas e vagas)
CREATE TABLE IF NOT EXISTS turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_curso VARCHAR(100) NOT NULL,      -- Ex: Informática Básica, Libras, etc.
    instrutor VARCHAR(100),
    dia_semana VARCHAR(20) NOT NULL,       -- Ex: Segunda-feira, Quarta-feira
    horario_inicio TIME NOT NULL,           -- Ex: 14:00:00
    horario_fim TIME NOT NULL,              -- Ex: 16:00:00
    limite_vagas INT DEFAULT 20,
    vagas_ocupadas INT DEFAULT 0
);

-- 3. Tabela de Agendamentos / Matrículas (Vínculo do Aluno com a Turma)
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    turma_id INT NOT NULL,
    data_agendamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Confirmado', 'Cancelado') DEFAULT 'Confirmado',
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
    UNIQUE(aluno_id, turma_id) -- Impede o aluno de se cadastrar 2x na mesma turma
);

USE instituto_livre_acesso;

-- Adiciona a coluna idade na tabela de alunos
ALTER TABLE alunos ADD COLUMN idade INT AFTER nome;

-- (Opcional) Se quiseres guardar também o nome do pai/mãe/responsável:
ALTER TABLE alunos ADD COLUMN nome_responsavel VARCHAR(100) AFTER idade;

SELECT * FROM instituto_livre_acesso.turmas;
SELECT * FROM alunos;
SELECT * FROM agendamentos;
SELECT * FROM turmas;
