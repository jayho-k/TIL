

# postgres : xcom value를 jsonb로 저장하게 된다.
def push_dict():
    value = "Hello"
    return {
        'username' : 'airflow_user',
        'run_status' : 'success',
        'score' : 99
    }

def pull_value(ti):
    pulled = ti.xcom_pull(task_ids='task_push') # task_ids로 xcom에서 값을 가져오는 것
    print(pulled)

with DAG(
    dag_id="xcom_multi_keys",
    start_date=datetime(2026,1,1),
    schedule=None,
    catchup=False
) as dag:
    run_task_01 = PythonOperator(
        task_id="task_push",
        python_callable=push_dict
    )

    run_task_02 = PythonOperator(
        task_id="task_pull",
        python_callable=pull_value
    )

    run_task_01 >> run_task_02