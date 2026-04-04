from airflow.sdk import DAG, chain
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator # PythonOperator를 잘사용하진 않는다.
from pendulum import datetime # pendulum : 타임존 관련해서 정확하며, pendulum를 사용하는 것을 권장



def print_hello():
    print("hello world")

with DAG(
    dag_id="first_dag", # dag_id : airflow 내에서 반드시 고유한 값을 가져야한다.
    start_date=datetime(2026, 1, 1, tz="Asia/Seoul") # default : utc >> tz 설정은 필수
    schedule="@daily", # 수행 주기
    catchup=False, # 수행되지 않은 과거 Dag run 스케줄 수행 여부
    tags=["fundamental", "tutorial"]
) as dag:
    
    # task_id는 DAG 내에서 고유해야 함
    bash_task = BashOperator(
        task_id="print_date_bash",
        bash_command='echo "#### today: `date`""' # echo는 쌍 따움표가 들어간다. ` 이건 shell에서 커멘드로 사용된다.
    )

    python_task = PythonOperator(
        task_id = "say_hello_python",
        python_callable=print_hello
    )

    bash_task >> python_task
