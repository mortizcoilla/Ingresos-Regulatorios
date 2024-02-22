def vatt(df, n, k):
    # Valores constantes (
    ipc_0 = 97.89
    cpi_0 = 246.663
    d0 = 629.55
    ta0 = 0.06
    t_0 = 0.255

    # Extracción de valores del DataFrame
    avi_n0 = df.loc[n, 'AVI_0']
    coma_n0 = df.loc[n, 'COMA_0']
    aeir_n0 = df.loc[n, 'AEIR_0']
    alpha_j = df.loc[n, 'alpha_j']
    beta_j = df.loc[n, 'beta_j']
    gamma_j = df.loc[n, 'gamma_j']
    delta_j = df.loc[n, 'delta_j']
    ipc_k = df.loc[k, 'IPC']
    cpi_k = df.loc[k, 'CPI']
    d_k = df.loc[k, 'D']
    tak = df.loc[k, 'Tak']
    t_k = df.loc[k, 't']

    parte1 = avi_n0 * ((alpha_j * ipc_k / ipc_0 * d0 / d_k) + (beta_j * cpi_k / cpi_0 * (1 + tak) / (1 + ta0)))

    parte2 = coma_n0 * ipc_k / ipc_0 * d0 / d_k

    parte3 = aeir_n0 * ((gamma_j * ipc_k / ipc_0 * d0 / d_k) +
                        (delta_j * cpi_k / cpi_0 * (1 + tak) / (1 + ta0))) * t_k / t_0 * (1 - t_0 / (1 - t_k))

    vatt = parte1 + parte2 + parte3

    return vatt

