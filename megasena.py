# -*- coding: utf-8 -*-

from datetime import date
import os
import zipfile,requests
from tqdm import tqdm
import codecs
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
import itertools



class m_stats(object):
    def __init__(self):
        self.path='http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_megase.zip'
        self.folder=os.path.join(os.getcwd(),'results')
        self.resultfile="D_MEGA.HTM"
        self.result1 = None
        self.numbers={}

    def get_result(self):

        return ( itertools.tee(self.result1))


    def set_result(self,valor):

        self.result1=valor


    def get_filename(self):
        filename = 'mega_'+str(date.today()).replace('-', '') + '.zip'
        fpath = os.path.join(self.folder,filename)
        return(fpath,filename)

    def get_allresults(self, fpath):
        if os.path.exists(fpath):
            os.remove(fpath)
        u=requests.get(self.path,stream=True)
        with open(fpath, "wb+") as handle:
            for data in tqdm(u.iter_content()):
                handle.write(data)

    def decompress(self,fpath):

        zip_ref = zipfile.ZipFile(fpath, 'r')
        zip_ref.extractall(self.folder)

        zip_ref.close()

        with codecs.open(os.path.join(self.folder,self.resultfile),'r',encoding='utf-8', errors='ignore') as html:
            try:
                soup = BeautifulSoup(html,"html.parser")
            except:
                pass
            table = soup.find("table")

            headings = [th.get_text() for th in table.find("tr").find_all("th")]

            datasets = []
            for row in table.find_all("tr")[1:]:
                dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
                datasets.append(dataset)
            self.set_result(datasets)

    def get_sresult(self,concurso):
        control=0
        for dataset in self.get_result():
            for field in dataset:
                if field[0] == 'Concurso' and str(field[1]) == concurso:
                        control=1
                if (field[0] == 'Concurso') and  (str(field[1]).isdigit()) and not (str(field[1]) == concurso):
                        control=0
                        break
                if control == 1:
                    print("{0:<16}: {1}".format(field[0], field[1]))


    def set_numbers(self):
        for dataset in self.get_result():
            for field in dataset:
                if str(field[0])[2:8] == 'Dezena':
                    if not int(field[1]) in self.numbers.keys():
                        self.numbers.update({ int(field[1]) : 1 })
                    else:
                        self.numbers[int(field[1])]+=1


    def get_top_numbers_by_date(self,date_top,n):

        control=0
        datetime_top = datetime.strptime(date_top, '%d/%m/%Y')
        top_numbers_by_date={}
        for dataset in list(self.get_result())[0]:
            for field in dataset:

                if field[0] == 'Data Sorteio' and len(field[1]) > 6:
                    if datetime.strptime(field[1], '%d/%m/%Y') >= datetime_top:
                        control=1

                    if datetime.strptime(field[1], '%d/%m/%Y') < datetime_top:
                        control=0

                if str(field[0])[2:8] == 'Dezena' and control == 1:
                    if not int(field[1]) in top_numbers_by_date.keys():
                        top_numbers_by_date.update({ int(field[1]) : 1 })

                    else:
                        top_numbers_by_date[int(field[1])] += 1

        c=Counter(top_numbers_by_date)
        return c.most_common(n)

    def get_least_numbers_by_date(self,date_top,n):
        control=0
        datetime_top = datetime.strptime(date_top, '%d/%m/%Y')
        least_numbers_by_date={}
        for dataset in self.get_result()[0]:
            for field in dataset:
                if field[0] == 'Data Sorteio' and datetime.strptime(field[1], '%d/%m/%Y') >= datetime_top:
                        control=1

                if field[0] == 'Data Sorteio' and datetime.strptime(field[1], '%d/%m/%Y') < datetime_top:
                        control=0

                if str(field[0])[2:8] == 'Dezena' and control == 1:
                    if not int(field[1]) in least_numbers_by_date.keys():
                        least_numbers_by_date.update({ int(field[1]) : 1 })

                    else:
                        least_numbers_by_date[int(field[1])] += 1

        c=Counter(least_numbers_by_date)
        return c.most_common()[:-n-1:-1]

    def get_value_by_number(self,number):
        return self.numbers[number]


    def get_top_numbers(self,n):
        c=Counter(self.numbers)
        return c.most_common(n)


    def get_least_numbers(self,n):
        c=Counter(self.numbers)
        return c.most_common()[:-n-1:-1]



if __name__ == '__main__':

    ms=m_stats()
    # Definir um nome do arquivo para ser salvo - Função nao obrigatoria
    fpath,filename=ms.get_filename()
    # Obter os resultados
    print('\n * Obtendo os resultados da Mega-Sena. Isto costuma ser rápido...\n')
    ms.get_allresults(fpath)
    # Descompactar o arquivo e salvar em memoria
    ms.decompress(fpath)



    # Imprimir concurso especifico
    ms.get_sresult('1')

    ms.set_numbers()
    # Mostra valor especifico que um número foi sorteado
    numero=9
    print("\nNúmero %s foi sorteado: %s\n" %(numero,ms.get_value_by_number(numero)))

    #TOP MAIS
    top_numeros=5
    print("\nTOP Números da MegaSena de todos os sorteios:\n")
    for k, v in ms.get_top_numbers(top_numeros):
        print('%s: %i' % (k, v))

    #TOP MENOS
    least_numeros=5
    print("\nNúmeros que menos sairam de todos os sorteios:\n")
    for k, v in ms.get_least_numbers(least_numeros):
        print('%s: %i' % (k, v))


    #TOP MAIS POR DATA MINIMA
    top_numeros=5
    top_date='05/09/2012'
    print("\nTOP Números da MegaSena de todos os sorteios com data acima de %s:\n" % top_date)
    for k, v in ms.get_top_numbers_by_date(top_date,top_numeros):
        print('%s: %i' % (k, v))

    #TOP MENOS MAIS POR DATA MINIMA
    top_numeros=5
    top_date='05/09/2012'
    print("\nTOP Menos Números da MegaSena de todos os sorteios com data acima de %s:\n" % top_date)
    for k, v in ms.get_least_numbers_by_date(top_date,top_numeros):
        print('%s: %i' % (k, v))


