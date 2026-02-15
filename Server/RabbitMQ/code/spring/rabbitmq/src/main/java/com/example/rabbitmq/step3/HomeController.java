package com.example.rabbitmq.step3;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller("step3HomeController")
@RequestMapping("/step3")
public class HomeController {

    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("message", "Welcome to RabbitMQ Sample!");
        return "home"; // src/main/resources/templates/home.html 파일을 찾음
    }
}