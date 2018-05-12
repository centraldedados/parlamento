#!/usr/bin/env python3
''' Script para limpar ou obter a 'estrutura' de um ficheiro JSON '''
import os
import json
import click
from datetime import datetime as dt

CONFIGOBJ_ACTIV_DEPUTADOS = {
    'prefixos_a_truncar': [
        'pt_gov_ar_wsar_objectos_',
        'pt_ar_wsgode_objectos_'
    ],
    'prefixos_de_atributo_a_ignorar': [
        '@', '?', 'ArrayOf'
    ],
    'sufixos_de_atributo_a_ignorar': [
        'List'
    ],
    'atributos_a_ignorar': [
        # "ini", "req", "sgt", "scgt", "intev", "actP", "gpa", "rel", "eventos",
        # "deslocacoes", "cms", "dadosLegisDeputado", "audiencias", "audicoes", "depGP", "depCargo",
        # "parlamentoJovens", "videos", "depSituacao", "dlP", "dlE", "relatoresIniciativas",
        # "relatoresPeticoes", "relatoresContasPublicas", "relatoresIniEuropeias"
    ]
}


def listar(p_path, out_list, limitcount=-1, maxlevel=-1):
    '''Extractor de texto transforma o ficheiro de entrada numa lista de linhas
    de texto de saída que deverá estar vazia.

    Parâmetros:
    * caminho_entrada - caminho completo para o ficheiro de entrada
    * lista_saida - lista que irá receber as linhas de texto produzidas
    * limitcount - limite de número máximo de linhas a ler do ficheiro de entrada
    * maxlevel - limite máximo à profundidade da árvore a ler
    '''
    stack = []
    level = 0
    tree = json.load(open(p_path))
    del out_list[:]

    stack.append([level, '--raiz--', tree])

    while len(stack) > 0:
        currlevel, currid, currnode = stack.pop()

        if currnode is None:
            continue

        newlevel = currlevel + 1
        if maxlevel >= 0 and newlevel > maxlevel:
            dostack = False
        else:
            dostack = True

        if isinstance(currnode, list):
            out_list.append("{}{}:".format(' ' * (newlevel - 2), currid))
            if dostack:
                # currnode.reverse()
                for ei, el in reversed(list(enumerate(currnode))):
                    stack.append([newlevel, str(ei), el])
        elif isinstance(currnode, dict):
            if currid != '--raiz--' \
                    and not currid.startswith('@') \
                    and not currid.startswith('?'):
                out_list.append("{}{}:".format(' ' * (newlevel - 2), currid))
            if dostack:
                kl = list(currnode.keys())
                kl.reverse()
                for key in kl:
                    stack.append([newlevel, key, currnode[key]])
        elif isinstance(currnode, str):
            # aqui é que filtramos o valor do string
            pass
        else:
            if not str(currid).strip().startswith('@'):
                out_list.append("{}{}: {}".format(' ' * (newlevel - 2), currid, str(currnode)[:40]))

        if limitcount >= 0 and len(out_list) >= limitcount:
            break


def listaparcial(p_in_path, p_out_path, limitcount=10000, maxlevel=-1):
    '''Função de amostragem que transforma 'limitcount' linhas do ficheiro JSON
    de entrada numa saida de texto indentado, sem filtrar, e sem preocupação em
    construir objectos JSON completos na saída.

    O objectivo desta função é o de conseguir ler com facilidade n linhas ou o
    JSON original apenas até uma certa profundidade.  Depois de efectuar uma
    amostragem por esta via, é mais fácil produzir a configuração final de
    extracção a usar com 'unique'.

    Parâmetros:
    * caminho_entrada - caminho completo para o ficheiro de entrada
    * caminho_saida - caminho completo para o ficheiro JSON de saída
    * limitcount - limite de número máximo de linhas a ler do ficheiro de
      entrada
    * maxlevel - limite máximo à profundidade da árvore a ler
    '''
    out = []
    listar(p_in_path, out, limitcount=limitcount, maxlevel=maxlevel)
    with open(p_out_path, 'w') as f:
        for item in out:
            f.write("%s\n" % item)


