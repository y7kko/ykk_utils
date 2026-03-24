import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import locale
class PlottingLayouts:
    @staticmethod
    def structuredgrid(gridsize = [2,2], row_title = None, col_title = None, 
                       figsize = None, col_fontsize = 12, row_fontsize = 12,
                       col_txt_size = 0.1, row_txt_size = 0.1, sharex = True,
                       sharey = True, ax_kw:dict=None):
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
        ignore_row_title = False
        if row_title is None:
            ignore_row_title = True
        if col_title is None:
            col_title = ['']*n_colunas
        if figsize is None:
            figsize = [3.5*n_linhas,2.5*n_colunas]
                    


        mosaic_formatter = []
        line_ratios = []
        # Gerando o layout
        column_header = [f'C{header+1}' for header in range(n_colunas)]
        mosaic_formatter.append(column_header)
        line_ratios.append(col_txt_size) #column vsize
        for linha in range(n_linhas):
            line_title = [f'L{linha+1}']*n_colunas
            line_ax = [f'ax{linha+1}{col+1}' for col in range(n_colunas) ]
            if not ignore_row_title:
                mosaic_formatter.append(line_title)
                line_ratios.append(row_txt_size) #row vsize
            mosaic_formatter.append(line_ax)
            line_ratios.append(1) #figure vsize

        if ax_kw is not None:
            per_subplot_kw = {}
            for linha in range(n_linhas):
                for col in range(n_colunas):
                    ax_key = f'ax{linha+1}{col+1}'
                    per_subplot_kw[ax_key] = ax_kw

        else:
            per_subplot_kw = None

        #instanciando o layout
        fig, ax_dict = plt.subplot_mosaic(mosaic_formatter,
                                    figsize=figsize,
                                    height_ratios=line_ratios,
                                    sharex=sharex,
                                    sharey=sharey,
                                    per_subplot_kw=per_subplot_kw,
                                    )

        for idx, ax_key in enumerate([f'C{col+1}' for col in range(n_colunas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, col_title[idx], ha='center', va='center', 
                    fontsize=col_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)
        if not ignore_row_title:
            for idx,ax_key in enumerate([f'L{lin +1}' for lin in range(n_linhas)]):
                ax_dict[ax_key].set_axis_off()
                ax_dict[ax_key].text(0.5, 0.5, row_title[idx], ha='center', va='top', 
                        fontsize=row_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        return fig, ax_dict
    
    @staticmethod
    def structuredgrid2(gridsize=[2,2], row_title=None, col_title=None, 
                       figsize=None, col_fontsize=12, row_fontsize=12,
                       col_txt_size=0.1, row_txt_size=0.1, sharex=True,
                       sharey=True, ax_kw:dict=None):
        
        n_linhas = gridsize[0]
        n_colunas = gridsize[1]

        if row_title is None:
            row_title = ['']*n_linhas
        if col_title is None:
            col_title = ['']*n_colunas
        if figsize is None:
            figsize = [3.5*n_linhas, 2.5*n_colunas]

        mosaic_formatter = []
        line_ratios = []
        
        # Gerando o layout
        column_header = [f'C{header+1}' for header in range(n_colunas)]
        mosaic_formatter.append(column_header)
        line_ratios.append(col_txt_size)
        
        for linha in range(n_linhas):
            line_title = [f'L{linha+1}']*n_colunas
            line_ax = [f'ax{linha+1}{col+1}' for col in range(n_colunas)]
            mosaic_formatter.append(line_title)
            mosaic_formatter.append(line_ax)
            line_ratios.append(row_txt_size)
            line_ratios.append(1)

        # Instanciando o layout sem projeção inicial
        fig, ax_dict = plt.subplot_mosaic(mosaic_formatter,
                                    figsize=figsize,
                                    height_ratios=line_ratios,
                                    sharex=sharex,
                                    sharey=sharey)

        # Aplicar projeção apenas aos eixos de plotagem (não aos títulos)
        if ax_kw and 'projection' in ax_kw:
            projection = ax_kw['projection']
            for key in ax_dict.keys():
                if key.startswith('ax'):  # Apenas para eixos de plotagem
                    # Remove o eixo original e cria um novo com projeção
                    fig.delaxes(ax_dict[key])
                    # Determina a posição do eixo original
                    pos = ax_dict[key].get_position()
                    # Cria novo eixo com projeção
                    ax_dict[key] = fig.add_subplot(
                        int(key[2]), int(key[3]), 1,  # grid position
                        projection=projection
                    )
                    ax_dict[key].set_position(pos)

        # Configurar títulos
        for idx, ax_key in enumerate([f'C{col+1}' for col in range(n_colunas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, col_title[idx], ha='center', va='center', 
                    fontsize=col_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        for idx, ax_key in enumerate([f'L{lin+1}' for lin in range(n_linhas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, row_title[idx], ha='center', va='top', 
                    fontsize=row_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        return fig, ax_dict




    @staticmethod
    def structuredgrid3(gridsize=[2,2], row_title=None, col_title=None, 
                    figsize=None, col_fontsize=12, row_fontsize=12,
                    col_txt_size=0.1, row_txt_size=0.1, sharex=True,
                    sharey=True, ax_kw:dict=None, colorbar_width=0.05):
        
        n_linhas = gridsize[0]
        n_colunas = gridsize[1]

        if row_title is None:
            row_title = ['']*n_linhas
        if col_title is None:
            col_title = ['']*n_colunas
        if figsize is None:
            # Aumentar largura para acomodar colorbars
            figsize = [3.5 * (n_colunas + colorbar_width), 2.5 * n_linhas]

        mosaic_formatter = []
        line_ratios = []
        width_ratios = [1] * n_colunas + [colorbar_width]  # Colunas normais + colorbar
        
        # Primeira linha: Headers das colunas + none
        header_row = [f'C{col+1}' for col in range(n_colunas)] + ['none_header']
        mosaic_formatter.append(header_row)
        line_ratios.append(col_txt_size)
        
        for linha in range(n_linhas):
            # Linha do título: Títulos repetidos + none
            title_row = [f'L{linha+1}'] * n_colunas + [f'none_title{linha+1}']
            mosaic_formatter.append(title_row)
            line_ratios.append(row_txt_size)
            
            # Linha dos eixos: Axes + colorbar
            axis_row = [f'ax{linha+1}{col+1}' for col in range(n_colunas)] + [f'cbar{linha+1}']
            mosaic_formatter.append(axis_row)
            line_ratios.append(1)

        # Instanciando o layout sem projeção inicial
        fig, ax_dict = plt.subplot_mosaic(mosaic_formatter,
                                    figsize=figsize,
                                    height_ratios=line_ratios,
                                    width_ratios=width_ratios,
                                    sharex=sharex,
                                    sharey=sharey,)

        # Aplicar projeção apenas aos eixos de plotagem (não aos títulos)
        if ax_kw and 'projection' in ax_kw:
            projection = ax_kw['projection']
            for key in list(ax_dict.keys()):
                if key.startswith('ax'):  # Apenas para eixos de plotagem
                    # Remove o eixo original e cria um novo com projeção
                    original_pos = ax_dict[key].get_position()
                    fig.delaxes(ax_dict[key])
                    
                    # Cria novo eixo com projeção na mesma posição
                    ax_dict[key] = fig.add_axes(original_pos, projection=projection)

        # Configurar headers das colunas
        for idx, ax_key in enumerate([f'C{col+1}' for col in range(n_colunas)]):
            ax_dict[ax_key].set_axis_off()
            ax_dict[ax_key].text(0.5, 0.5, col_title[idx], ha='center', va='center', 
                    fontsize=col_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        # Configurar títulos das linhas (T1, T2, etc.)
        for linha in range(n_linhas):
            for col in range(n_colunas):
                ax_key = f'L{linha+1}'
                ax_dict[ax_key].set_axis_off()
                # Só adiciona texto no primeiro T de cada linha
                if col == 0:
                    ax_dict[ax_key].text(0.5, 0.5, row_title[linha], ha='center', va='top', 
                            fontsize=row_fontsize, fontweight='normal', transform=ax_dict[ax_key].transAxes)

        # Configurar eixos "none" (vazios)
        none_keys = [key for key in ax_dict.keys() if key.startswith('none')]
        for key in none_keys:
            ax_dict[key].set_axis_off()

        # Configurar colorbars (inicialmente vazias)
        for linha in range(n_linhas):
            cbar_key = f'cbar{linha+1}'
            ax_dict[cbar_key].set_axis_off()

        return fig, ax_dict

    @staticmethod
    def add_colorbar_to_row(fig, ax_dict, row, mappable, label=None, orientation='vertical'):
        """
        Adiciona colorbar a uma linha específica
        
        Args:
            fig: Figura
            ax_dict: Dicionário de eixos
            row (int): Número da linha (1-indexed)
            mappable: Objeto mappable do plot (e.g., retorno de contourf, imshow)
            label (str, optional): Label da colorbar
            orientation (str): 'vertical' ou 'horizontal'
        """
        cbar_key = f'cbar{row}'
        
        if cbar_key not in ax_dict:
            raise KeyError(f"Colorbar para linha {row} não encontrada. Verifique se structuredgrid2 foi chamado com colorbars habilitadas.")
        
        # Reutilizar o eixo da colorbar
        pos = ax_dict[cbar_key].get_position()
        fig.delaxes(ax_dict[cbar_key])
        
        # Criar novo eixo para colorbar na mesma posição
        ax_dict[cbar_key] = fig.add_axes(pos)
        
        # Adicionar colorbar
        cbar = fig.colorbar(mappable, cax=ax_dict[cbar_key], orientation=orientation)
        
        if label:
            cbar.set_label(label)
            
        return cbar

    @staticmethod
    def serif_font(virgulas=True):
        """Muda o sistema global de fontes do matplotlib para
        LaTeX + Times New Roman
        """
        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
        })

        if virgulas:
            locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
            plt.rcParams['axes.formatter.use_locale'] = True
    @staticmethod
    def set_ptbr():
        locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
        plt.rcParams['axes.formatter.use_locale'] = True
