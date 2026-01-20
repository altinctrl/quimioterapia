from src.schemas.protocolo import CategoriaBlocoEnum, UnidadeDoseEnum, ViaAdministracaoEnum, FaseEnum

PROTOCOLOS_DATA = [
    {
        "nome": "PEMETREXEDE + CISPLATINA",
        "indicacao": "Ca Pulmão",
        "tempo_total_minutos": 240,
        "duracao_ciclo_dias": 21,
        "total_ciclos": 6,
        "fase": FaseEnum.PALIATIVO,
        "dias_semana_permitidos": [1],
        "templates_ciclo": [
            {
                "id_template": "padrao",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.PRE_MED,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Dexametasona",
                                    "dose_referencia": 4,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 50ml",
                                                              "Soro Fisiológico 0,9% 100ml", "Sem Diluente (Bolus)"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            },
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Ondansetrona",
                                    "dose_referencia": 8,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 50ml",
                                                              "Soro Fisiológico 0,9% 100ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Pemetrexede",
                                    "dose_referencia": 500,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 10,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 3,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Cisplatina",
                                    "dose_referencia": 75,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 120,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 500ml"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "nome": "VELCADE (BORTEZOMIBE)",
        "indicacao": "Mieloma Múltiplo",
        "tempo_total_minutos": 30,
        "duracao_ciclo_dias": 7,
        "total_ciclos": 8,
        "fase": FaseEnum.PALIATIVO,
        "dias_semana_permitidos": [3],
        "templates_ciclo": [
            {
                "id_template": "padrao",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Bortezomibe",
                                    "dose_referencia": 1.3,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.SC,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 50ml", "Água para Injeção 10ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 50ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Dexametasona",
                                    "dose_referencia": 20,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 50ml",
                                                              "Soro Fisiológico 0,9% 100ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "nome": "RITUXIMABE MONOTERAPIA",
        "indicacao": "Linfoma não-Hodgkin",
        "tempo_total_minutos": 300,
        "duracao_ciclo_dias": 21,
        "total_ciclos": 6,
        "fase": FaseEnum.PALIATIVO,
        "dias_semana_permitidos": [5],
        "templates_ciclo": [
            {
                "id_template": "padrao",
                "blocos": [
                    {
                        "ordem": 1, "categoria": CategoriaBlocoEnum.PRE_MED,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Dipirona",
                                    "dose_referencia": 1,
                                    "unidade": UnidadeDoseEnum.G,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml", "Sem Diluente (Bolus)"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            },
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Hidrocortisona",
                                    "dose_referencia": 100,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Rituximabe",
                                    "dose_referencia": 375,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 240,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 500ml"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }]
    },
    {
        "nome": "FOLFOX 6",
        "indicacao": "Ca Colorretal",
        "tempo_total_minutos": 240,
        "duracao_ciclo_dias": 14,
        "total_ciclos": 12,
        "fase": FaseEnum.ADJUVANTE,
        "dias_semana_permitidos": [1, 2, 3],
        "templates_ciclo": [
            {
                "id_template": "padrao",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Oxaliplatina",
                                    "dose_referencia": 85,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 120,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Glicose 5% 250ml", "Glicose 5% 500ml"],
                                        "selecionada": "Glicose 5% 250ml"
                                    }
                                }
                            },
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Leucovorina",
                                    "dose_referencia": 400,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 120,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Glicose 5% 250ml", "Soro Fisiológico 0,9% 250ml"],
                                        "selecionada": "Glicose 5% 250ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Fluorouracil",
                                    "dose_referencia": 400,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 120,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Bolus", "Soro Fisiológico 0,9% 50ml"],
                                        "selecionada": "Bolus"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 3,
                        "categoria": CategoriaBlocoEnum.INFUSOR,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Fluorouracil",
                                    "dose_referencia": 2400,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 2760,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 500ml",
                                                              "Soro Fisiológico 0,9% 1000ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 500ml"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "nome": "AC-T (DOXORRUBICINA + CICLOFOSFAMIDA)",
        "indicacao": "Ca Mama",
        "tempo_total_minutos": 180,
        "duracao_ciclo_dias": 21,
        "total_ciclos": 4,
        "fase": FaseEnum.NEOADJUVANTE,
        "dias_semana_permitidos": [1, 2, 3, 4, 5],
        "templates_ciclo": [
            {
                "id_template": "padrao",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.PRE_MED,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Ondansetrona",
                                    "dose_referencia": 16,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 50ml",
                                                              "Soro Fisiológico 0,9% 100ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 100ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Doxorrubicina",
                                    "dose_referencia": 60,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 15,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml", "Sem Diluente (Bolus)"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 3,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Ciclofosfamida",
                                    "dose_referencia": 600,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "nome": "PROTOCOLO COMPLEXO (DEMO)",
        "indicacao": "Neoplasia Avançada de Teste",
        "fase": FaseEnum.PALIATIVO,
        "linha": 1,
        "total_ciclos": 12,
        "duracao_ciclo_dias": 21,
        "tempo_total_minutos": 420,
        "dias_semana_permitidos": [1, 2, 3, 4],
        "ativo": True,
        "observacoes": "Protocolo imaginário para teste.",
        "precaucoes": "Seguir este protocolo faz mal à saúde.",
        "templates_ciclo": [
            {
                "id_template": "Ataque - Ciclo 1",
                "aplicavel_aos_ciclos": "1",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.PRE_MED,
                        "itens": [
                            {
                                "tipo": "grupo_alternativas",
                                "label_grupo": "Escolha do Anti-HT3 (Protocolo de Pesquisa)",
                                "opcoes": [
                                    {
                                        "medicamento": "Ondansetrona",
                                        "dose_referencia": 8,
                                        "unidade": UnidadeDoseEnum.MG,
                                        "via": ViaAdministracaoEnum.IV,
                                        "tempo_minutos": 45,
                                        "dias_do_ciclo": [1],
                                        "configuracao_diluicao": {
                                            "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                                  "Soro Fisiológico 0,9% 250ml",
                                                                  "Soro Fisiológico 0,9% 500ml"],
                                            "selecionada": "Soro Fisiológico 0,9% 250ml"
                                        }
                                    },
                                    {
                                        "medicamento": "Palonosetrona",
                                        "dose_referencia": 0.25,
                                        "unidade": UnidadeDoseEnum.MG,
                                        "via": ViaAdministracaoEnum.IV,
                                        "tempo_minutos": 45,
                                        "dias_do_ciclo": [1],
                                        "configuracao_diluicao": {
                                            "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                                  "Soro Fisiológico 0,9% 250ml",
                                                                  "Soro Fisiológico 0,9% 500ml"],
                                            "selecionada": "Soro Fisiológico 0,9% 250ml"
                                        }
                                    }
                                ]
                            },
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Dexametasona",
                                    "dose_referencia": 20,
                                    "unidade": UnidadeDoseEnum.MG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 45,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Medicamento de Ataque X",
                                    "dose_referencia": 10,
                                    "unidade": UnidadeDoseEnum.MG_KG,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    },
                                    "notas_especificas": "Infusão lenta apenas no C1"
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "id_template": "Manutenção",
                "aplicavel_aos_ciclos": "2-12",
                "blocos": [
                    {
                        "ordem": 1,
                        "categoria": CategoriaBlocoEnum.PRE_MED,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Dipirona",
                                    "dose_referencia": 1,
                                    "unidade": UnidadeDoseEnum.G,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 2,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Droga A (Sinergia)",
                                    "dose_referencia": 150,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            },
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Droga B (Sinergia)",
                                    "dose_referencia": 50,
                                    "unidade": UnidadeDoseEnum.MG_M2,
                                    "via": ViaAdministracaoEnum.IV,
                                    "tempo_minutos": 60,
                                    "dias_do_ciclo": [1],
                                    "configuracao_diluicao": {
                                        "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                              "Soro Fisiológico 0,9% 250ml",
                                                              "Soro Fisiológico 0,9% 500ml"],
                                        "selecionada": "Soro Fisiológico 0,9% 250ml"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ordem": 3,
                        "categoria": CategoriaBlocoEnum.QT,
                        "itens": [
                            {
                            "tipo": "medicamento_unico",
                            "dados": {
                                "medicamento": "Platina de Teste",
                                "dose_referencia": 6,
                                "unidade": UnidadeDoseEnum.AUC,
                                "via": ViaAdministracaoEnum.IV,
                                "tempo_minutos": 60,
                                "dias_do_ciclo": [1],
                                "configuracao_diluicao": {
                                    "opcoes_permitidas": ["Soro Fisiológico 0,9% 100ml",
                                                          "Soro Fisiológico 0,9% 250ml",
                                                          "Soro Fisiológico 0,9% 500ml"],
                                    "selecionada": "Soro Fisiológico 0,9% 250ml"
                                }
                            }
                        }
                        ]
                    },
                    {
                        "ordem": 4,
                        "categoria": CategoriaBlocoEnum.POS_MED_HOSPITALAR,
                        "itens": [
                            {
                            "tipo": "medicamento_unico",
                            "dados": {
                                "medicamento": "Hidratação Pós-QT",
                                "dose_referencia": 500,
                                "unidade": UnidadeDoseEnum.UI,
                                "via": ViaAdministracaoEnum.IV,
                                "tempo_minutos": 30,
                                "dias_do_ciclo": [1],
                                "configuracao_diluicao": {
                                    "opcoes_permitidas": ["Soro Fisiológico 0,9% 500ml"],
                                    "selecionada": "Soro Fisiológico 0,9% 500ml"
                                }
                            }
                        }
                        ]
                    },
                    {
                        "ordem": 5,
                        "categoria": CategoriaBlocoEnum.INFUSOR,
                        "itens": [
                            {
                            "tipo": "medicamento_unico",
                            "dados": {
                                "medicamento": "Quimioterápico Expansor",
                                "dose_referencia": 1200,
                                "unidade": UnidadeDoseEnum.MG_M2,
                                "via": ViaAdministracaoEnum.IV,
                                "tempo_minutos": 1140,
                                "dias_do_ciclo": [1],
                                "notas_especificas": "Instalar na bomba elastomérica para 24h"
                            }
                        }
                        ]
                    },
                    {
                        "ordem": 6,
                        "categoria": CategoriaBlocoEnum.POS_MED_DOMICILIAR,
                        "itens": [
                            {
                                "tipo": "medicamento_unico",
                                "dados": {
                                    "medicamento": "Filgrastima",
                                    "dose_referencia": 5,
                                    "unidade": UnidadeDoseEnum.MCG_KG,
                                    "dose_maxima": 300,
                                    "via": ViaAdministracaoEnum.SC,
                                    "tempo_minutos": 30,
                                    "dias_do_ciclo": [3, 4, 5],
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
]
