import io
import os
import time
import pymupdf 
import zipfile
from PIL import Image
import streamlit as st
import pandas as pd
from collections import Counter
from PyPDF2 import PdfReader
from streamlit_extras.scroll_to_element import *

class messages():
    def __init__(self, *args):
        self.none = args[0]
    
    def messageDown(_self, *args):
        dataFiles = args[0]
        colMens = args[1]
        colDown = args[2]
        ext = args[3].lower()
        partial = args[4]
        keyDown = args[5]
        resol = args[6]
        placeMens = colMens.empty()
        placeDown = colDown.empty()
        fileResult = f'imagens_convertidas_{resol}_dpi_{ext}.zip'
        exprSucess = (f'Sucesso {partial} na conversão para o formato :blue[**{ext}**]. ' 
                      f'Faça download e acesse o arquivo :blue[**{fileResult}**].')
        colMens.success(exprSucess, icon='☑️',  width='stretch')
        optDown = colDown.download_button(
            label='Download',
            data=dataFiles,
            file_name=fileResult,
            mime='application/zip', 
            icon=':material/download:', 
            width='stretch', 
            key=keyDown, 
            help='Grava o arquivo zipado na pasta Download.')
    
    @st.dialog(title='Problema na conversão❗', width='medium', icon='🚧')
    def mensFormat(self, *args):
        oks = args[0]
        qOks = len(oks)
        noks = args[1]
        qNoks = len(noks)
        ext = args[2]
        key = args[3]
        nTotal = qOks + qNoks 
        textOk = f'📋 Resultado da tentativa de converter :blue[**{nTotal}**] arquivo(s) para o formato :blue[**{ext}**].<br><br>' 
        if qOks > 0:
            textOk +=  f':blue[**{qOks}**] arquivo(s) bem-sucedido(s):<br>'
            textOk += ' '.join([f'<br>ⵌ{str(w+1)} 📂{oks[w]}' for w in range(qOks)])
        else:
            textOk += '🚫 Não houve conversão bem-sucedida!<br>'
        textOk += f'<br>🔖 :blue[**{qNoks}**] arquivo(s) com problema:'
        if qNoks > 0:
            textOk += ' '.join([f'<br>ⵌ{str(w+1)} 📂{noks[w]}' for w in range(qNoks)])
        st.markdown(textOk, unsafe_allow_html=True)
        scroll_to_element(key)
        
    @st.dialog(title='Falha no aplicativo❗', width='medium', icon='🆘')
    def mensError(self, fail):
        st.markdown(f'Ocorreu o seguinte erro: {fail}. Contate o administador da ferramenta.')
 
class operatFiles():
    def __init__(self, *args):
        self.none = args[0]
    
    @st.cache_data
    def operatBasic(_self, *args):
        upLoads = args[0]
        sepHead = args[1]
        dictUpLoads = {}
        for upLoad in upLoads:
            keyLoad = f'{upLoad.name}{sepHead}{upLoad.type}{sepHead}{upLoad.size}'
            dictUpLoads.setdefault(keyLoad, [])
            dictUpLoads[keyLoad].append(upLoad)
        return dictUpLoads
        
    @st.cache_data
    def operatOthertoOther(_self, *args):
        fileUpLoads = args[0]
        sepHead = args[1]
        ext = args[2].lower()
        resol = args[3]
        zipBuffer = io.BytesIO()
        keysnOk = ['ok', 'nok']
        statusFileZip = {keysnOk[0]: [], keysnOk[1]:[]}
        for file, upLoads in fileUpLoads.items():
            for upLoad in upLoads:
                with zipfile.ZipFile(zipBuffer, 'a', zipfile.ZIP_DEFLATED) as zipFile:
                    upNameExt = upLoad.name
                    upName, upExt = os.path.splitext(upNameExt)
                    upName = f'{upName}_{resol}_dpi' 
                    upExt = upExt.lower().replace('.', '').strip()
                    try:
                        imgNew, imgBytes = _self.operatNoPdfToOther(upLoad, ext, resol, upName)
                        zipFile.writestr(imgNew, imgBytes.getvalue())
                        statusFileZip[keysnOk[0]].append(upNameExt)
                    except Exception as error:
                        statusFileZip[keysnOk[1]].append(upNameExt)
        return(zipBuffer.getvalue(), statusFileZip)
        
    @st.cache_data
    def operatNoPdfToOther(_self, *args):
        upLoad = args[0]
        ext = args[1]
        resol = args[2]
        upName = args[3]
        img = Image.open(upLoad)
        imgBytes = io.BytesIO()
        if ext == 'tif':
            extConv = 'tiff'
        elif ext == 'jpg':
            extConv = 'jpeg'
        else:
            extConv = ext
        img.save(imgBytes, format=extConv, dpi=(resol, resol))
        imgNew = f'{upName}.{ext}'
        return(imgNew, imgBytes)
                                   
