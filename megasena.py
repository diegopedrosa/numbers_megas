# -*- coding: utf-8 -*-

from datetime import date
import os
import zipfile,requests
from tqdm import tqdm
import codecs
from bs4 import BeautifulSoup
from collections import Counter



class m_stats():
    def __init__(self):
        self.path='http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_megase.zip'
        self.folder=os.path.join(os.getcwd(),'results')
        self.resultfile="D_MEGA.HTM"
        self.result=None
        self.numbers={}

    def get_filename(self):
        filename = 'mega_'+str(date.today()).replace('-', '') + '.zip'
        fpath = os.path.join(self.folder,filename)
        return(fpath,filename)

    def get_allresults(self, fpath, filename):
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

            # The first tr contains the field names.
            headings = [th.get_text() for th in table.find("tr").find_all("th")]

            datasets = []
            for row in table.find_all("tr")[1:]:
                dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
                datasets.append(dataset)
            self.result=datasets

    def get_sresult(self,concurso):
        control=0
        for dataset in self.result:
            for field in dataset:
                if field[0] == 'Concurso' and str(field[1]) == concurso:
                        control=1
                if (field[0] == 'Concurso') and  (str(field[1]).isdigit()) and not (str(field[1]) == concurso):
                        control=0
                        break
                if control == 1:
                    print("{0:<16}: {1}".format(field[0], field[1]))


    def set_numbers(self):
        for dataset in self.result:
            for field in dataset:
                if str(field[0])[2:8] == 'Dezena':
                    if not int(field[1]) in self.numbers.keys():
                        self.numbers.update({ int(field[1]) : 1 })
                    else:
                        self.numbers[int(field[1])]+=1



    def get_value_by_number(self,number):
        return self.numbers[number]


    def get_top_numbers(self,n):
        c=Counter(self.numbers)
        for k, v in c.most_common(n):
            print('%s: %i' % (k, v))

    def get_least_numbers(self,n):
        c=Counter(self.numbers)
        for k, v in c.most_common()[:-n-1:-1]:
            print('%s: %i' % (k, v))


if __name__ == '__main__':

    ms=m_stats()
    # Definir um nome do arquivo para ser salvo - Função nao obrigatoria
    fpath,filename=ms.get_filename()
    # Obter os resultados
    print('\n * Obtendo os resultados da Mega-Sena. Isto costuma ser rápido...\n')
    ms.get_allresults(fpath, filename)
    # Descompactar o arquivo e salvar em memoria
    ms.decompress(fpath)

    #ms.set_numbers()
    # Mostra valor especifico

    #print(ms.get_value_by_number(60))
   # ms.get_top_numbers(60)

   # ms.get_least_numbers(60)

    # Imprimir concurso especifico
    ms.get_sresult('1422')