def lerstruct(p_path, out_dict, configobj, listaumelemento=True, maxlevel=-1):
    '''Extractor propriamente dito, transforma o ficheiro de entrada numa
    árvore dentro do dicionário que deverá estar vazio.

    Parâmetros:
    * caminho_entrada - caminho completo para o ficheiro de entrada
    * dicionário_saida - dicionário que irá receber a árvore produzida
    * configobj - dicionário contendo os parâmetros de configuração do
      processo de leitura
    * listaumelemento - booleano, se verdadeiro apenas o primeiro elemento de
      cada lista é transcrito
    * maxlevel - limite máximo à profunidade da árvore a ler

    '''

    stack = []
    level = 0
    tree = json.load(open(p_path))
    stack.append([level, '--raiz--', tree, out_dict])

    while len(stack) > 0:

        currlevel, currid, currnode, outobj_node = stack.pop()

        if currnode is None:
            continue

        newlevel = currlevel + 1

        if maxlevel >= 0 and newlevel > maxlevel:
            dostack = False
        else:
            dostack = True

        for prefx in configobj['prefixos_a_truncar']:
            currid = currid.replace(prefx, '')

        if isinstance(currnode, list):
            outobj_node[currid] = []
            outobj_node = outobj_node[currid]
            if dostack:
                for ei, el in reversed(list(enumerate(currnode))):
                    stack.append([newlevel, str(ei), el, outobj_node])
                    if listaumelemento:
                        break

        elif isinstance(currnode, dict):
            oktogo = False
            if (currid != '--raiz--' and
               currid not in configobj['atributos_a_ignorar']):

                okprefix_suffix = True

                for attrprf in configobj['prefixos_de_atributo_a_ignorar']:
                    if currid.startswith(attrprf):
                        okprefix_suffix = False
                        break

                if okprefix_suffix:
                    for attrsfx in configobj['sufixos_de_atributo_a_ignorar']:
                        if currid.endswith(attrsfx):
                            okprefix_suffix = False
                            break

                if okprefix_suffix:
                    oktogo = True

            if oktogo:
                if isinstance(outobj_node, list):
                    outobj_node.append({})
                    outobj_node = outobj_node[-1]
                else:
                    outobj_node[currid] = {}
                    outobj_node = outobj_node[currid]

            if dostack:
                kl = list(currnode.keys())
                kl.reverse()
                for key in kl:
                    stack.append([newlevel, key, currnode[key], outobj_node])

        else:
            if not str(currid).strip().startswith('@'):
                if isinstance(outobj_node, list):
                    outobj_node.append(currnode)
                elif isinstance(outobj_node, dict):
                    outobj_node[currid] = currnode


def unique(p_in_path, p_out_path, p_configobj):
    '''Após filtrar o conteúdo, é gerado um novo ficheiro JSON de "estrutura",
    indentado, no qual cada lista é substituída por uma lista idêntica contendo
    apenas o último elemento.
    O nome de saída pode levar uma entrada de formato {} que receberá a data e
    hora no formato ISO.

    Parâmetros:
    * caminho_entrada - caminho completo para o ficheiro JSON de entrada
    * caminho_saida - caminho completo para o ficheiro JSON de saida
    * configobj - dicionário contendo os parâmetros de configuração do processo
      de leitura;
    '''
    out = {}
    lerstruct(p_in_path, out, p_configobj)
    with open(p_out_path.format(dt.now().isoformat()), 'w') as outfile:
        json.dump(out, outfile, indent=2, ensure_ascii=False)


def full(p_in_path, p_out_path, p_configobj):
    '''Após filtrar o conteúdo, é gerado um novo ficheiro JSON indentado,
    contendo a totalidade do ficheiro de entrada. O nome de saída pode levar
    uma entrada de formato {} que receberá a data e hora no formato ISO

    Parâmetros:
    * caminho_entrada - caminho completo para o ficheiro JSON de entrada;
    * caminho_saida - caminho completo para o ficheiro JSON de saida;
    * configobj - dicionário contendo os parâmetros de configuração do processo
    de leitura
    '''
    out = {}
    lerstruct(p_in_path, out, p_configobj, listaumelemento=False)
    with open(p_out_path.format(dt.now().isoformat()), 'w') as outfile:
        json.dump(out, outfile, indent=2, ensure_ascii=False)


@click.command()
@click.argument('filename')
@click.option('--in-place', '-i', is_flag=True, default=False, help="Gravar por cima do ficheiro original")
@click.option('--partial', '-p', is_flag=True, default=False, help="Correr parcialmente para verificar resultados")
@click.option('--outfile', '-o', help="Ficheiro para gravar o resultado")
def run(filename, outfile, in_place, partial):
    if not outfile and not in_place:
        base, ext = os.path.splitext(filename)
        outfile = base + '-filtrado' + ext
    elif in_place:
        outfile = filename

    if partial:
        # listaparcial(filename, outfile, limitcount=100, maxlevel=5)
        unique(filename, outfile, CONFIGOBJ_ACTIV_DEPUTADOS)
    else:
        full(filename, outfile, CONFIGOBJ_ACTIV_DEPUTADOS)


if __name__ == "__main__":
    run()
