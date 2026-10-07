# 기술 요구 사항

## 1. 아키텍처
```text
Vue.js SPA
    |
    | HTTP / JSON
    v
Django REST Framework
    |
    | Django ORM
    v
PostgreSQL
```

## 2. 프론트엔드
- Vue.js 3 사용
- Vite로 프로젝트 구성
- Bootstrap 5.0 적용
- HTML5, CSS3 사용
- SPA 구조로 구현

## 3. 백엔드
- Python 3 사용
- Django 사용
- Django REST Framework 사용
- REST/JSON API 제공
- Django ORM으로 DB 처리

## 4. 데이터베이스
- PostgreSQL 사용
- 기본적으로 관계형 데이터 중심으로 설계

## 5. 데이터 모델
### User 모델
- Django의 AbstractUser를 상속해 확장한다.
- 기본 필수 항목 포함
- 역할 구분 필드가 필요하다.

### 권장 필드
- username: 사번 사용
- password: 비밀번호
- name: 성명
- role: 관리자/매니저/직원
- team: 팀 연결

### Team 모델
- name
- manager

### EvaluationItem 모델
- name
- weight
- description

### EvaluationResponse 모델
- employee
- manager
- team
- submitted_at
- is_submitted
- status
- score values

## 6. API 구조
다음 형태로 구현을 단순화한다.
- 로그인 API
- 사용자 API
- 팀 API
- 평가 항목 API
- 평가 제출 API
- 점수 계산 API
- 결과 CSV 다운로드 API

## 7. 구현 제약
- 복잡한 인증 시스템을 추가하지 않는다.
- 실시간 기능을 추가하지 않는다.
- 비동기/웹소켓 기능을 사용하지 않는다.
- 단일 프로젝트 구조를 유지한다.
