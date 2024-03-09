# CTAS

> - Update/Delete 할때 마다 기존데이터를 Undo Segment와 Redo Log에 Writing해야한다
>   - 많은 시간이 소요된다.

## Update

```sql
update Test1
set big_ename = 'AA'
where deptno > 5; -- 1분 6초

-- CTAS 사용법
-- 1. Table생성
create table Test1_tmp
as
select empno, slary, deptno,
	case when(deptno > 5) then 'AA'
	else big_ename end
    	as big_ename,
	big_addr
from Test1 -- 4초

-- 2. create index
-- 시간이 오래걸릴까?

-- 3. rename
rename Test1_tmp to Test1
```





























