# ItemWriter





## JdbcBatchItemWriter

- bulk 방식으로 insert, update, delete 방식으로 처리한다.

![image-20240809205633974](./Writer.assets/image-20240809205633974.png)

![image-20240809205952269](./Writer.assets/image-20240809205952269.png)



## JpaItemWrieter

- ItemReader나 ItemProcessor로 부터 아이템을 전달 받을 떄는 Entity class 타입으로 받아야한다.

![image-20240809211925921](./Writer.assets/image-20240809211925921.png)

![image-20240809211936232](./Writer.assets/image-20240809211936232.png)



## ItemWriterAdapter

- 한번에 일괄처리를하는것이 아닌 한건씩 처리하게 된다.



## CompositeItemWriter

 job하나 step 하나 read 같고 write를 다르게
   write1 : 짝수, write2 : 홀수
  - 결과 : Chunk 사이즈로 write가 하나씩 실행되며 차례대로 실행된다. 즉 multi thread는 아니며 Read를 가져온 것으로 차례로 실행되는 것
1. Chunk 사이즈 만큼 가져온다.
2. 그걸로 Write 계산을 진행한다.

- Delegate 시키는 것

```java
@Bean
@StepScope
public CompositeItemWriter<Agv> compositeItemWriter(){
    List<ItemWriter<? super Agv>> writers = Stream.of(
        customItemWriter(),
        customItemWriter2()
    ).collect(Collectors.toList());

    return new CompositeItemWriterBuilder<Agv>()
        .delegates(writers)
        .build();
}

// 홀수
@Bean
@StepScope
public CustomItemWriter<Agv> customItemWriter(){

    String sql = "insert into agvsum (sum) values (:sum)";

    CustomItemWriter<Agv> agvCustomItemWriter = new CustomItemWriter<>(true);
    agvCustomItemWriter.setDataSource(agvParameter.getDataSource());
    agvCustomItemWriter.setSql(sql);
    agvCustomItemWriter.setItemSqlParameterSourceProvider(new BeanPropertyItemSqlParameterSourceProvider<>());

    agvCustomItemWriter.afterPropertiesSet();

    return agvCustomItemWriter;
}

// 짝수
@Bean
@StepScope
public CustomItemWriter<Agv> customItemWriter2(){

    String sql = "insert into agvsum (sum) values (:sum)";

    CustomItemWriter<Agv> agvCustomItemWriter = new CustomItemWriter<>(false);
    agvCustomItemWriter.setDataSource(agvParameter.getDataSource());
    agvCustomItemWriter.setSql(sql);
    agvCustomItemWriter.setItemSqlParameterSourceProvider(new BeanPropertyItemSqlParameterSourceProvider<>());

    agvCustomItemWriter.afterPropertiesSet();

    return agvCustomItemWriter;
}






```