class acessories():
    def __init__(self, *args):
        self.none = args[0]
    
    @st.cache_data
    def returnUpload(_self):
        confUp = """
                <style>
                    .stFileUploader [data-testid="stFileUploaderDropzone"] {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    }
                </style>
                """
        return confUp
    
    @st.cache_data
    def returnStr(_self, role):
        nRole = len(role)
        if nRole >= 2:
            roleStr = ', '.join(role[:-1])
            roleStr += f' e {role[-1]}'
        else:
            roleStr = role[0]
        return(roleStr, nRole)
        
    @st.cache_data
    def returnInfo(_self, *args):
        listOpt = args[0]
        iconPos = args[1]
        iconNeg = args[2]
        exprOpt = args[3]
        exprSel = args[4]
        mode = args[5]
        exts = args[6]
        nOpt = len(listOpt)
        if mode == 0: 
            if exts[3] in listOpt: 
                nOpt += 1
            if exts[-1] in listOpt:
                nOpt += 1
        match nOpt:
            case 0:
                txtInfo = f'{iconNeg} {exprOpt} {exprSel} ({nOpt})'
            case 1:
                txtInfo = f'{iconPos} {exprOpt} {exprSel} ({nOpt})'
            case _:
                txtInfo = f'{iconPos} {exprOpt}s {exprSel}s ({nOpt})'
        return txtInfo
    
    @st.cache_data    
    def makeTables(_self, *args):
        mode = args[0]
        if mode == 0:
            upLoads = args[1]
            sepHead = args[2]
            objFiles = operatFiles(None)
            keys = ['nome', 'tipo', 'tamanho', 'quantidade', 'status']
            heads = {key:[] for key in keys}
            nameTypeSize = []
            keysUp = list(upLoads.keys())        
            for keyUp in keysUp:
                keyUpSplit = keyUp.split(sepHead)
                for s, spl in enumerate(keyUpSplit):
                    heads[keys[s]].append(spl) 
                nRep = len(upLoads[keyUp])
                heads[keys[s+1]].append(nRep)
                if nRep > 1:
                    heads[keys[s+2]].append('com repetição')
                else:
                    heads[keys[s+2]].append('sem repetição')
        else:
            exts = args[1]
            heads = {'formato': exts, 
                     'informações': 
                         ['https://en.wikipedia.org/wiki/BMP_file_format', 
                          'https://pt.wikipedia.org/wiki/GIF', 
                          'https://en.wikipedia.org/wiki/ICO_(file_format)', 
                          'https://en.wikipedia.org/wiki/JPEG', 
                          'https://pdfcandy.com/pt/blog/o-que-e-um-arquivo-jpg.html', 
                          'https://pt.wikipedia.org/wiki/PDF', 
                          'https://pt.wikipedia.org/wiki/PNG', 
                          'https://en.wikipedia.org/?title=.ppm&redirect=no', 
                          'https://www.quora.com/What-is-a-tif-file-for', 
                          'https://pt.wikipedia.org/wiki/Tagged_Image_File_Format']}
        matrix = pd.DataFrame(heads, index=None) 
        return matrix
        
