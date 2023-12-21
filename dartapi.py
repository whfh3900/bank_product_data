import requests
import os
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta
from tqdm import tqdm
import time
import json
import xmltodict
import codecs

def make_local_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"'{folder_path}' 폴더가 생성되었습니다.")
    else:
        print(f"'{folder_path}' 폴더가 이미 존재합니다.")





class DartAPI():
    def __init__(self, crtfc_key):
        self.crtfc_key = crtfc_key



    def unique_num(self, save_path="../data/unique_corp"):
        # Dart API 엔드포인트 URL
        url = 'https://opendart.fss.or.kr/api/corpCode.xml' #고유번호 개발가이드
        # GET 요청 보내기
        params = {'crtfc_key': self.crtfc_key}
        response = requests.get(url, params=params)

        # 응답 상태코드 확인
        if response.status_code == 200:
            # Zip 파일 저장 경로
            make_local_folder(save_path)
            zip_file_path = os.path.join(save_path, "unique_corp.zip")

            # 응답 데이터 저장 (binary 모드로)
            with open(zip_file_path, 'wb') as file:
                file.write(response.content)

            # Zip 파일 압축 해제
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(save_path)
                
            # XML 파일 경로
            xml_file = os.path.join(save_path, "CORPCODE.xml")
            # XML 파일 열기
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # 데이터 추출 및 리스트 생성
            data_list = []
            for child in root.findall('list'):
                corp_code = child.find('corp_code').text
                corp_name = child.find('corp_name').text
                stock_code = child.find('stock_code').text.strip()
                modify_date = child.find('modify_date').text
                
                data_list.append([corp_code, corp_name, stock_code, modify_date])

            # Pandas DataFrame 생성
            columns = ['corp_code', 'corp_name', 'stock_code', 'modify_date']
            df = pd.DataFrame(data_list, columns=columns)
            return df
        else:
            raise KeyError('올바르지 않은 api key 입니다.')


        
    def usang(self, day, ago_day, have_corp, ):

        use_corp = pd.DataFrame()
        url = 'https://opendart.fss.or.kr/api/piicDecsn.json' #유상증자 결정 개발가이드

        for i,n in tqdm(have_corp.items()):
            # GET 요청 보내기
            params = {'crtfc_key': self.crtfc_key,
                    'corp_code':n,
                    'bgn_de':ago_day,
                    'end_de':day,}
            try:
                response = requests.get(url, params=params, verify=False)
            except Exception as e:
                time.sleep(30)
                response = requests.get(url, params=params, verify=False)

            # 응답 상태코드 확인
            if response.status_code == 200:
                if response.json()["status"] == "000":
                    etc = pd.DataFrame(response.json()['list'])
                    use_corp = pd.concat([use_corp, etc], axis=0)
        return use_corp



    def umusang(self, day, have_corp):
        string_to_day = datetime.strptime(day, "%Y%m%d")
        three_months_ago = (string_to_day - timedelta(days=3*30)).strftime('%Y%m%d')

        use_corp = pd.DataFrame()
        url = 'https://opendart.fss.or.kr/api/pifricDecsn.json' #유무상증자 결정 개발가이드

        for i,n in tqdm(have_corp.items()):
            # GET 요청 보내기
            params = {'crtfc_key': self.crtfc_key,
                    'corp_code':n,
                    'bgn_de':'20150101',
                    'end_de':day,}
            try:
                response = requests.get(url, params=params, verify=False)
            except Exception as e:
                time.sleep(30)
                response = requests.get(url, params=params, verify=False)

            # 응답 상태코드 확인
            if response.status_code == 200:
                if response.json()["status"] == "000":
                    etc = pd.DataFrame(response.json()['list'])
                    use_corp = pd.concat([use_corp, etc], axis=0)
        return use_corp
    
    
    def download_word(self, rcept_no_list, save_path="../data/doc"):
        make_local_folder(save_path)
        for rcept_no in tqdm(rcept_no_list):
            # Dart API 엔드포인트 URL
            url = 'https://opendart.fss.or.kr/api/document.xml' #공시서류원본파일 개발가이드
            # GET 요청 보내기
            params = {'crtfc_key': self.crtfc_key,
                    'rcept_no': rcept_no}
            response = requests.get(url, params=params)

            # 응답 상태코드 확인
            if response.status_code == 200:

                zip_file_path = os.path.join(save_path, "%s.zip"%rcept_no)

                # 응답 데이터 저장 (binary 모드로)
                with open(zip_file_path, 'wb') as file:
                    file.write(response.content)

                # Zip 파일 압축 해제
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(save_path)

                # XML 파일 열기
                xml_file_path = os.path.join(save_path, "%s.xml"%rcept_no)

                try:
                    # XML 파일 읽기
                    with open(xml_file_path, 'r', encoding="utf-8-sig") as xml_file:
                        xml_data = xml_file.read()
                except UnicodeDecodeError as e:
                    # XML 파일 읽기
                    with open(xml_file_path, 'r', encoding="cp949") as xml_file:
                        xml_data = xml_file.read()
                    
                    with codecs.open(xml_file_path, 'w', encoding='utf-8-sig') as new_xml_file:
                        new_xml_file.write(xml_data)
    
                # Zip 파일 삭제
                os.remove(zip_file_path)
     

            else:
                raise KeyError('올바르지 않은 api key 입니다.')