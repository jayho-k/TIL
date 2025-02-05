package thread.collection.java;

import java.util.ArrayList;
import java.util.List;

import static java.util.Collections.*;

public class SynchronizedListMain {

    public static void main(String[] args) {
        // 동시성
        List<Object> list = synchronizedList(new ArrayList<>());
        list.add("data1");

    }

}