class main():
    def __init__(self):
        self.objMessages = messages(None)
        try:
            self.setKeys()
            self.setPage()
            self.homeScreen()
        except Exception as fail:
            self.objMessages.mensError(fail)            
        
    def setKeys(self):
        self.keys = ['fileDown', 'statusButt', 'valSlider', 'valInput', 'numFiles', 
                     'numExt', 'buttDown', 'popInfo']
        for k, key in enumerate(self.keys): 
            if key not in st.session_state:
                if k <= 1 or key == self.keys[-1]:
                    st.session_state[key] = True
                elif key == self.keys[-2]:
                    st.session_state[key] = False
                else:
                    st.session_state[key] = 0
        if 'buttDown' not in st.session_state:
            st.session_state['buttDown'] = False
        self.objAcess = acessories(None)
        self.exts = ['BMP', 'GIF', 'ICO', 'JPEG', 'JPG', 'PDF', 'PNG', 
                     'PPM', 'TIF', 'TIFF']
        self.extsUni = ['BMP', 'GIF', 'ICO', 'JPG', 'PNG', 'PPM', 'TIF']
        self.extsStr, self.nExts = self.objAcess.returnStr(self.extsUni)
        self.valMin, self.valMax, self.step = (70,1500, 1)
        self.icons = ['🏷️', '📚', '🛠️', '🎛️'] 
        self.labels = [f'{self.icons[0]} Formatos de imagem para pesquisa e seleção', 
                       f'{self.icons[1]} Lista de arquivos de imagem selecionados', 
                       f'{self.icons[2]} Resolução', 
                       f'{self.icons[3]} Opções']
    
    def homeScreen(self):
        self.sepHead = '#####......#####'
        self.wdt, self.hgt = (1366, 768)
        self.oprExpr = 'opção'
        with st.container(border=4, vertical_alignment='top'):
            self.setKeys()
            colDown, colButton = st.columns([18, 25], width='stretch')
            self.objFiles = operatFiles(None)
            self.keysWidget = ['multExt', 'multFiles', 'contZip']
            with colDown:
                helpDown = f'Escolha/selecione um ou mais destes {self.nExts} formatos de imagem: :blue[***{self.extsStr}***].\n'
                helpDown += f'O formato :blue[***{self.extsUni[3]}***] implica também :blue[***{self.exts[3]}***].'
                helpDown += f'O formato :blue[***{self.extsUni[-1]}***] implica também :blue[***{self.exts[-1]}***].'
                with st.container(border=None, vertical_alignment='center'):
                    st.markdown(self.labels[0], width='stretch', text_alignment='center', 
                                help=helpDown)
                    self.options = st.multiselect(label=f'{self.labels[0]}', 
                                                  options=self.extsUni, key=self.keysWidget[0],  
                                                  width='stretch', label_visibility='collapsed', 
                                                  placeholder='Tipo(s) de imagem escolhida(s)', 
                                                  on_change=self.changeVal, args=(2,)) 
                    if self.options == []:
                        st.session_state[self.keys[0]] = True
                        helpStr = 'Não há formatos de imagem selecionados para pesquisa.'
                    else:
                        st.session_state[self.keys[0]] = False 
                        self.optStr, self.nOpt = self.objAcess.returnStr(self.options)
                        helpStr = (f'Selecione ou arraste arquivos com qualquer um deste(s) '
                                   f':blue[***{self.nOpt} formato(s)***]:\n{self.optStr}.')
                    st.markdown(self.labels[1], width='stretch', text_alignment='center', 
                                help=helpStr)
                    self.upDowns = st.file_uploader(label=self.labels[1], 
                                                    accept_multiple_files=True, 
                                                    type=self.options, key=self.keysWidget[1],
                                                    max_upload_size=1024*20, 
                                                    width='stretch', label_visibility='collapsed',  
                                                    disabled=st.session_state.fileDown, 
                                                    on_change=self.changeVal, args=(3,))                    
                    if self.upDowns == []:
                        st.session_state[self.keys[1]] = True
                        st.session_state[self.keys[2]] = self.valMin
                        st.session_state[self.keys[3]] = self.valMin
                        st.session_state['clicked'] = None
                        st.session_state[self.keys[-1]] = True
                        self.allUpLoads = {}
                    else:
                        st.session_state[self.keys[1]] = False 
                        st.session_state[self.keys[-1]] = False
                        self.allUpLoads = self.objFiles.operatBasic(self.upDowns, self.sepHead)
                    confUp = self.objAcess.returnUpload()
                    st.markdown(confUp, unsafe_allow_html=True)
            with colButton:
                st.markdown(self.labels[2], width='stretch', text_alignment='center', 
                            help='Deslize o cursor para a direita ➡️ (aumento) e para a esquerda ⬅️ (diminuição).\n'
                                 'Para entrada numérica, digite a resolução (apertando "enter" depois) ou aumente (➕)/ diminua (➖) \n'
                                 'o valor desejado. O controle deslizante e o controle numérico se afetam reciprocamente.')
                colSlider, colResol = st.columns(spec=[13, 3.7], width='stretch', vertical_alignment='center')
                self.slider = colSlider.slider(label=self.labels[2], min_value=self.valMin, max_value=self.valMax,
                                               step=self.step, key=self.keys[2], label_visibility='collapsed', 
                                               disabled=st.session_state.statusButt, on_change=self.changeVal, 
                                               args=(0,), width='stretch')
                self.resol = colResol.number_input(label=self.labels[2], min_value=self.valMin, max_value=self.valMax,
                                                   step=self.step, key=self.keys[3], label_visibility='collapsed',
                                                   disabled=st.session_state.statusButt, on_change=self.changeVal, 
                                                   args=(1,), format='%d', placeholder='0', width='stretch')
                self.defineParameters()
                self.optStr, self.nOpt = self.objAcess.returnStr(self.exts)
                helpStr = (f'A conversão será feita acionando o botão correspondente a um dos {self.nOpt} formato(s):\n '
                           f':blue[***{self.optStr}***].')
                st.markdown(self.labels[3], width='stretch', text_alignment='center', 
                            help=helpStr)
                self.colOne, self.colTwo, self.colThree, self.colFour, self.colFive = st.columns(spec=5, width='stretch', vertical_alignment='top')
                self.defineButtons(0)
                self.colSix, self.colSeven, self.colEight, self.nine, self.ten = st.columns(spec=5, width='stretch', vertical_alignment='top')
                self.defineButtons(1)
            with st.container(border=False):
                self.colConfig, self.colInfo = st.columns([42, 6], width='stretch', 
                                                           vertical_alignment='bottom')
            self.configInfo()
        self.infoGeneral()
        if not st.session_state[self.keys[-2]]:
            with st.container(border=False, key=self.keysWidget[-1]):
                self.colMens, self.colZip = st.columns([21, 3], width='stretch', vertical_alignment='center')
            self.callButton()
        else:
            scroll_to_element(self.keysWidget[0])
                    
    def infoGeneral(self):
        with st.expander(label='Informações gerais', icon='📌',  width='stretch', 
                         expanded=False):
            matrix = self.objAcess.makeTables(1, self.exts)
            df = pd.DataFrame(matrix)
            st.dataframe(df,
                column_config={
                    "informações": st.column_config.LinkColumn(
                        "Link de Acesso",
                        help="Clique para abrir o site",
                        max_chars=100,
                    )
                },
                width='stretch' , hide_index=True)
               
    def defineButtons(self, mode):
        if mode == 0:
            self.listCol = self.colOne, self.colTwo, self.colThree, self.colFour, self.colFive
            nCols = len(self.listCol)
            self.ButOne, self.buttTwo, self.buttThree, self.buttFour, self.ButFive = [None for n in range(nCols)]
            self.listButt = [self.ButOne, self.buttTwo, self.buttThree, self.buttFour, self.ButFive]
            cont = list(range(nCols))
        else:
            self.listCol = self.colSix, self.colSeven, self.colEight, self.nine, self.ten
            nCols = len(self.listCol)
            self.buttSix, self.buttSeven, self.buttEight, self.buttNine, self.buttTen = [None for n in range(nCols)]
            self.listButt = [self.buttSix, self.buttSeven, self.buttEight, self.buttNine, self.buttTen]
            cont = list(range(nCols, 2*nCols))
        self.butts = []
        for b, butt in enumerate(self.listButt):
            col = self.listCol[b]
            c = cont[b]
            butt = col.button(label=self.buttons[c][0], key=self.buttons[c][1], 
                              icon=self.buttons[c][2], help=self.buttons[c][3],
                              use_container_width=self.buttons[c][4], on_click=self.clickButton, 
                              args=(c,), 
                              disabled=st.session_state.statusButt)
            self.butts.append(butt)
    
    def clickButton(self, buttId):
        if 'clicked' not in st.session_state:
            st.session_state['clicked'] = None
        st.session_state['clicked'] = f' {self.oprExpr} {self.exts[buttId]}' 
                
    def configInfo(self):
        self.positive = '✔️'
        self.negative = '❌'
        txtFormat = self.objAcess.returnInfo(self.options, self.positive, self.negative, 'formato', 'escolhido', 0, self.extsUni)
        txtFile = f'{self.objAcess.returnInfo(self.upDowns, self.positive, self.negative, 'arquivo', 'selecionado', 1, self.extsUni)}'
        txtResol = f'{self.positive} resolução ({str(st.session_state[self.keys[2]])}dpi)'
        if st.session_state['clicked'] is None:
            txtOpt = f'{self.negative} nenhuma opção clicada'
        else:
            txtOpt = f'{self.positive} {st.session_state['clicked']} clicada'
        with self.colConfig:
            colFormatSel, colFileSel, colResolSel, colOptSel = st.columns(spec=4, vertical_alignment='center', 
                                                                          width='stretch')
            colFormatSel.markdown(txtFormat)
            colFileSel.markdown(txtFile)
            colResolSel.markdown(txtResol)
            colOptSel.markdown(txtOpt)
        self.buttInfo = self.colInfo.popover(label='Info', key='popInfo', help='Clique para exibir ou ocultar detalhes dos arquivos.', 
                                             use_container_width=True, icon=self.symbols[-1], 
                                             disabled=st.session_state[self.keys[-1]])            
        with self.buttInfo:
            matrix = self.objAcess.makeTables(0, self.allUpLoads, self.sepHead)
            st.dataframe(matrix, width=int(self.wdt*0.95), height="auto", hide_index=True)
    
    def callButton(self):
        buttClick = st.session_state['clicked']
        if buttClick is not None:
            buttClick = buttClick.replace(self.oprExpr, '').strip()
            textSp = 'Convertendo arquivo(s) para o formato {buttClick} com resolução de {self.resol}dpi...'
            dataFiles, fileFails = self.objFiles.operatOthertoOther(self.allUpLoads, self.sepHead, buttClick, self.resol)  
            keyF = list(fileFails.keys()) 
            oks = fileFails[keyF[0]]
            noks = fileFails[keyF[1]]
            partial = ''
            if len(noks) > 0:
                partial = 'parcial'
                self.objMessages.mensFormat(oks, noks, buttClick, self.keysWidget[0])
            if len(oks) > 0:
                self.objMessages.messageDown(dataFiles, self.colMens, self.colZip, 
                                             buttClick, partial, self.keys[-2], self.resol)
                scroll_to_element(self.keysWidget[-1])
            
    def changeVal(self, widget):
        st.session_state['clicked'] = None
        if widget == 0:
            st.session_state[self.keys[3]] = st.session_state[self.keys[2]]
        else:
            st.session_state[self.keys[2]] = st.session_state[self.keys[3]]
    
    def defineParameters(self):
        self.buttons = {}
        self.symbols = [':material/image:', ':material/image_inset:', 
                        ':material/variables:', ':material/imagesmode:', 
                        ':material/aspect_ratio:', ':material/capture:', 
                        ':material/photo_frame:', ':material/gradient:', 
                        ':material/hallway:', ':material/mms:']
        for s, symbols in enumerate(self.symbols): 
            self.buttons[s] = [self.exts[s], f'conv{self.exts[s]}', self.symbols[s], 
                               f'Converte para o formato :blue[***{self.exts[s].lower()}***].', 
                               True] 
        self.symbols.append(':material/folder_info:')
    
    def setPage(self):
        st.set_page_config(
        page_title='Conversor de imagens',
        page_icon=':material/image:',
        layout='wide', 
        initial_sidebar_state=None, 
        menu_items=None)   
        with open('configImg.css') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
