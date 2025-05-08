package reflection;

import reflection.data.BasicData;

import java.lang.reflect.Field;

public class FieldV1 {

    public static void main(String[] args) {
        Class<BasicData> helloClass = BasicData.class;

        System.out.println("====== fields() ======");
        Field[] fields = helloClass.getFields();
        for (Field field : fields) {
            System.out.println("field = " + field);
        }

        System.out.println("====== declaredFields() ======");
        Field[] declaredFields = helloClass.getDeclaredFields();
        for (Field field : declaredFields) {
            System.out.println("declaredField = " + field);
        }
    }
}
