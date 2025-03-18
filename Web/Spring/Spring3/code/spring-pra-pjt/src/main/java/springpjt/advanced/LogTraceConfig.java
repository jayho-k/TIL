package springpjt.advanced;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springpjt.advanced.trace.logtrace.FieldLogTrace;
import springpjt.advanced.trace.logtrace.LogTrace;

@Configuration
public class LogTraceConfig {

    @Bean
    public LogTrace logTrace() {
        return new FieldLogTrace();
    }

}
