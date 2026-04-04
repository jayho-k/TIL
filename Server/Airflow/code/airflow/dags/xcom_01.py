
def push_vlaue():
    value = "Hello"
    return value # return 만 하게 되도 task_id로 xCom push 수행. keu는 return_value

# ti 객체는 ariflow가 해당 함수 수행 시에 자동으로 입력하여 수행한다.
def pull_value(ti):
    pulled = ti.xcom_pull(task_ids='task_push') # task_ids로 xcom에서 값을 가져오는 것
    print(pulled)
 

with DAG(
    dag_id="xcom_01",
    start_date=datetime(2026,1,1),
    schedule=None,
    catchup=False
) as dag:
    run_task_01 = PythonOperator(
        task_id="task_push",
        python_callable=push_value
    )

    run_task_02 = PythonOperator(
        task_id="task_pull",
        python_callable=pull_value
    )

    run_task_01 >> run_task_02