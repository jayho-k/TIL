package com.example.rabbitmq.step5;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/logs")
@RequiredArgsConstructor
public class LogController {
    private final CustomExceptionHandler exceptionHandler;

    @GetMapping("/error")
    public ResponseEntity<String> errorAPI() {
        try {
            String value = null;
            value.getBytes(); // null pointer
        } catch (Exception e) {
            exceptionHandler.handleException(e);
        }
        return ResponseEntity.ok("Controller Nullpointer Exception 처리 ");
    }

    @GetMapping("/warn")
    public ResponseEntity<String> warnAPI() {
        try {
            throw new IllegalArgumentException("invalid");
        } catch (Exception e) {
            exceptionHandler.handleException(e);
        }
        return null;
    }

    @PostMapping("/info")
    public ResponseEntity<String> infoAPI(@RequestBody String message) {
        exceptionHandler.handleMessage(message);
        return ResponseEntity.ok("Controller Info log 발송 처리 ");
    }

}