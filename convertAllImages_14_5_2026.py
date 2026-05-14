import io
import os
import time
import zipfile
from PIL import Image
import streamlit as st
import pandas as pd
from collections import Counter
from PyPDF2 import PdfReader
from fpdf import FPDF
from streamlit_extras.scroll_to_element import *

class messages():
    def __init__(self, *args):
        self.none = args[0]
    
    def messageDown(_self, *args):
        dataFiles = args[0]
        colMens = args[1]
        colDown = args[2]
        ext = args[3].lower()
        placeMens = colMens.empty()
        placeDown = colDown.empty()
        colMens.success(f'Sucesso na conversão para {ext}', icon='☑️',  width='stretch')
        optDown = colDown.download_button(
            label='Download',
            data=dataFiles,
            file_name='imagens_convertidas.zip',
            mime='application/zip', 
            icon=':material/download:', 
            width='stretch', 
            key='buttDown', 
            help='Grava o arquivo zipado na pasta Download.')
 
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
        failZip = {}
        with zipfile.ZipFile(zipBuffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for file, upLoads in fileUpLoads.items():
                for upLoad in upLoads:
                    try:
                        upName, upExt = os.path.splitext(upLoad.name)
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
                        zip_file.writestr(imgNew, imgBytes.getvalue())
                    except Exception as error:
                        failZip.setdefault(file, [])
                        failZip[file].append(upLoad)
        return zipBuffer.getvalue()
                                
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
        nOpt = len(listOpt)
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
        upLoads = args[0]
        sepHead = args[1]
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
        matrix = pd.DataFrame(heads, index=None)  
        return matrix
        
class main():
    def __init__(self):
        self.setKeys()
        self.setPage()
        self.homeScreen()
        
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
        self.extsUni = ['BMP', 'GIF', 'ICO', 'JPG', 'PDF', 'PNG', 'PPM', 'TIF']
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
            self.messages = messages(None)
            self.keysWidget = ['multExt', 'multFiles', 'contZip']
            with colDown:
                with st.container(border=None, vertical_alignment='center'):
                    st.markdown(self.labels[0], width='stretch', text_alignment='center', 
                                help=f'Escolha/selecione um ou mais destes {self.nExts} formatos de imagem: :blue[***{self.extsStr}***].')
                    self.options = st.multiselect(label=f'{self.labels[0]}', 
                                                  options=self.extsUni, key=self.keysWidget[0],  
                                                  width='stretch', label_visibility='collapsed', 
                                                  placeholder='Tipo(s) de imagem escolhida(s)') 
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
                                                    disabled=st.session_state.fileDown)                    
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
        if not st.session_state[self.keys[-2]]:
            with st.container(border=False, key=self.keysWidget[-1]):
                self.colMens, self.colZip = st.columns([21, 3], width='stretch', vertical_alignment='center')
            self.callButton()
        else:
            #scroll_to_element(self.keysWidget[0])
            pass
                    
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
        txtFormat = self.objAcess.returnInfo(self.options, self.positive, self.negative, 'formato', 'escolhido')
        txtFile = f'{self.objAcess.returnInfo(self.upDowns, self.positive, self.negative, 'arquivo', 'selecionado')}'
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
        self.buttInfo = self.colInfo.popover(label='Info', key='popInfo', help='Clique para exibir ou ocultar detalhes da sessão de uso.', 
                                             use_container_width=True, icon=self.symbols[-1], 
                                             disabled=st.session_state[self.keys[-1]])            
        with self.buttInfo:
            matrix = self.objAcess.makeTables(self.allUpLoads, self.sepHead)
            st.dataframe(matrix, width=int(self.wdt*0.95), height="auto", hide_index=True)
    
    def callButton(self):
        buttClick = st.session_state['clicked']
        if buttClick is not None:
            buttClick = buttClick.replace(self.oprExpr, '').strip()
            dataFiles = self.objFiles.operatOthertoOther(self.allUpLoads, self.sepHead, buttClick, self.resol)  
            textSp = 'Convertendo arquivo(s) para o formato {buttClick} com resolução de {self.resol}dpi...'
            with st.spinner(text=textSp, show_time=True, width='stretch'): 
                self.messages.messageDown(dataFiles, self.colMens, self.colZip, buttClick)
            #scroll_to_element(self.keysWidget[-1])
            
    def changeVal(self, widget):
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
