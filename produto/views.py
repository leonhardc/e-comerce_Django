from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from .models import Produto, Variacao
from utils.returns_id import retorna_id


class ListaProdutos(ListView):

    # Lista os produtos da base de dados na página inicial.
    model = Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'

class DetalheProduto(DetailView):

    # Mostra os detalhes de um produto escolhido pelo cliente na página anterior.
    model = Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'

class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):

        # HTTP_REFERER é um método que o django usa para guardar a referência da página
        # anteriormente acessada pelo usuário.
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )

        # Em produto/templates/produto/detalhes.html a tag <select> implementa o atributo
        # name="vid", que nesse caso se refere ao Id da variação do produto.
        # O método abaixo - self.request.GET.get('vid') - implementa ima forma de capturarmos
        # o id da variação do produto para podermos, posteriormente, adicioná-lo ao carrinho de
        # compras.
        variacao_id = self.request.GET.get('vid')

        # se não existir uma variação do nosso produto retornamos para página acessada
        # anteriormente
        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        # Captura o objeto que representa a variação na nossa base de dados
        variacao = get_object_or_404(Variacao, id=variacao_id)
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        variacao_id = variacao.id # sobrescrevendo valor de variacao_id
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        # Se o estoque for insuficiente, retornar uma mensagem de erro.
        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente.'
            )
            return redirect(http_referer)

        # Se não existir um carrinho, criamos um carrinho.
        # Uma _.session funciona como os cookies no navegador, são informações do usuário
        # sobre dados da seção, mas que serão armazenadas pelo servidor, pelo tempo que for
        # necessário.
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        # Acrescenta variação de produto ao carrinho
        carrinho = self.request.session['carrinho']
        if variacao_id in carrinho:
            # TODO: Variação exite no carrinho
            pass
        else:
            carrinho[variacao_id] = {
                'produto_id':produto_id,
                'produto_nome':produto_nome,
                'variacao_nome':variacao_nome,
                'variacao_id':variacao_id,
                'preco_unitario':preco_unitario,
                'preco_unitario_promocional':preco_unitario_promocional,
                'preco_quantitativo':preco_unitario,
                'preco_quantitativo_promocional':preco_unitario_promocional,
                'quantidade': 1,
                'slug':slug,
                'imagem':imagem
            }

        # Salvando a sessão
        self.request.session.save()

        # httpresponse para teste
        return HttpResponse(f'Adicionar ao Carrinho: {variacao.produto} {variacao.nome}')

class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Remover do Carrinho')

class Carrinho(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Carrinho')

class Finalizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalizar')
