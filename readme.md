<div align="center">
  <img src="https://evento.kro.kr/assets/evento_logo.png" alt="Evento 로고" width="200">

  <h3>간편한 일정 관리 및 공유 캘린더 플랫폼</h3>
  <p>
    캘린더를 <strong>생성, 구독 및 관리</strong>하며
    개인 일정과 아티스트의 일정을 손쉽게 확인하고 상호작용할 수 있습니다.
  </p>
   <a href="https://evento.kro.kr/" target="_blank">
    <img src="https://img.shields.io/badge/배포 링크-8867DF?style=for-the-badge">
  </a>
</div>

---

<h3 align="center">✨👩🏻‍💻 Tech Stack 👩🏻‍💻✨</h3>
<div align=center> 
  <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black"> 
  <img src="https://img.shields.io/badge/tailwindcss-1daabb.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/aws-F7A80D?style=for-the-badge&logo=amazon-aws&logoColor=white">
  <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/postgresql-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
</div>


<h3 align="center">✨📋 Collaboration & Management Tools 📋✨</h3>
<div align=center> 
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white"> 
  <img src="https://img.shields.io/badge/discord-5865F2?style=for-the-badge&logo=discord&logoColor=white">
  <img src="https://img.shields.io/badge/notion-000000?style=for-the-badge&logo=notion&logoColor=white">
  <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white">
  <img src="https://img.shields.io/badge/figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white">
  
</div>

---

## Team PoodingDev

<div align="center">
  <h3>Frontend</h3>
  <table>
    <tr>
      <th>신채영(총괄팀장)</th>
      <th>윤수진</th>
      <th>김호선</th>
    </tr>
    <tr>
      <td align="center">
        <a href="https://github.com/cxaos"><img src="https://github.com/cxaosdev.png" height=150 width=150><br/>@cxaosdev</a>
      </td>
      <td align="center">
        <a href="https://github.com/sujinnn"><img src="https://github.com/sujinnn.png" height=150 width=150><br/>@sujinnn</a>
      </td>
      <td align="center">
        <a href="https://github.com/kim-ho-seon"><img src="https://github.com/kim-ho-seon.png" height=150 width=150><br/>@kim-ho-seon</a>
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <h3>Backend</h3>
  <table>
    <tr>
      <th>정승원(BE팀장)</th>
      <th>김진강</th>
      <th>권은혜</th>
    </tr>
    <tr>
      <td align="center">
        <a href="https://github.com/seungwon0113"><img src="https://github.com/seungwon0113.png" height=150 width=150><br/>@seungwon0113</a>
      </td>
      <td align="center">
        <a href="https://github.com/jingangkim"><img src="https://github.com/jingangkim.png" height=150 width=150><br/>@jingangkim</a>
      </td>
      <td align="center">
        <a href="https://github.com/grace287"><img src="https://github.com/grace287.png" height=150 width=150><br/>@grace287</a>
      </td>
    </tr>
  </table>
</div>


## 📌 프로젝트 구조  
```
Evento_BE(Django_project) 
 ┣ .github/workflows,ISUUE_TEMPLATE 
 ┣ config
 ┣ user             //사용자 로그인
 ┣ claendars        //캘린더, 캘린더관리자, 구독
 ┣ comment          //이벤트 댓글
 ┣ comment_like     //댓글 좋아요 (X)
 ┣ event            //이벤트
 ┗ faviorite_event   //이벤트 즐겨찾기

DATABASE : Postgresql
```

---

## 📌 개발 기간 및 작업 관리  

### 개발 기간  
전체 개발 기간 : 2024-11-14 ~ 2024-12-10

UI 구현 및 수정 : 2024-11-19 ~ 2024-11-27

기능 구현 : 2024-11-25 ~ 2024-12-5

API 연결 및 검토 : 2024-11-14 ~ 2024-12-11

### 작업 관리  
- Jira를 활용하여 Sprint 기반 작업 관리  
- Notion으로 프로젝트 문서화 및 일정 관리  

---

## 📌 주요 기능  

