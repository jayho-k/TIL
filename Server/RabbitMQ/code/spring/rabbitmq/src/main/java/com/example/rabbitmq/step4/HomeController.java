package com.example.rabbitmq.step4;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller("step4HomeController")
@RequestMapping("/step4")
public class HomeController {

    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("message", "Welcome to RabbitMQ Sample!");
        return "home"; // src/main/resources/templates/home.html 파일을 찾음
    }

    @GetMapping("/news")
    public String news(Model model) {
        model.addAttribute("message", "Welcome to RabbitMQ News Sample!");
        return "news";
    }
}