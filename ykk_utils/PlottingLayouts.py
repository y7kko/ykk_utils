import numpy as np
import matplotlib.pyplot as plt

class PlottingLayouts:
    @staticmethod
    def structuredgrid(gridsize=[2,2], row_title=None, col_title=None, figsize=None):
        """Cria um gridlayout de títulos compartilhados, para casos onde todos os plots
        representam um "meshgrid" de algo:

        Examples:
            >>> axd['ax12'].plot() #'plota na linha 1 coluna 2'

        Args:
            gridsize (list, optional): Número de linhas e colunas. Defaults to [2,2].
            row_title (str, optional): Titulo de cada linha. Defaults to None.
            col_title (_type_, optional): Título de cada coluna. Defaults to None.
            figsize (_type_, optional): Tamanho da figura. Defaults to None.
        Returns:
            fig, axd: Instância da figura e dicionário de ax
        """
        n_linhas = gridsize[0]
        n_colunas = gridsize[1]

        if row_title is None:
            row_title = ['']*n_linhas
        if col_title is None:
            col_title = ['']*n_colunas
        if figsize is None:
            figsize = [3.5*n_linhas,2.5*n_colunas]


        mosaic_formatter = []
        line_ratios = []
        # Gerando o layout
        column_header = [f'C{header+1}' for header in range(n_colunas)]
        mosaic_formatter.append(column_header)
        line_ratios.append(0.5)
        for linha in range(n_linhas):
            line_title = [f'L{linha+1}']*n_colunas
            line_ax = [f'ax{linha+1}{col+1}' for col in range(n_colunas) ]
            mosaic_formatter.append(line_title)
            mosaic_formatter.append(line_ax)
            line_ratios.append(0.2)
            line_ratios.append(1)

        #instanciando o layout
        fig, ax_dict = plt.subplot_mosaic(mosaic_formatter,
                                    figsize=figsize,
                                    height_ratios=line_ratios,
                                    sharex=True,
                                    sharey=True
                                    )

        for idx, ax_key in enumerate([f'C{col+1}' for col in range(n_colunas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, col_title[idx], ha='center', va='center', 
                    fontsize=12, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        for idx,ax_key in enumerate([f'L{lin +1}' for lin in range(n_linhas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, row_title[idx], ha='center', va='top', 
                    fontsize=12, fontweight='normal', transform=ax_dict[ax_key].transAxes)
            
        return fig, ax_dict