### 1. 캘린더 생성  
- 사용자는 여러 개의 캘린더를 생성할 수 있습니다.  
- 생성된 캘린더는 **공개** 또는 **비공개**로 설정 가능하며, 필요에 따라 전환할 수 있습니다.  
- 공개 캘린더는 **생성자의 닉네임**으로 검색할 수 있습니다. (닉네임은 중복될 수 없습니다.) 

### 2. 캘린더 구독  
- 사용자는 여러 개의 공개 캘린더를 구독할 수 있습니다.  
- 구독한 캘린더는 메인 화면 캘린더 UI에서 확인할 수 있습니다.  
- **왼쪽 사이드바**에서 구독한 캘린더 목록을 확인하고, 체크박스를 통해 원하는 캘린더를 선택하여 화면에 표시할 수 있습니다.  

### 3. 관리 권한  
- 다른 사용자가 생성한 캘린더에 관리 멤버로 초대받을 수 있습니다.  
- 초대받은 캘린더는 **읽기 및 쓰기 권한**이 부여됩니다.  
- 관리 권한이 있는 캘린더의 색상을 변경하여 메인 화면에서 캘린더를 시각적으로 구분할 수 있습니다.  

### 4. 일정 관리 및 상호작용  
- 관리 권한이 있는 캘린더의 일정마다 **코멘트**를 남길 수 있습니다.  
- **D-day 설정**: 중요한 일정은 북마크 기능으로 지정하여 사이드바에서 빠르게 확인할 수 있습니다.  
- 메인 화면의 **오른쪽 하단 버튼**들을 통해 새 일정을 생성하고, 속한 캘린더와 공개/비공개 상태를 설정할 수 있습니다.  

### 5. 검색  
- **닉네임**으로 유저를 검색할 수 있습니다.  
- 검색된 결과에서:  
  - 구독 중인 캘린더는 **구독 취소 버튼**이 표시됩니다.  
  - 미구독 캘린더는 **구독 버튼**이 표시됩니다.  
- **구독 버튼** 클릭 시:  
  - 오른쪽 섹션의 **구독한 캘린더**에 캘린더가 추가됩니다.  
  - **왼쪽 사이드바의 구독한 캘린더 목록**에서도 확인할 수 있습니다.  

### 6. 내 프로필  
- 내 프로필 페이지에서 사용자의 기본 정보를 확인할 수 있습니다: 닉네임, 이름, 아이디, 생일  
- **프로필 이미지 옆 펜슬 아이콘** 클릭 시 **프로필 수정 페이지**로 이동합니다.  
- **프로필 수정 페이지**에서는 다음 정보 수정이 가능합니다: 닉네임, 생일  

### 7. 사용자 친화적 UI  
- **사이드바 구성**:  
  - **내 캘린더**:  
    - 자신이 관리자로 있는 캘린더 목록이 표시됩니다.  
    - 각 캘린더 목록 옆 체크박스를 통해 메인 화면에 표시 여부를 설정할 수 있습니다.  
    - 오른쪽 버튼으로 초대 코드를 발송하거나, 새 캘린더를 생성할 수 있습니다.  
  - **구독한 캘린더**:  
    - 자신이 구독한 캘린더 목록이 표시됩니다.  
    - 각 캘린더 목록 옆 체크박스로 메인 화면에 표시 여부를 설정할 수 있습니다.  
    - 오른쪽 연필 아이콘 클릭 시 캘린더 검색 페이지로 이동할 수 있습니다.  
- 캘린더는 색상으로 구분되어 시각적 인식이 용이합니다.  

### 8. 회원가입 및 로그인  
- **SNS 계정**으로만 회원가입이 가능합니다.  
- 모든 서비스는 **로그인 후** 이용할 수 있습니다.  

### 9. 일반 사용자 지원  
- 아티스트 일정뿐만 아니라 일반 사용자(팬 포함)도 개인 캘린더 및 그룹 캘린더를 생성하고 공유할 수 있습니다.  

---

필요한 추가사항이나 수정 요청이 있다면 언제든 말씀해주세요! 😊
