# 03_injection

> 주입 방법
>
> - 필드 주입
>
> - 생성자 주입(Constructor Injection)
> - 세터 주입 (Setter Injection)
>
> 순환 참조방지



Field Injection

```
@Service
public class StudentServiceImpl implements StudentService {

    @Autowired
    private CourseService courseService;

    @Override
    public void studentMethod() {
        courseService.courseMethod();
    }

}
```



Setter Injection

```
@Service
public class StudentServiceImpl implements StudentService {

    private CourseService courseService;

    @Autowired
    public void setCourseService(CourseService courseService) {
        this.courseService = courseService;
    }

    @Override
    public void studentMethod() {
        courseService.courseMethod();
    }
}
```















