package com.rps.bench;

import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PingController {

    private final JdbcTemplate jdbcTemplate;

    public PingController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping("/api/ping")
    public Map<String, String> ping() {
        jdbcTemplate.queryForObject("SELECT 1", Integer.class);
        return Map.of("status", "ok");
    }
}
