"""Tickets rotulados à mão: departamento correto e se são urgentes."""

DEPARTAMENTOS = {
    "cobranca": "Pagamento, fatura, cobrança, reembolso",
    "tecnico": "Falha, erro, lentidão, indisponibilidade",
    "conta": "Login, senha, cadastro, e-mail da conta",
}

TICKETS = [
    {"texto": "O checkout está falhando para todos os clientes há uma hora.", "departamento": "tecnico", "urgente": True},
    {"texto": "Fui cobrado duas vezes na fatura de setembro, preciso do estorno hoje.", "departamento": "cobranca", "urgente": True},
    {"texto": "Esqueci minha senha e o e-mail de recuperação não chega.", "departamento": "conta", "urgente": False},
    {"texto": "A página de relatórios demora uns 10 segundos para abrir, quando der.", "departamento": "tecnico", "urgente": False},
    {"texto": "Quero trocar o cartão de crédito da assinatura antes do próximo mês.", "departamento": "cobranca", "urgente": False},
    {"texto": "Não consigo entrar na conta e tenho uma apresentação em 20 minutos.", "departamento": "conta", "urgente": True},
    {"texto": "A API retorna erro 500 em todas as chamadas de produção desde as 14h.", "departamento": "tecnico", "urgente": True},
    {"texto": "Gostaria de receber a nota fiscal do mês passado em PDF.", "departamento": "cobranca", "urgente": False},
    {"texto": "Preciso mudar o e-mail cadastrado, o antigo foi desativado.", "departamento": "conta", "urgente": False},
    {"texto": "O botão de exportar não faz nada quando clico, só em um navegador.", "departamento": "tecnico", "urgente": False},
    {"texto": "Cancelei dentro da garantia e o valor ainda não voltou, já faz 15 dias.", "departamento": "cobranca", "urgente": False},
    {"texto": "Minha conta foi bloqueada depois de três tentativas e preciso acessar agora.", "departamento": "conta", "urgente": True},
    {"texto": "O painel mostra dados de ontem, o sync parece parado.", "departamento": "tecnico", "urgente": False},
    {"texto": "Vocês cobraram um plano anual que eu não contratei, isso é inaceitável.", "departamento": "cobranca", "urgente": True},
    {"texto": "Como altero o nome que aparece no meu perfil?", "departamento": "conta", "urgente": False},
    {"texto": "O app fecha sozinho sempre que abro a tela de pagamentos.", "departamento": "tecnico", "urgente": False},
    {"texto": "Boleto gerado com valor diferente do combinado, podem corrigir?", "departamento": "cobranca", "urgente": False},
    {"texto": "Recebi um e-mail de login suspeito na minha conta, acho que alguém entrou.", "departamento": "conta", "urgente": True},
    {"texto": "Todo o sistema está fora do ar e nossos clientes não conseguem comprar.", "departamento": "tecnico", "urgente": True},
    {"texto": "Podem me enviar o histórico de pagamentos dos últimos 6 meses?", "departamento": "cobranca", "urgente": False},
    {"texto": "Quero excluir minha conta e meus dados.", "departamento": "conta", "urgente": False},
    {"texto": "A busca está lenta de manhã, nada grave, só queria avisar.", "departamento": "tecnico", "urgente": False},
    {"texto": "O desconto prometido não apareceu na cobrança e vence hoje.", "departamento": "cobranca", "urgente": True},
    {"texto": "Não recebo o código de verificação por SMS para entrar.", "departamento": "conta", "urgente": False},
]
