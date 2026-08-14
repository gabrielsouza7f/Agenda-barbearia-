// src/controllers/orcamentoController.js
const ClienteModel = require('../models/ClienteModel');
const BarbeiroModel = require('../models/BarbeiroModel');
const ServicoModel = require('../models/ServicoModel');
const AgendamentoModel = require('../models/AgendamentoModel');
const bcrypt = require('bcryptjs');
const { validationResult } = require('express-validator');

class OrcamentoController {
    /**
     * POST /orcamento - Cria um novo agendamento
     * Valida consentimento LGPD obrigatório
     */
    async criarOrcamento(req, res) {
        try {
            // 1. Validação dos campos
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'Dados inválidos',
                    detalhes: errors.array()
                });
            }

            const {
                nome,
                email,
                telefone,
                senha,
                barbeiroId,
                servicoId,
                dataHora,
                aceitouLgpd
            } = req.body;

            // 2. VALIDAÇÃO LGPD - Obrigatório aceitar
            if (!aceitouLgpd) {
                return res.status(403).json({
                    error: 'Consentimento LGPD obrigatório',
                    message: 'É necessário aceitar os termos de privacidade para realizar o agendamento.',
                    artigo: 'Art. 8º da LGPD - Consentimento do titular'
                });
            }

            // 3. Verifica se barbeiro existe
            const barbeiro = await BarbeiroModel.findById(barbeiroId);
            if (!barbeiro) {
                return res.status(404).json({
                    error: 'Barbeiro não encontrado'
                });
            }

            // 4. Verifica se serviço existe
            const servico = await ServicoModel.findById(servicoId);
            if (!servico) {
                return res.status(404).json({
                    error: 'Serviço não encontrado'
                });
            }

            // 5. Verifica disponibilidade do barbeiro no horário
            const disponivel = await BarbeiroModel.verificarDisponibilidade(
                barbeiroId,
                dataHora
            );

            if (!disponivel) {
                return res.status(409).json({
                    error: 'Horário indisponível',
                    message: 'O barbeiro já possui um agendamento neste horário.'
                });
            }

            // 6. Cria ou busca cliente
            let cliente = await ClienteModel.findByEmail(email);

            if (cliente) {
                // Cliente já existe, verifica se já deu consentimento
                if (!cliente.aceitou_lgpd) {
                    return res.status(403).json({
                        error: 'Consentimento LGPD não registrado',
                        message: 'Este cliente não possui consentimento LGPD registrado.',
                        clienteId: cliente.id
                    });
                }
            } else {
                // Cria novo cliente com hash da senha
                const salt = await bcrypt.genSalt(10);
                const senhaHash = await bcrypt.hash(senha, salt);

                const clienteId = await ClienteModel.create(
                    nome,
                    email,
                    telefone,
                    senhaHash,
                    true // aceitou_lgpd
                );

                cliente = await ClienteModel.findById(clienteId);
            }

            // 7. Cria o agendamento
            const agendamentoId = await AgendamentoModel.create(
                cliente.id,
                barbeiroId,
                servicoId,
                dataHora
            );

            // 8. Busca o agendamento completo para retorno
            const agendamentoCompleto = await AgendamentoModel.findById(agendamentoId);

            // 9. Resposta de sucesso
            return res.status(201).json({
                success: true,
                message: 'Agendamento realizado com sucesso!',
                data: {
                    agendamento: agendamentoCompleto,
                    cliente: {
                        id: cliente.id,
                        nome: cliente.nome,
                        email: cliente.email,
                        consentimento_lgpd: cliente.aceitou_lgpd,
                        data_consentimento: cliente.data_consentimento
                    },
                    lgpd: {
                        consentimento_dado: true,
                        data_consentimento: cliente.data_consentimento,
                        direitos: [
                            'Acesso aos dados (Art. 18, I)',
                            'Correção de dados (Art. 18, II)',
                            'Exclusão de dados (Art. 18, III)',
                            'Revogação do consentimento (Art. 8º, §5º)'
                        ]
                    }
                }
            });

        } catch (error) {
            // Tratamento de erro UNIQUE (conflito de horário)
            if (error.code === 'ER_DUP_ENTRY') {
                return res.status(409).json({
                    error: 'Conflito de horário',
                    message: 'Este barbeiro já possui um agendamento neste horário.',
                    detalhe: error.sqlMessage
                });
            }

            console.error('Erro ao criar agendamento:', error);
            return res.status(500).json({
                error: 'Erro interno do servidor',
                message: 'Falha ao processar o agendamento.'
            });
        }
    }

    /**
     * GET /orcamentos - Lista todos os agendamentos (Admin)
     */
    async listarOrcamentos(req, res) {
        try {
            const { status, barbeiroId, clienteId, dataInicio, dataFim, limit = 50, offset = 0 } = req.query;

            const filtros = {
                status,
                barbeiroId: barbeiroId ? parseInt(barbeiroId) : null,
                clienteId: clienteId ? parseInt(clienteId) : null,
                dataInicio,
                dataFim,
                limit: parseInt(limit),
                offset: parseInt(offset)
            };

            // Remove filtros vazios
            Object.keys(filtros).forEach(key => {
                if (filtros[key] === null || filtros[key] === undefined || filtros[key] === '') {
                    delete filtros[key];
                }
            });

            const agendamentos = await AgendamentoModel.findAll(filtros);

            // Adiciona informações de consentimento LGPD para cada cliente
            const agendamentosComLgpd = await Promise.all(
                agendamentos.map(async (ag) => {
                    const cliente = await ClienteModel.findById(ag.cliente_id);
                    return {
                        ...ag,
                        cliente_lgpd: {
                            consentimento: cliente ? cliente.aceitou_lgpd : false,
                            data_consentimento: cliente ? cliente.data_consentimento : null
                        }
                    };
                })
            );

            return res.json({
                success: true,
                total: agendamentosComLgpd.length,
                agendamentos: agendamentosComLgpd,
                filtros_aplicados: filtros
            });

        } catch (error) {
            console.error('Erro ao listar agendamentos:', error);
            return res.status(500).json({
                error: 'Erro interno do servidor',
                message: 'Falha ao listar os agendamentos.'
            });
        }
    }

    /**
     * DELETE /orcamento/:id - Direito de Exclusão (Art. 18 LGPD)
     */
    async excluirOrcamento(req, res) {
        try {
            const { id } = req.params;
            const { motivo } = req.body;

            // 1. Busca o agendamento
            const agendamento = await AgendamentoModel.findById(id);

            if (!agendamento) {
                return res.status(404).json({
                    error: 'Agendamento não encontrado'
                });
            }

            // 2. Busca o cliente
            const cliente = await ClienteModel.findById(agendamento.cliente_id);

            // 3. LOG de exclusão para auditoria (LGPD)
            console.log(`[LGPD - EXCLUSÃO] Agendamento ID ${id} - Motivo: ${motivo || 'Não informado'}`);
            console.log(`[LGPD - EXCLUSÃO] Cliente: ${cliente ? cliente.email : 'Desconhecido'}`);
            console.log(`[LGPD - EXCLUSÃO] Data/Hora: ${new Date().toISOString()}`);
            console.log(`[LGPD - EXCLUSÃO] Art. 18, III - Direito de Exclusão`);

            // 4. Remove o agendamento
            const deletado = await AgendamentoModel.delete(id);

            if (!deletado) {
                return res.status(500).json({
                    error: 'Falha ao excluir agendamento'
                });
            }

            // 5. Resposta com confirmação LGPD
            return res.json({
                success: true,
                message: 'Agendamento excluído com sucesso (Direito de Exclusão - Art. 18 LGPD)',
                data: {
                    agendamento_id: id,
                    cliente_id: agendamento.cliente_id,
                    data_exclusao: new Date().toISOString(),
                    lgpd: {
                        direito_aplicado: 'Art. 18, III - Exclusão de dados pessoais',
                        base_legal: 'Art. 18, § 2º - O titular pode revogar o consentimento a qualquer tempo',
                        recomendacao: 'Mantenha registro desta exclusão por 5 anos (Art. 16, VII - LGPD)'
                    }
                }
            });

        } catch (error) {
            console.error('Erro ao excluir agendamento:', error);
            return res.status(500).json({
                error: 'Erro interno do servidor',
                message: 'Falha ao excluir o agendamento.'
            });
        }
    }
}

module.exports = new OrcamentoController();