# 밸런스히어로 Development Intern Project 2

### 참여자 : Aleph, Dori, Kate, Rev
---

#### 1. CSV Parsing 이란?  
입력받는 엑셀 파일에 대해 칼럼의 종류를 분석하고 칼럼의 정보와 데이터를 데이터베이스에 저장해주는 프로그램이다.  

#### 2. Combine Excel 이란?  
데이터베이스에 저장되어 있는 칼럼의 정보와 데이터를 매칭해서 서로 다른 종류의 데이터는,  
다른 시트에 작성되게 하면서 하나의 엑셀 파일로 결합시켜주는 프로그램이다.  

#### 3. 필요한 파일 및 설정들  
- 필요한 파일  
csv_parsing.py  
combine_excel.py  
user_config.ini  

- 필요한 설정  
서버의 데이터베이스를 규격에 맞게 설정한다.  

#### 4. 사용 방법  
  
1. csv_parsing.py  
파싱하고자 하는 엑셀 파일을 argument로 넣어서 python3 으로 실행하면 된다.  

2. combine_excel.py
python3 으로 해당 프로그램을 실행하면 통합된 엑셀 파일이 생성된다.  

#### 5. user_info 규칙  
##### 1. [DATABASE]  
엑셀 데이터를 저장할 데이터베이스 정보를 입력한다. 순서대로 서버주소, 유저 아이디, 비밀번호, 스키마 이름이다.  

##### 2. [DELIMITER]  
엑셀파일 확장자에 따른 구분자를 정의하는 곳이다. CSV파일은 default 값이 없어 입력을 해야한다.  
