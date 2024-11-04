# IDENTIFICAÇÃO DO ESTUDANTE:
# Preencha seus dados e leia a declaração de honestidade abaixo. NÃO APAGUE
# nenhuma linha deste comentário de seu código!
#
#    Nome completo: Vitor Bertelli do Prado
#    Matrícula:     202299641
#    Turma:         CC6N
#    Email:         vitorbertelli19@gmail.com
#
# DECLARAÇÃO DE HONESTIDADE ACADÊMICA:
# Eu afirmo que o código abaixo foi de minha autoria. Também afirmo que não
# pratiquei nenhuma forma de "cola" ou "plágio" na elaboração do programa,
# e que não violei nenhuma das normas de integridade acadêmica da disciplina.
# Estou ciente de que todo código enviado será verificado automaticamente
# contra plágio e que caso eu tenha praticado qualquer atividade proibida
# conforme as normas da disciplina, estou sujeito à penalidades conforme
# definidas pelo professor da disciplina e/ou instituição.


# Imports permitidos (não utilize nenhum outro import!):
import sys
import math
import base64
import tkinter
from io import BytesIO
from PIL import Image as PILImage


# Classe Imagem:
class Imagem:
    def __init__(self, largura, altura, pixels):
        self.largura = largura
        self.altura = altura
        self.pixels = pixels

    def get_pixel(self, x, y):
        # Alternativa para a função lidar com pixels fora dos limites da imagem.
        # Além de servir como prevenção em caso de erro.
        # O retorno é o pixel mais próximo do pixel fora dos limites.
        if(x < 0): # Corrige a posição do pixel em relação a largura.
            x = 0
        elif(x >= self.largura):
            x = self.largura - 1

        if(y < 0): # Corrige a posição do pixel em relação a altura.
            y = 0
        elif(y >= self.altura):
            y = self.altura - 1

        endereco = x + (y * self.largura) # Sabendo que os pixels estão armazenados em uma lista em row-major order,
                                          # o endereço (índice) do pixel é calculado através da fórmula acima.
        return self.pixels[endereco]

    def set_pixel(self, x, y, c):
        endereco = x + (y * self.largura) # Variável explicada na função get_pixel.
        self.pixels[endereco] = c

    def aplicar_correlacao(self, kernel):
        n = len(kernel) # Variável que armazena o tamanho do kernel. Considerando que o kernel seja uma matriz quadrada n X n onde n é ímpar.
        deslocamento = n // 2 # Variável utilizada para calcular o deslocamento necessário ao aplicar a correlação sobre cada pixel da imagem.
                              # Por exemplo, se o kernel for 3x3, será necessário descolar 1 pixel para todos os lados para aplicar a operação de soma ponderada aos pixels vizinhos em relação ao pixel central.

        # Função interna que aplica a correlação sobre cada pixel da imagem.
        # Essa função foi criada para ser utilizada como argumento na função aplicar_por_pixel.
        def func(c, x, y):
            soma_ponderada = 0 # Variável inicializada para armazenar a soma ponderada a cada iteração da operação.
                               # Essa soma é resultante da combinação linear dos n^2 pixels mais próximos ao pixel (x, y).

            # Laço que percorre a matriz do kernel.
            for i in range(n):
                for j in range(n):
                    soma_ponderada += kernel[j][i] * self.get_pixel(x + i - deslocamento, y + j - deslocamento)
            return soma_ponderada # Após a operação, o valor resultante é retornado e será defino no pixel (x, y) na função aplicar_por_pixel.

        return self.aplicar_por_pixel(func) # Retorna a imagem resultante após a aplicação da correlação, não aplica diretamente a imagem original.
    
    # Função criada pelo aluno (Vitor) para normalizar os pixels da imagem.
    # Ou seja, garantir que os valores dos pixels sejam inteiros e recortam os pixels que estejam fora do intervalo [0, 255] para dentro.
    def normalizar_pixels(self):
        return self.aplicar_por_pixel(lambda c, x, y: round(c) if c >= 0 and c <= 255 else 0 if c < 0 else 255)  # É utilizado a função aplicar_por_pixel para percorrer todos os pixels da imagem.
                                                                                                                 # Uma função anônima é utilizada para padronizar os valores dos pixels.
        # Durante o desenvolvimento do laboratório, houve uma dúvida sobre como garantir que os valores dos pixels sejam do tipo inteiro.
        # Já que a função round() arredonda o número para o inteiro mais próximo e int() simplesmente descarta a parte decimal, retornando somente a parte inteira.
        # Por isso, foi utilizado a round() pois foi a única que passou em todos os testes. Contrário da função int(), que não passou em alguns dos testes.

    def aplicar_por_pixel(self, func):
        resultado = Imagem.nova(self.largura, self.altura)
        for x in range(resultado.largura):
            for y in range(resultado.altura):
                cor = self.get_pixel(x, y)
                nova_cor = func(cor, x, y) # Os argumentos x e y foram adicionados para que a função aplicar_por_pixel se torne mais genérica e ser reutilizada em aplicar_correlacao.
                resultado.set_pixel(x, y, nova_cor)
        return resultado

    def invertida(self):
        return self.aplicar_por_pixel(lambda c, x, y: 255 - c) # Foi realizado a correção para a função funcione corretamente.
                                                               # Além disso, foi adicionado os parâmetros x e y para que a função funcione com a modificação feita em aplicar_por_pixel.

    def borrada(self, n):
        valor = 1 / (n * n) # Variável que armazena o valor do kernel para o desfoque de caixa.
        kernel_desfoque = [[valor for _ in range(n)] for _ in range(n)] # Cria um kernel que armaena valores idênticos que somam 1.
        
        resultado = self.aplicar_correlacao(kernel_desfoque) # Aplica a correlação sobre a imagem original com o kernel de desfoque.
        resultado = resultado.normalizar_pixels()

        return resultado

    def focada(self, n):
        # Para implementar a função focada, foi decidido utilizar a subtração explícita.
        # Para isso foi necessário criar uma imagem intermediária, seguindo os passos da função borrada, ao ínves de chamar a função.
        # Pois, como foi dito no enunciado, a versão desfocada não pode ter nenhum arredondamento ou corte nos pixels.
        valor = 1 / (n * n) # Variaveis como os da função borrada.
        kernel_desfoque = [[valor for _ in range(n)] for _ in range(n)] 
        imagem_borrada = self.aplicar_correlacao(kernel_desfoque)

        # Loço padrão para percorrer todos os pixels imagem e aplicar a subtração explícita.
        resultado = Imagem.nova(self.largura, self.altura)
        for x in range(resultado.largura):
            for y in range(resultado.altura):
                cor = self.get_pixel(x, y)
                nova_cor = 2 * cor - imagem_borrada.get_pixel(x, y) # Execução da fórmula como apresentada do PDF.
                resultado.set_pixel(x, y, nova_cor)

        # O enunciado não deixa explícito se é necessário fazer o corte dos pixels para o intervalo [0, 255]. Somente o arredondamento.
        # Mas seguindo uma lógica básica, não faz sentido ter pixels com valores negativos ou maiores que 255. Logo foi aplicado a função para normalizar os valores.        
        resultado = resultado.normalizar_pixels()

        return resultado # Retorna a imagem resultante após a aplicação da função focada.

    def bordas(self):
        resultado = Imagem.nova(self.largura, self.altura) # Imagem vazia que armazenará o resultado final.
        # Kernels utilizados para a detecção das bordas.
        kernel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        kernel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

        # Imagens intermediárias contendo as aproximações das derivadas horizontais e verticais.
        imagem_x = self.aplicar_correlacao(kernel_x) # self.aplicar_correlacao() garante a aplicação dos kernels na imagem que chamou a função bordas().
        imagem_y = self.aplicar_correlacao(kernel_y)

        # Para finalizar a operação de detecção de bordas, realizamos o cálculo de combinação das aplicações acima.
        # Recebe, em cada pixel da imagem, a raiz quadrada da soma dos quadrados dos pixels correspondentes em imagem_x e imagem_y.
        resultado = resultado.aplicar_por_pixel(lambda c, x, y: math.sqrt(imagem_x.get_pixel(x, y) ** 2 + imagem_y.get_pixel(x, y) ** 2))
        resultado = resultado.normalizar_pixels() # Por fim, garante que a imagem final possua os pixels 'legais'.

        return resultado


    # Abaixo deste ponto estão utilitários para carregar, salvar e mostrar
    # as imagens, bem como para a realização de testes. Você deve ler as funções
    # abaixo para entendê-las e verificar como funcionam, mas você não deve
    # alterar nada abaixo deste comentário.
    #
    # ATENÇÃO: NÃO ALTERE NADA A PARTIR DESTE PONTO!!! Você pode, no final
    # deste arquivo, acrescentar códigos dentro da condicional
    #
    #                 if __name__ == '__main__'
    #
    # para executar testes e experiências enquanto você estiver executando o
    # arquivo diretamente, mas que não serão executados quando este arquivo
    # for importado pela suíte de teste e avaliação.
    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('altura', 'largura', 'pixels'))

    def __repr__(self):
        return "Imagem(%s, %s, %s)" % (self.largura, self.altura, self.pixels)

    @classmethod
    def carregar(cls, nome_arquivo):
        """
        Carrega uma imagem do arquivo fornecido e retorna uma instância dessa
        classe representando essa imagem. Também realiza a conversão para tons
        de cinza.

        Invocado como, por exemplo:
           i = Imagem.carregar('test_images/cat.png')
        """
        with open(nome_arquivo, 'rb') as guia_para_imagem:
            img = PILImage.open(guia_para_imagem)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2]) for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Modo de imagem não suportado: %r' % img.mode)
            l, a = img.size
            return cls(l, a, pixels)

    @classmethod
    def nova(cls, largura, altura):
        """
        Cria imagens em branco (tudo 0) com a altura e largura fornecidas.

        Invocado como, por exemplo:
            i = Imagem.nova(640, 480)
        """
        return cls(largura, altura, [0 for i in range(largura * altura)])

    def salvar(self, nome_arquivo, modo='PNG'):
        """
        Salva a imagem fornecida no disco ou em um objeto semelhante a um arquivo.
        Se o nome_arquivo for fornecido como uma string, o tipo de arquivo será
        inferido a partir do nome fornecido. Se nome_arquivo for fornecido como
        um objeto semelhante a um arquivo, o tipo de arquivo será determinado
        pelo parâmetro 'modo'.
        """
        saida = PILImage.new(mode='L', size=(self.largura, self.altura))
        saida.putdata(self.pixels)
        if isinstance(nome_arquivo, str):
            saida.save(nome_arquivo)
        else:
            saida.save(nome_arquivo, modo)
        saida.close()

    def gif_data(self):
        """
        Retorna uma string codificada em base 64, contendo a imagem
        fornecida, como uma imagem GIF.

        Função utilitária para tornar show_image um pouco mais limpo.
        """
        buffer = BytesIO()
        self.salvar(buffer, modo='GIF')
        return base64.b64encode(buffer.getvalue())

    def mostrar(self):
        """
        Mostra uma imagem em uma nova janela Tk.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # Se Tk não foi inicializado corretamente, não faz mais nada.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # O highlightthickness=0 é um hack para evitar que o redimensionamento da janela
        # dispare outro evento de redimensionamento (causando um loop infinito de
        # redimensionamento). Para maiores informações, ver:
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        tela = tkinter.Canvas(toplevel, height=self.altura,
                              width=self.largura, highlightthickness=0)
        tela.pack()
        tela.img = tkinter.PhotoImage(data=self.gif_data())
        tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        def ao_redimensionar(event):
            # Lida com o redimensionamento da imagem quando a tela é redimensionada.
            # O procedimento é:
            #  * converter para uma imagem PIL
            #  * redimensionar aquela imagem
            #  * obter os dados GIF codificados em base 64 (base64-encoded GIF data)
            #    a partir da imagem redimensionada
            #  * colocar isso em um label tkinter
            #  * mostrar a imagem na tela
            nova_imagem = PILImage.new(mode='L', size=(self.largura, self.altura))
            nova_imagem.putdata(self.pixels)
            nova_imagem = nova_imagem.resize((event.width, event.height), PILImage.NEAREST)
            buffer = BytesIO()
            nova_imagem.save(buffer, 'GIF')
            tela.img = tkinter.PhotoImage(data=base64.b64encode(buffer.getvalue()))
            tela.configure(height=event.height, width=event.width)
            tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        # Por fim, faz o bind da função para que ela seja chamada quando a tela
        # for redimensionada:
        tela.bind('<Configure>', ao_redimensionar)
        toplevel.bind('<Configure>', lambda e: tela.configure(height=e.height, width=e.width))

        # Quando a tela é fechada, o programa deve parar
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)


# Não altere o comentário abaixo:
# noinspection PyBroadException
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()


    def refaz_apos():
        tcl.after(500, refaz_apos)


    tcl.after(500, refaz_apos)
except:
    tk_root = None

WINDOWS_OPENED = False

if __name__ == '__main__':
    # O código neste bloco só será executado quando você executar
    # explicitamente seu script e não quando os testes estiverem
    # sendo executados. Este é um bom lugar para gerar imagens, etc.

    # QUESTÃO 2
    bluegill = Imagem.carregar("test_images/bluegill.png")
    bluegill_invertida = bluegill.invertida()
    bluegill_invertida.salvar("respostas/bluegill_invertida.png")

    # QUESTÃO 4
    kernel = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    pigbird = Imagem.carregar("test_images/pigbird.png")
    pigbird_modificada = pigbird.aplicar_correlacao(kernel)
    pigbird_modificada.salvar("respostas/pigbird_modificada.png")

    # QUESTÃO 5
    python = Imagem.carregar("test_images/python.png")
    python_focada = python.focada(11)
    python_focada.salvar("respostas/python_focada.png")

    # QUESTÃO 6
    construct = Imagem.carregar("test_images/construct.png")
    
    kernel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    kernel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    construct_x = construct.aplicar_correlacao(kernel_x)
    construct_y = construct.aplicar_correlacao(kernel_y)
    construct_x.mostrar()
    construct_y.mostrar()
    
    construct_bordas = construct.bordas()
    construct_bordas.salvar("respostas/construct_bordas.png")


    # O código a seguir fará com que as janelas de Imagem.mostrar
    # sejam exibidas corretamente, quer estejamos executando
    # interativamente ou não:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
